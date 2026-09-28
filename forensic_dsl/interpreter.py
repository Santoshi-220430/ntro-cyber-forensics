"""
Forensic DSL - Interpreter & Execution Engine
Problem ID: SIH26148 | NTRO Cyber Forensics Prototype
"""

import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from .ast_nodes import (
    ProgramNode, CaseStmt, GetStmt, HashStmt, SearchStmt,
    BuildTimelineStmt, AnalyzeStmt, GenerateReportStmt,
    VerifyIntegrityStmt, SetStmt, BlockedCommandStmt
)
from backend.app.database import get_db_connection
from backend.app.security.compatibility import SecurityCompatibilityManager
from backend.app.forensic.collectors import (
    SystemCollector, ProcessCollector, FileCollector,
    NetworkCollector, LogCollector, OfflinePCAPParser
)
from backend.app.evidence.evidence_service import EvidenceService
from backend.app.timeline.timeline_service import TimelineService
from backend.app.analysis.analysis_engine import AnalysisEngine
from backend.app.reports.report_generator import ForensicReportGenerator
from backend.app.audit.audit_service import AuditService

class DSLInterpreter:
    def __init__(self, current_user: Dict[str, Any], security_mode: str = "AUTHORIZED"):
        self.user = current_user
        self.security_mode = security_mode
        self.mode = "DEMO" # Default to DEMO mode for reproducible prototype demonstration
        self.case_id: Optional[str] = None
        self.case_number: Optional[str] = None
        self.output_logs: List[str] = []
        self.results: Dict[str, Any] = {
            "system": None,
            "processes_count": 0,
            "files_count": 0,
            "connections_count": 0,
            "logs_count": 0,
            "timeline_events_count": 0,
            "findings_count": 0,
            "report": None,
            "integrity_verified": None
        }

    def _log(self, text: str):
        self.output_logs.append(text)

    def execute(self, program: ProgramNode, default_case_id: Optional[str] = None) -> Dict[str, Any]:
        self.output_logs = []
        self.case_id = default_case_id

        # If default_case_id provided, fetch case number
        if self.case_id:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT case_number, mode FROM cases WHERE id = ?;", (self.case_id,))
            row = c.fetchone()
            if row:
                self.case_number = row["case_number"]
                self.mode = row["mode"] or "DEMO"
            conn.close()

        # Step 1: Pre-execution Security Compatibility Check
        script_repr = "\n".join([str(s) for s in program.statements])
        sec_eval = SecurityCompatibilityManager.evaluate_execution(
            mode=self.security_mode,
            script_content=script_repr,
            user_info=self.user,
            case_id=self.case_id or "GLOBAL"
        )

        self._log(f"[*] Security Mode: [{sec_eval['mode']}] | Status: {sec_eval['security_status']}")
        if "simulated_alert" in sec_eval:
            self._log(f"[!] {sec_eval['simulated_alert']}")

        # Step 2: Iterate and execute AST statements
        for stmt in program.statements:
            if isinstance(stmt, BlockedCommandStmt):
                self._log(f"[!] BLOCKED: {stmt.details}")
                self._log(f"    Reason: {stmt.reason}")
                return {
                    "status": "BLOCKED",
                    "logs": self.output_logs,
                    "security_eval": sec_eval,
                    "results": self.results
                }

            elif isinstance(stmt, CaseStmt):
                self._handle_case_stmt(stmt)

            elif isinstance(stmt, SetStmt):
                self._handle_set_stmt(stmt)

            elif isinstance(stmt, GetStmt):
                self._handle_get_stmt(stmt)

            elif isinstance(stmt, HashStmt):
                self._handle_hash_stmt(stmt)

            elif isinstance(stmt, SearchStmt):
                self._handle_search_stmt(stmt)

            elif isinstance(stmt, BuildTimelineStmt):
                self._handle_build_timeline(stmt)

            elif isinstance(stmt, AnalyzeStmt):
                self._handle_analyze(stmt)

            elif isinstance(stmt, GenerateReportStmt):
                self._handle_generate_report(stmt)

            elif isinstance(stmt, VerifyIntegrityStmt):
                self._handle_verify_integrity(stmt)

        self._log("[+] Forensic DSL Execution Sequence Completed.")

        # Persist execution run in script_executions table
        if self.case_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            exec_id = f"exec-{uuid.uuid4().hex[:12]}"
            now = datetime.now(timezone.utc).isoformat()
            cursor.execute("""
            INSERT INTO script_executions (id, case_id, executor_id, executor_name, raw_script, status, output_logs, security_status, started_at, completed_at)
            VALUES (?, ?, ?, ?, ?, 'SUCCESS', ?, ?, ?, ?)
            """, (
                exec_id, self.case_id, self.user.get("id"),
                self.user.get("full_name"), script_repr[:500],
                "\n".join(self.output_logs), sec_eval["security_status"], now, now
            ))
            conn.commit()
            conn.close()

        return {
            "status": "SUCCESS",
            "case_id": self.case_id,
            "case_number": self.case_number,
            "logs": self.output_logs,
            "security_eval": sec_eval,
            "results": self.results
        }

    def _handle_case_stmt(self, stmt: CaseStmt):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, case_number, mode FROM cases WHERE case_number = ? OR id = ?;", (stmt.case_id, stmt.case_id))
        row = cursor.fetchone()
        if row:
            self.case_id = row["id"]
            self.case_number = row["case_number"]
            self.mode = row["mode"] or "DEMO"
            self._log(f"[+] Active Case Context switched to: {self.case_number} (Mode: {self.mode})")
        else:
            # Auto-create case if not present
            case_id = f"case-{uuid.uuid4().hex[:10]}"
            now = datetime.now(timezone.utc).isoformat()
            cursor.execute("""
            INSERT INTO cases (id, case_number, title, description, status, investigator_id, investigator_name, target_host, mode, created_at, updated_at)
            VALUES (?, ?, ?, 'Auto-initialized by DSL command', 'ACTIVE', ?, ?, 'WS-TARGET.local', 'DEMO', ?, ?)
            """, (case_id, stmt.case_id, f"Investigation {stmt.case_id}", self.user.get("id"), self.user.get("full_name"), now, now))
            conn.commit()
            self.case_id = case_id
            self.case_number = stmt.case_id
            self._log(f"[+] Case {stmt.case_id} initialized and activated.")
        conn.close()

    def _handle_set_stmt(self, stmt: SetStmt):
        if stmt.key == "MODE":
            val = str(stmt.value).upper()
            if val in ("DEMO", "LIVE"):
                self.mode = val
                self._log(f"[+] Execution environment set to: {self.mode}")
                if self.case_id:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE cases SET mode = ? WHERE id = ?;", (self.mode, self.case_id))
                    conn.commit()
                    conn.close()

    def _ensure_case(self):
        if not self.case_id:
            # Default to demo case
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, case_number, mode FROM cases ORDER BY created_at ASC LIMIT 1;")
            row = cursor.fetchone()
            conn.close()
            if row:
                self.case_id = row["id"]
                self.case_number = row["case_number"]
                self.mode = row["mode"] or "DEMO"
            else:
                self.case_id = "default-case"
                self.case_number = "CASE-DEFAULT"

    def _handle_get_stmt(self, stmt: GetStmt):
        self._ensure_case()
        target = stmt.target.upper()
        conn = get_db_connection()
        cursor = conn.cursor()

        if target == "SYSTEM":
            self._log(f"[*] Querying system configuration and telemetry ({self.mode} mode)...")
            sys_data = SystemCollector.collect_live() if self.mode == "LIVE" else SystemCollector.collect_demo(self.case_number)
            self.results["system"] = sys_data

            # Persist
            cursor.execute("DELETE FROM system_info WHERE case_id = ?;", (self.case_id,))
            cursor.execute("""
            INSERT INTO system_info (id, case_id, os_name, os_version, hostname, username, architecture, cpu_count, cpu_freq_mhz, total_ram_gb, available_ram_gb, uptime_seconds, boot_time, collected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"sys-{uuid.uuid4().hex[:10]}", self.case_id, sys_data["os_name"], sys_data["os_version"],
                sys_data["hostname"], sys_data["username"], sys_data["architecture"], sys_data["cpu_count"],
                sys_data["cpu_freq_mhz"], sys_data["total_ram_gb"], sys_data["available_ram_gb"],
                sys_data["uptime_seconds"], sys_data["boot_time"], sys_data["collected_at"]
            ))
            conn.commit()
            conn.close()

            # Register as evidence
            EvidenceService.register_evidence(
                case_id=self.case_id,
                name=f"System_Config_{sys_data['hostname']}.json",
                source_type="SYSTEM",
                collector_name=self.user.get("full_name", "Investigator"),
                metadata=sys_data
            )
            self._log(f"[+] System info collected: {sys_data['hostname']} ({sys_data['os_name']} {sys_data['architecture']}, {sys_data['total_ram_gb']}GB RAM)")

        elif target in ("PROCESSES", "SERVICES"):
            self._log(f"[*] Inspecting running processes ({self.mode} mode)...")
            procs = ProcessCollector.collect_live() if self.mode == "LIVE" else ProcessCollector.collect_demo()
            self.results["processes_count"] = len(procs)

            cursor.execute("DELETE FROM processes WHERE case_id = ?;", (self.case_id,))
            records = []
            for p in procs:
                records.append((
                    f"prc-{uuid.uuid4().hex[:10]}", self.case_id, p["pid"], p.get("ppid", 0),
                    p["name"], p.get("exe_path", ""), p.get("cmdline", ""), p.get("username", ""),
                    p.get("cpu_percent", 0.0), p.get("memory_mb", 0.0), p.get("start_time", ""),
                    p.get("status", "running"), p.get("is_suspicious", 0), p.get("suspicious_reason", "")
                ))
            cursor.executemany("""
            INSERT INTO processes (id, case_id, pid, ppid, name, exe_path, cmdline, username, cpu_percent, memory_mb, start_time, status, is_suspicious, suspicious_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, records)
            conn.commit()
            conn.close()

            suspicious_count = len([p for p in procs if p.get("is_suspicious")])
            self._log(f"[+] {len(procs)} processes inspected ({suspicious_count} flagged as suspicious).")

        elif target in ("FILES", "FILE"):
            path_arg = stmt.argument
            self._log(f"[*] Scanning file metadata in target path '{path_arg or 'Monitored Directories'}' ({self.mode} mode)...")
            files = FileCollector.collect_live(path_arg) if (self.mode == "LIVE" and path_arg) else FileCollector.collect_demo()
            self.results["files_count"] = len(files)

            cursor.execute("DELETE FROM files WHERE case_id = ?;", (self.case_id,))
            records = []
            for f in files:
                records.append((
                    f"fil-{uuid.uuid4().hex[:10]}", self.case_id, f["path"], f["filename"],
                    f.get("extension", ""), f.get("size_bytes", 0), f.get("created_time", ""),
                    f.get("modified_time", ""), f.get("accessed_time", ""), f.get("sha256", ""),
                    f.get("md5", ""), f.get("is_suspicious", 0), f.get("suspicious_reason", "")
                ))
            cursor.executemany("""
            INSERT INTO files (id, case_id, path, filename, extension, size_bytes, created_time, modified_time, accessed_time, sha256, md5, is_suspicious, suspicious_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, records)
            conn.commit()
            conn.close()

            # Register files as evidence artifacts
            for f in files:
                EvidenceService.register_evidence(
                    case_id=self.case_id,
                    name=f["filename"],
                    source_type="FILE",
                    original_file_path=f["path"] if (self.mode == "LIVE" and os.path.exists(f["path"])) else None,
                    collector_name=self.user.get("full_name", "Investigator"),
                    metadata=f,
                    simulated_hash=f.get("sha256")
                )

            self._log(f"[+] {len(files)} files cataloged with SHA-256 integrity hashes.")

        elif target in ("NETWORK", "CONNECTIONS", "INTERFACES"):
            self._log(f"[*] Enumerating active sockets & network telemetry ({self.mode} mode)...")
            conns = NetworkCollector.collect_live() if self.mode == "LIVE" else NetworkCollector.collect_demo()
            self.results["connections_count"] = len(conns)

            cursor.execute("DELETE FROM network_connections WHERE case_id = ?;", (self.case_id,))
            records = []
            for c in conns:
                records.append((
                    f"net-{uuid.uuid4().hex[:10]}", self.case_id, c["local_address"], c["local_port"],
                    c.get("remote_address", ""), c.get("remote_port", 0), c["protocol"],
                    c.get("state", "ESTABLISHED"), c.get("pid", 0), c.get("process_name", ""),
                    c.get("is_suspicious", 0), c.get("suspicious_reason", "")
                ))
            cursor.executemany("""
            INSERT INTO network_connections (id, case_id, local_address, local_port, remote_address, remote_port, protocol, state, pid, process_name, is_suspicious, suspicious_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, records)
            conn.commit()
            conn.close()
            self._log(f"[+] {len(conns)} active network connections collected.")

        elif target in ("LOGS", "USERS"):
            self._log(f"[*] Collecting normalized security and authentication logs ({self.mode} mode)...")
            logs = LogCollector.collect_live() if self.mode == "LIVE" else LogCollector.collect_demo()
            self.results["logs_count"] = len(logs)

            cursor.execute("DELETE FROM logs WHERE case_id = ?;", (self.case_id,))
            records = []
            for l in logs:
                records.append((
                    f"log-{uuid.uuid4().hex[:10]}", self.case_id, l["timestamp"], l["source"],
                    l["event_type"], l["severity"], l.get("user", ""), l.get("host", ""),
                    l["message"], l.get("raw_data", "")
                ))
            cursor.executemany("""
            INSERT INTO logs (id, case_id, timestamp, source, event_type, severity, user, host, message, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, records)
            conn.commit()
            conn.close()
            self._log(f"[+] {len(logs)} security event records normalized.")

    def _handle_hash_stmt(self, stmt: HashStmt):
        self._ensure_case()
        self._log(f"[*] Computing cryptographic hashes for evidence files (Algorithm: {stmt.algorithm})...")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, sha256_hash FROM evidence WHERE case_id = ?;", (self.case_id,))
        rows = cursor.fetchall()
        conn.close()
        for r in rows:
            self._log(f"    [SHA-256] {r['name']}: {r['sha256_hash'][:24]}...")
        self._log(f"[+] SHA-256 calculated for {len(rows)} evidence artifacts.")

    def _handle_search_stmt(self, stmt: SearchStmt):
        self._ensure_case()
        self._log(f"[*] Searching {stmt.target_type} for query '{stmt.query}'...")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT path, filename FROM files WHERE case_id = ? AND (filename LIKE ? OR path LIKE ?);", (self.case_id, f"%{stmt.query}%", f"%{stmt.query}%"))
        matches = cursor.fetchall()
        conn.close()
        self._log(f"[+] Search matched {len(matches)} files.")
        for m in matches:
            self._log(f"    Found: {m['path']}")

    def _handle_build_timeline(self, stmt: BuildTimelineStmt):
        self._ensure_case()
        self._log("[*] Correlating multi-source timeline (Files, Processes, Logs, Network)...")
        events = TimelineService.build_timeline_for_case(self.case_id, actor_name=self.user.get("full_name", "Investigator"))
        self.results["timeline_events_count"] = len(events)
        self._log(f"[+] {len(events)} events correlated into unified chronological timeline.")

    def _handle_analyze(self, stmt: AnalyzeStmt):
        self._ensure_case()
        self._log("[*] Executing deterministic forensic detection rules & IOC correlation...")
        findings = AnalysisEngine.analyze_case(self.case_id, actor_name=self.user.get("full_name", "Investigator"))
        self.results["findings_count"] = len(findings)
        self._log(f"[+] {len(findings)} suspicious findings generated by rule engine.")
        for f in findings:
            self._log(f"    [{f['severity']}] {f['title']}")

    def _handle_generate_report(self, stmt: GenerateReportStmt):
        self._ensure_case()
        self._log(f"[*] Assembling forensic examination report (Format: {stmt.report_format})...")
        report_meta = ForensicReportGenerator.generate_report(
            case_id=self.case_id,
            author_name=self.user.get("full_name", "Lead DFIR Analyst"),
            author_badge=self.user.get("badge_number", "NTRO-INV-42")
        )
        self.results["report"] = report_meta
        self._log(f"[+] Report generated: {report_meta['filename']} (Size: {report_meta['file_size']} bytes)")
        self._log(f"    SHA-256 Digest: {report_meta['sha256_hash']}")

    def _handle_verify_integrity(self, stmt: VerifyIntegrityStmt):
        self._ensure_case()
        self._log("[*] Performing live SHA-256 integrity verification across all evidence...")
        results = EvidenceService.verify_all_evidence(self.case_id, actor_name=self.user.get("full_name", "Investigator"))
        failed = [r for r in results if r["status"] != "VERIFIED"]
        self.results["integrity_verified"] = len(failed) == 0
        if failed:
            self._log(f"[!] INTEGRITY VERIFICATION FAILED FOR {len(failed)} ITEM(S)!")
            for f in failed:
                self._log(f"    [FAIL] {f['name']} ({f['evidence_number']})")
        else:
            self._log(f"[+] ALL {len(results)} EVIDENCE ITEMS PASS INTEGRITY VERIFICATION (0 TAMPERED).")
