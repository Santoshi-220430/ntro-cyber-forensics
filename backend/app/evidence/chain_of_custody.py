"""
Forensic Platform - Chain of Custody Tracker
Problem ID: SIH26148 | NTRO Cyber Forensics Prototype
"""

import uuid
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from ..database import get_db_connection

class ChainOfCustodyService:
    @staticmethod
    def record_entry(
        case_id: str,
        evidence_id: Optional[str],
        action: str,
        actor_name: str,
        actor_role: str,
        details: str
    ) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()

        entry_id = f"coc-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        # Chain linking: Fetch previous entry hash for this case
        cursor.execute("SELECT id, action, details, evidence_id, integrity_hash FROM chain_of_custody WHERE case_id = ? ORDER BY timestamp DESC LIMIT 1;", (case_id,))
        prev_row = cursor.fetchone()

        # Deduplication: If latest entry has identical action and details for this case/evidence, avoid duplicate spam
        if prev_row and prev_row["action"] == action and prev_row["details"] == details and (prev_row["evidence_id"] or "") == (evidence_id or ""):
            conn.close()
            return {
                "id": prev_row["id"],
                "case_id": case_id,
                "evidence_id": evidence_id,
                "action": action,
                "actor_name": actor_name,
                "actor_role": actor_role,
                "timestamp": now,
                "details": details,
                "integrity_hash": prev_row["integrity_hash"]
            }

        prev_hash = prev_row["integrity_hash"] if prev_row else "0" * 64

        # Cryptographically chain entries
        payload = f"{entry_id}|{prev_hash}|{case_id}|{evidence_id}|{action}|{actor_name}|{now}|{details}"
        chain_hash = hashlib.sha256(payload.encode()).hexdigest()

        cursor.execute("""
        INSERT INTO chain_of_custody (id, case_id, evidence_id, action, actor_name, actor_role, timestamp, details, integrity_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry_id, case_id, evidence_id, action,
            actor_name, actor_role, now, details, chain_hash
        ))

        conn.commit()
        conn.close()

        return {
            "id": entry_id,
            "case_id": case_id,
            "evidence_id": evidence_id,
            "action": action,
            "actor_name": actor_name,
            "actor_role": actor_role,
            "timestamp": now,
            "details": details,
            "integrity_hash": chain_hash
        }

    @staticmethod
    def get_entries(case_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chain_of_custody WHERE case_id = ? ORDER BY timestamp ASC;", (case_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
