"""
Forensic Platform - Rule-Based Detection Engine & IOC Matcher
Problem ID: SIH26148 | NTRO Cyber Forensics Prototype
"""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from ..database import get_db_connection
from ..audit.audit_service import AuditService
from ..evidence.chain_of_custody import ChainOfCustodyService

class AnalysisEngine:
    @staticmethod
    def analyze_case(case_id: str, actor_name: str = "Lead DFIR Analyst") -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Clear existing findings for clean re-run
        cursor.execute("DELETE FROM findings WHERE case_id = ?;", (case_id,))

        findings: List[Dict[str, Any]] = []
        now = datetime.now(timezone.utc).isoformat()

        # Fetch all case data
        cursor.execute("SELECT * FROM processes WHERE case_id = ?;", (case_id,))
        processes = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM files WHERE case_id = ?;", (case_id,))
        files = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM network_connections WHERE case_id = ?;", (case_id,))
        connections = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM logs WHERE case_id = ?;", (case_id,))
        logs = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM iocs;")
        iocs = [dict(r) for r in cursor.fetchall()]

        # Index IOCs for swift O(1) matching
        ioc_hashes = {i["value"].lower(): i for i in iocs if i["type"] == "HASH"}
        ioc_ips = {i["value"]: i for i in iocs if i["type"] == "IP"}
        ioc_domains = {i["value"].lower(): i for i in iocs if i["type"] == "DOMAIN"}
        ioc_filenames = {i["value"].lower(): i for i in iocs if i["type"] == "FILENAME"}

        # RULE 1: IOC Hash Match
        for f in files:
            file_hash = (f.get("sha256") or "").lower()
            if file_hash in ioc_hashes:
                matched_ioc = ioc_hashes[file_hash]
                findings.append({
                    "title": f"IOC Hash Match: {matched_ioc['description']}",
                    "severity": matched_ioc.get("severity", "CRITICAL"),
                    "category": "IOC",
                    "description": f"File '{f['filename']}' ({f['path']}) matches known threat indicator hash {file_hash[:16]}... Source: {matched_ioc.get('source', 'Threat Intel')}",
                    "evidence_ref": f["path"],
                    "rule_id": "RULE-IOC-001",
                    "rule_name": "Known Threat Indicator Hash Match"
                })

        # RULE 2: Suspicious File Location (Executable in Temp/AppData)
        for f in files:
            path_lower = f["path"].lower()
            ext = f.get("extension", "").lower()
            if ext in ('.exe', '.dll', '.bat', '.ps1', '.vbs', '.scr'):
                if "temp" in path_lower or "appdata" in path_lower or "downloads" in path_lower:
                    findings.append({
                        "title": f"Executable in Monitored User Directory: {f['filename']}",
                        "severity": "HIGH",
                        "category": "FILE",
                        "description": f"Executable binary or script discovered residing in high-risk directory '{f['path']}'. Common persistence/stager mechanism.",
                        "evidence_ref": f["path"],
                        "rule_id": "RULE-FILE-002",
                        "rule_name": "Unusual Executable Location Detection"
                    })

        # RULE 3: Process Execution from User/Temp Directory
        for p in processes:
            exe_lower = (p.get("exe_path") or "").lower()
            if "temp" in exe_lower or "appdata" in exe_lower:
                findings.append({
                    "title": f"Suspicious Process Execution: {p['name']} (PID:{p['pid']})",
                    "severity": "HIGH",
                    "category": "PROCESS",
                    "description": f"Process '{p['name']}' running from temporary path '{p['exe_path']}'. Command line: {p['cmdline'][:100]}",
                    "evidence_ref": f"PID-{p['pid']}",
                    "rule_id": "RULE-PROC-001",
                    "rule_name": "Suspicious Executable Execution Path"
                })

        # RULE 4: Hidden or Encoded PowerShell Execution
        for p in processes:
            cmd_lower = (p.get("cmdline") or "").lower()
            if "powershell" in cmd_lower and ("-w hidden" in cmd_lower or "-exec bypass" in cmd_lower or "-enc" in cmd_lower or "invoke-webrequest" in cmd_lower):
                findings.append({
                    "title": f"Obfuscated PowerShell Invocation Detected (PID:{p['pid']})",
                    "severity": "HIGH",
                    "category": "PROCESS",
                    "description": f"PowerShell process invoked with evasion/download flags: {p['cmdline'][:120]}...",
                    "evidence_ref": f"PID-{p['pid']}",
                    "rule_id": "RULE-PROC-002",
                    "rule_name": "PowerShell Script Evasion & Staging Detection"
                })

        # RULE 5: IOC IP / Suspicious Outbound Connection
        for c in connections:
            remote_ip = c.get("remote_address") or ""
            remote_port = c.get("remote_port") or 0
            if remote_ip in ioc_ips:
                matched_ioc = ioc_ips[remote_ip]
                findings.append({
                    "title": f"IOC Outbound Network C2 Match: {remote_ip}:{remote_port}",
                    "severity": "CRITICAL",
                    "category": "NETWORK",
                    "description": f"Active socket initiated by {c['process_name']} (PID:{c['pid']}) connects to known Threat Intel IP {remote_ip} ({matched_ioc['description']}).",
                    "evidence_ref": f"{c['local_address']}:{c['local_port']} -> {remote_ip}:{remote_port}",
                    "rule_id": "RULE-NET-001",
                    "rule_name": "Threat Intel C2 Network Communication"
                })
            elif remote_port in (4444, 1337, 5555, 8888, 9001):
                findings.append({
                    "title": f"Anomalous Outbound Port Connection: {remote_ip}:{remote_port}",
                    "severity": "HIGH",
                    "category": "NETWORK",
                    "description": f"Outbound socket to unconventional port {remote_port} by process {c['process_name']}.",
                    "evidence_ref": f"{c['local_address']}:{c['local_port']} -> {remote_ip}:{remote_port}",
                    "rule_id": "RULE-NET-002",
                    "rule_name": "Anomalous High-Risk Port Connection"
                })

        # RULE 6: Multiple Failed Authentication Logons
        failed_logins = [l for l in logs if "4625" in l.get("event_type", "") or "Failed" in l.get("event_type", "")]
        if len(failed_logins) >= 1:
            findings.append({
                "title": f"Authentication Failure Anomaly ({len(failed_logins)} event(s) recorded)",
                "severity": "MEDIUM",
                "category": "LOG",
                "description": f"Detected authentication failure events. Detailed probe against workstation credentials.",
                "evidence_ref": "Security Log Event 4625",
                "rule_id": "RULE-LOG-001",
                "rule_name": "Suspicious Authentication Failure Detection"
            })

        # Insert findings into DB
        finding_records = []
        for f in findings:
            fid = f"fnd-{uuid.uuid4().hex[:12]}"
            finding_records.append((
                fid, case_id, f["title"], f["severity"],
                f["category"], f["description"], f["evidence_ref"],
                f["rule_id"], f["rule_name"], now
            ))

        cursor.executemany("""
        INSERT INTO findings (id, case_id, title, severity, category, description, evidence_ref, rule_id, rule_name, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, finding_records)

        conn.commit()
        conn.close()

        ChainOfCustodyService.record_entry(
            case_id=case_id,
            evidence_id=None,
            action="RULE_ANALYSIS_COMPLETED",
            actor_name=actor_name,
            actor_role="INVESTIGATOR",
            details=f"Deterministic rule engine evaluation completed: {len(findings)} suspicious findings generated."
        )

        AuditService.log_event(
            actor_name=actor_name,
            actor_role="INVESTIGATOR",
            action="ANALYZE_EVIDENCE",
            resource_type="CASE",
            resource_id=case_id,
            details=f"Analysis engine generated {len(findings)} findings."
        )

        return findings

    @staticmethod
    def get_findings(case_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM findings WHERE case_id = ? ORDER BY timestamp DESC;", (case_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
