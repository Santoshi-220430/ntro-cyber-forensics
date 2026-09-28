"""
Forensic Platform - Immutable Audit Logging Service
Problem ID: SIH26148 | NTRO Cyber Forensics Prototype
"""

import uuid
import hashlib
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from ..database import get_db_connection

class AuditService:
    @staticmethod
    def log_event(
        actor_name: str,
        actor_role: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        status: str = "SUCCESS",
        details: Optional[str] = None,
        ip_address: str = "127.0.0.1"
    ) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()

        event_id = f"aud-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        # Generate cryptographic digest to seal audit record integrity
        raw_payload = f"{event_id}|{now}|{actor_name}|{actor_role}|{action}|{resource_type}|{resource_id}|{status}"
        digest = hashlib.sha256(raw_payload.encode()).hexdigest()

        cursor.execute("""
        INSERT INTO audit_logs (id, timestamp, actor_name, actor_role, action, resource_type, resource_id, status, details, ip_address, digest)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id, now, actor_name, actor_role, action,
            resource_type, resource_id, status, details, ip_address, digest
        ))

        conn.commit()
        conn.close()

        return {
            "id": event_id,
            "timestamp": now,
            "actor_name": actor_name,
            "action": action,
            "status": status,
            "digest": digest
        }

    @staticmethod
    def get_audit_logs(limit: int = 100, case_id: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        if case_id:
            cursor.execute("SELECT * FROM audit_logs WHERE resource_id = ? ORDER BY timestamp DESC LIMIT ?;", (case_id, limit))
        else:
            cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?;", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
