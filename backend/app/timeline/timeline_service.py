"""
Forensic Platform - Normalized Timeline Engine
Problem ID: SIH26148 | NTRO Cyber Forensics Prototype
"""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from ..database import get_db_connection
from ..audit.audit_service import AuditService
from ..evidence.chain_of_custody import ChainOfCustodyService

class TimelineService:
    @staticmethod
    def build_timeline_for_case(case_id: str, actor_name: str = "Lead DFIR Analyst") -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Clear existing timeline events for this case to rebuild fresh
        cursor.execute("DELETE FROM timeline_events WHERE case_id = ?;", (case_id,))

        events: List[Dict[str, Any]] = []

        # 1. Ingest Log Events
        cursor.execute("SELECT * FROM logs WHERE case_id = ?;", (case_id,))
        logs = cursor.fetchall()
        for l in logs:
            events.append({
                "timestamp": l["timestamp"],
                "source": "LOGS",
                "event_type": l["event_type"],
                "entity": l["host"] or l["user"] or "SYSTEM",
                "details": l["message"],
                "severity": l["severity"],
                "evidence_id": None
            })

        # 2. Ingest Process Events
        cursor.execute("SELECT * FROM processes WHERE case_id = ?;", (case_id,))
        procs = cursor.fetchall()
        for p in procs:
            if p["start_time"]:
                events.append({
                    "timestamp": p["start_time"],
                    "source": "PROCESS",
                    "event_type": "PROCESS_START",
                    "entity": f"{p['name']} (PID:{p['pid']})",
                    "details": f"Executed: {p['cmdline']} | User: {p['username']}",
                    "severity": "HIGH" if p["is_suspicious"] else "INFO",
                    "evidence_id": None
                })

        # 3. Ingest File Events
        cursor.execute("SELECT * FROM files WHERE case_id = ?;", (case_id,))
        files = cursor.fetchall()
        for f in files:
            if f["created_time"]:
                events.append({
                    "timestamp": f["created_time"],
                    "source": "FILE_SYSTEM",
                    "event_type": "FILE_CREATED",
                    "entity": f["filename"],
                    "details": f"File path: {f['path']} (Size: {f['size_bytes']} bytes, SHA256: {f['sha256'][:16]}...)",
                    "severity": "HIGH" if f["is_suspicious"] else "INFO",
                    "evidence_id": None
                })
            if f["modified_time"] and f["modified_time"] != f["created_time"]:
                events.append({
                    "timestamp": f["modified_time"],
                    "source": "FILE_SYSTEM",
                    "event_type": "FILE_MODIFIED",
                    "entity": f["filename"],
                    "details": f"File modified at: {f['path']}",
                    "severity": "MEDIUM" if f["is_suspicious"] else "LOW",
                    "evidence_id": None
                })

        # 4. Ingest Network Connection Events
        cursor.execute("SELECT * FROM network_connections WHERE case_id = ?;", (case_id,))
        conns = cursor.fetchall()
        now = datetime.now(timezone.utc).isoformat()
        for c in conns:
            events.append({
                "timestamp": now, # connection snapshot time
                "source": "NETWORK",
                "event_type": f"{c['protocol']}_{c['state']}",
                "entity": f"{c['local_address']}:{c['local_port']} -> {c['remote_address']}:{c['remote_port']}",
                "details": f"Active Socket by {c['process_name']} (PID:{c['pid']}). {c['suspicious_reason']}",
                "severity": "CRITICAL" if c["is_suspicious"] else "INFO",
                "evidence_id": None
            })

        # Sort all timeline events chronologically
        events.sort(key=lambda x: x["timestamp"])

        # Insert into timeline_events table
        records = []
        for e in events:
            eid = f"tle-{uuid.uuid4().hex[:12]}"
            records.append((
                eid, case_id, e["timestamp"], e["source"],
                e["event_type"], e["entity"], e["details"],
                e["severity"], e["evidence_id"]
            ))

        cursor.executemany("""
        INSERT INTO timeline_events (id, case_id, timestamp, source, event_type, entity, details, severity, evidence_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, records)

        conn.commit()
        conn.close()

        ChainOfCustodyService.record_entry(
            case_id=case_id,
            evidence_id=None,
            action="TIMELINE_CORRELATED",
            actor_name=actor_name,
            actor_role="INVESTIGATOR",
            details=f"Reconstructed and correlated unified chronological timeline comprising {len(events)} events across files, processes, logs, and network telemetry."
        )

        AuditService.log_event(
            actor_name=actor_name,
            actor_role="INVESTIGATOR",
            action="BUILD_TIMELINE",
            resource_type="CASE",
            resource_id=case_id,
            details=f"Successfully built timeline with {len(events)} events."
        )

        return events

    @staticmethod
    def get_timeline(case_id: str, severity: Optional[str] = None, source: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM timeline_events WHERE case_id = ?"
        params: List[Any] = [case_id]

        if severity:
            query += " AND severity = ?"
            params.append(severity.upper())
        if source:
            query += " AND source = ?"
            params.append(source.upper())

        query += " ORDER BY timestamp ASC;"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
