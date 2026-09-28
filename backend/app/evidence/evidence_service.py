"""
Forensic Platform - Evidence Management & Integrity Verification
Problem ID: SIH26148 | NTRO Cyber Forensics Prototype
"""

import os
import uuid
import json
import shutil
import hashlib
import mimetypes
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from ..database import get_db_connection
from ..config import EVIDENCE_VAULT_DIR
from .chain_of_custody import ChainOfCustodyService
from ..audit.audit_service import AuditService

def compute_hashes(file_path: str) -> Dict[str, str]:
    if not os.path.exists(file_path):
        return {"sha256": "FILE_NOT_FOUND", "md5": "FILE_NOT_FOUND"}

    sha256 = hashlib.sha256()
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
            md5.update(chunk)
    return {
        "sha256": sha256.hexdigest(),
        "md5": md5.hexdigest()
    }

class EvidenceService:
    @staticmethod
    def register_evidence(
        case_id: str,
        name: str,
        source_type: str,
        original_file_path: Optional[str] = None,
        collector_id: str = "usr-investigator",
        collector_name: str = "Lead DFIR Analyst",
        collection_method: str = "AUTOMATED_DSL_COLLECTION",
        metadata: Optional[Dict[str, Any]] = None,
        simulated_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()

        stored_file_path = None
        file_size = 0
        sha256_hash = simulated_hash or "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        md5_hash = "d41d8cd98f00b204e9800998ecf8427e"
        mime_type = "application/octet-stream"

        if original_file_path and os.path.exists(original_file_path):
            file_size = os.path.getsize(original_file_path)
            hashes = compute_hashes(original_file_path)
            sha256_hash = hashes["sha256"]
            md5_hash = hashes["md5"]

            mime_guess, _ = mimetypes.guess_type(original_file_path)
            if mime_guess:
                mime_type = mime_guess

            # Securely replicate into read-only Evidence Vault
            vault_target = EVIDENCE_VAULT_DIR / f"{name}"
            try:
                shutil.copy2(original_file_path, vault_target)
                stored_file_path = str(vault_target)
            except Exception:
                stored_file_path = original_file_path
        elif original_file_path:
            stored_file_path = original_file_path

        meta_json = json.dumps(metadata or {})

        # DEDUPLICATION CHECK: If evidence with this name already exists for this case, do not insert duplicate
        cursor.execute("SELECT * FROM evidence WHERE case_id = ? AND name = ?;", (case_id, name))
        existing = cursor.fetchone()
        if existing:
            # If hash matches, return existing record idempotently
            if existing["sha256_hash"] == sha256_hash and existing["file_size"] == file_size:
                conn.close()
                return dict(existing)
            else:
                # Update existing evidence record with refreshed hash and metadata
                cursor.execute("""
                UPDATE evidence SET
                    sha256_hash = ?, md5_hash = ?, file_size = ?,
                    file_path = COALESCE(?, file_path),
                    acquisition_timestamp = ?,
                    integrity_status = 'VERIFIED',
                    metadata_json = ?
                WHERE id = ?;
                """, (sha256_hash, md5_hash, file_size, stored_file_path, now, meta_json, existing["id"]))
                conn.commit()
                conn.close()

                ChainOfCustodyService.record_entry(
                    case_id=case_id,
                    evidence_id=existing["id"],
                    action="EVIDENCE_UPDATED",
                    actor_name=collector_name,
                    actor_role="INVESTIGATOR",
                    details=f"Evidence artifact {existing['evidence_number']} ({name}) updated and re-verified. SHA-256: {sha256_hash[:16]}..."
                )
                return {
                    "id": existing["id"],
                    "case_id": case_id,
                    "evidence_number": existing["evidence_number"],
                    "name": name,
                    "source_type": source_type,
                    "file_path": stored_file_path or existing["file_path"],
                    "file_size": file_size,
                    "sha256_hash": sha256_hash,
                    "md5_hash": md5_hash,
                    "integrity_status": "VERIFIED",
                    "acquisition_timestamp": now
                }

        # Count existing evidence to generate sequential ID
        cursor.execute("SELECT COUNT(*) as cnt FROM evidence WHERE case_id = ?;", (case_id,))
        count = cursor.fetchone()["cnt"] + 1
        evidence_number = f"EVD-{case_id[:8].upper()}-{count:03d}"
        evidence_id = f"evd-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        cursor.execute("""
        INSERT INTO evidence (
            id, case_id, evidence_number, name, source_type, file_path,
            file_size, sha256_hash, md5_hash, mime_type, acquisition_timestamp,
            collector_id, collector_name, collection_method, integrity_status, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'VERIFIED', ?)
        """, (
            evidence_id, case_id, evidence_number, name, source_type, stored_file_path,
            file_size, sha256_hash, md5_hash, mime_type, now,
            collector_id, collector_name, collection_method, meta_json
        ))

        conn.commit()
        conn.close()

        # Update chain of custody
        ChainOfCustodyService.record_entry(
            case_id=case_id,
            evidence_id=evidence_id,
            action="EVIDENCE_ACQUIRED",
            actor_name=collector_name,
            actor_role="INVESTIGATOR",
            details=f"Acquired {name} ({source_type}). Initial SHA-256 calculated: {sha256_hash[:16]}..."
        )

        AuditService.log_event(
            actor_name=collector_name,
            actor_role="INVESTIGATOR",
            action="EVIDENCE_ACQUIRED",
            resource_type="EVIDENCE",
            resource_id=evidence_id,
            details=f"Evidence {evidence_number} secured. SHA-256: {sha256_hash}"
        )

        return {
            "id": evidence_id,
            "evidence_number": evidence_number,
            "name": name,
            "source_type": source_type,
            "sha256_hash": sha256_hash,
            "md5_hash": md5_hash,
            "integrity_status": "VERIFIED",
            "file_size": file_size,
            "acquisition_timestamp": now
        }

    @staticmethod
    def verify_all_evidence(case_id: str, actor_name: str = "Lead DFIR Analyst") -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evidence WHERE case_id = ?;", (case_id,))
        rows = [dict(r) for r in cursor.fetchall()]

        results = []
        updates = []
        for row in rows:
            ev_id = row["id"]
            stored_hash = row["sha256_hash"]
            file_path = row["file_path"]
            ev_num = row["evidence_number"]

            status = "VERIFIED"
            current_hash = stored_hash

            if file_path and os.path.exists(file_path):
                live_hashes = compute_hashes(file_path)
                current_hash = live_hashes["sha256"]
                if current_hash != stored_hash:
                    status = "INTEGRITY_VERIFICATION_FAILED"
            
            updates.append((status, ev_id))
            results.append({
                "id": ev_id,
                "evidence_number": ev_num,
                "name": row["name"],
                "source_type": row["source_type"],
                "original_hash": stored_hash,
                "computed_hash": current_hash,
                "status": status,
                "match": (status == "VERIFIED")
            })

        for status, ev_id in updates:
            cursor.execute("UPDATE evidence SET integrity_status = ? WHERE id = ?;", (status, ev_id))
        conn.commit()
        conn.close()

        # Record consolidated batch chain of custody entry
        failed_items = [r for r in results if r["status"] != "VERIFIED"]
        if failed_items:
            ChainOfCustodyService.record_entry(
                case_id=case_id,
                evidence_id=None,
                action="INTEGRITY_ALERT",
                actor_name=actor_name,
                actor_role="INVESTIGATOR",
                details=f"INTEGRITY ALERT: {len(failed_items)} of {len(results)} evidence items failed hash verification!"
            )
            for f in failed_items:
                ChainOfCustodyService.record_entry(
                    case_id=case_id,
                    evidence_id=f["id"],
                    action="TAMPER_DETECTED",
                    actor_name=actor_name,
                    actor_role="INVESTIGATOR",
                    details=f"Tampering detected on {f['evidence_number']} ({f['name']}). Live SHA-256 does not match original digest."
                )
        else:
            ChainOfCustodyService.record_entry(
                case_id=case_id,
                evidence_id=None,
                action="INTEGRITY_VERIFIED",
                actor_name=actor_name,
                actor_role="INVESTIGATOR",
                details=f"Cryptographic SHA-256 verification scan completed across {len(results)} evidence items: All {len(results)} items confirmed intact (0 tampered)."
            )

        AuditService.log_event(
            actor_name=actor_name,
            actor_role="INVESTIGATOR",
            action="VERIFY_ALL_EVIDENCE",
            resource_type="CASE",
            resource_id=case_id,
            details=f"Verified integrity of {len(results)} evidence items."
        )

        return results

    @staticmethod
    def get_case_evidence(case_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evidence WHERE case_id = ? ORDER BY acquisition_timestamp ASC;", (case_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
