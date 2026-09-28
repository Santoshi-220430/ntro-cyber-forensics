"""
Forensic DSL - Validator and Security Policy Enforcement
Problem ID: SIH26148 | NTRO Cyber Forensics Prototype
"""

import os
from typing import List, Dict, Any, Tuple
from .ast_nodes import (
    ProgramNode, ASTNode, CaseStmt, GetStmt, HashStmt,
    SearchStmt, BuildTimelineStmt, AnalyzeStmt, GenerateReportStmt,
    VerifyIntegrityStmt, SetStmt, BlockedCommandStmt
)

class ValidationError:
    def __init__(self, message: str, line: int = 1, col: int = 1, severity: str = "ERROR", code: str = "VAL_ERR"):
        self.message = message
        self.line = line
        self.col = col
        self.severity = severity
        self.code = code

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "line": self.line,
            "col": self.col,
            "severity": self.severity,
            "code": self.code
        }

class DSLValidator:
    ALLOWED_TARGETS = {
        "SYSTEM", "USERS", "PROCESSES", "SERVICES", "NETWORK",
        "CONNECTIONS", "INTERFACES", "DNS", "LOGS", "FILES",
        "FILE", "PCAP", "EVIDENCE", "TIMELINE", "REPORT", "INTEGRITY", "MODE"
    }

    ROLE_PERMISSIONS = {
        "ADMIN": {"READ", "COLLECT", "ANALYZE", "EXPORT", "CONFIG", "POLICY"},
        "INVESTIGATOR": {"READ", "COLLECT", "ANALYZE", "EXPORT"},
        "VIEWER": {"READ"}
    }

    def __init__(self, user_role: str = "INVESTIGATOR", policy_mode: str = "FORENSIC_READ_ONLY"):
        self.user_role = user_role.upper()
        self.policy_mode = policy_mode
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    def validate(self, program: ProgramNode, default_case_id: str = None) -> Tuple[bool, List[Dict[str, Any]], List[Dict[str, Any]]]:
        self.errors = []
        self.warnings = []

        if not program.statements:
            self.errors.append(ValidationError("Empty forensic script. No executable statements provided.", line=1, col=1, code="EMPTY_SCRIPT"))
            return False, [e.to_dict() for e in self.errors], []

        has_case_stmt = False
        detected_case_id = default_case_id

        for stmt in program.statements:
            if isinstance(stmt, BlockedCommandStmt):
                self.errors.append(ValidationError(
                    f"COMMAND BLOCKED: '{stmt.details}'. Reason: {stmt.reason}",
                    line=stmt.line, col=stmt.col,
                    code="DESTRUCTIVE_COMMAND_BLOCKED"
                ))
            elif isinstance(stmt, CaseStmt):
                has_case_stmt = True
                detected_case_id = stmt.case_id
                if not stmt.case_id.strip():
                    self.errors.append(ValidationError("CASE statement cannot have an empty Case ID", stmt.line, stmt.col, code="INVALID_CASE_ID"))
            elif isinstance(stmt, GetStmt):
                self._validate_get(stmt)
            elif isinstance(stmt, HashStmt):
                self._validate_hash(stmt)
            elif isinstance(stmt, SearchStmt):
                self._validate_search(stmt)
            elif isinstance(stmt, BuildTimelineStmt):
                self._check_role_permission("ANALYZE", stmt.line, stmt.col, "BUILD TIMELINE")
            elif isinstance(stmt, AnalyzeStmt):
                self._check_role_permission("ANALYZE", stmt.line, stmt.col, "ANALYZE")
            elif isinstance(stmt, GenerateReportStmt):
                self._check_role_permission("EXPORT", stmt.line, stmt.col, "GENERATE REPORT")
            elif isinstance(stmt, VerifyIntegrityStmt):
                self._check_role_permission("READ", stmt.line, stmt.col, "VERIFY INTEGRITY")
            elif isinstance(stmt, SetStmt):
                if stmt.key not in ("MODE", "LIMIT", "LOG_LEVEL"):
                    self.warnings.append(ValidationError(f"Unknown configuration key '{stmt.key}'", stmt.line, stmt.col, severity="WARNING", code="UNKNOWN_CONFIG"))

        if not has_case_stmt and not default_case_id:
            self.warnings.append(ValidationError(
                "No CASE identifier declared in script. Script execution will require an active case context.",
                line=1, col=1, severity="WARNING", code="MISSING_CASE_STMT"
            ))

        is_valid = len(self.errors) == 0
        return is_valid, [e.to_dict() for e in self.errors], [w.to_dict() for w in self.warnings]

    def _check_role_permission(self, required_perm: str, line: int, col: int, cmd_name: str):
        perms = self.ROLE_PERMISSIONS.get(self.user_role, set())
        if required_perm not in perms:
            self.errors.append(ValidationError(
                f"Permission Denied: User role '{self.user_role}' is not authorized to execute '{cmd_name}' (requires '{required_perm}' permission)",
                line=line, col=col, code="RBAC_PERMISSION_DENIED"
            ))

    def _validate_get(self, stmt: GetStmt):
        self._check_role_permission("COLLECT", stmt.line, stmt.col, f"GET {stmt.target}")
        if stmt.target not in self.ALLOWED_TARGETS:
            self.errors.append(ValidationError(
                f"Unsupported target '{stmt.target}' for GET command. Allowed targets: {', '.join(sorted(self.ALLOWED_TARGETS))}",
                stmt.line, stmt.col, code="INVALID_TARGET"
            ))

        # Check path safety if argument is provided
        if stmt.argument and stmt.target in ("FILES", "FILE", "PCAP"):
            self._validate_safe_path(stmt.argument, stmt.line, stmt.col)

    def _validate_hash(self, stmt: HashStmt):
        self._check_role_permission("READ", stmt.line, stmt.col, f"HASH {stmt.target_type}")
        if stmt.path:
            self._validate_safe_path(stmt.path, stmt.line, stmt.col)

    def _validate_search(self, stmt: SearchStmt):
        self._check_role_permission("READ", stmt.line, stmt.col, f"SEARCH {stmt.target_type}")
        if stmt.path:
            self._validate_safe_path(stmt.path, stmt.line, stmt.col)

    def _validate_safe_path(self, path: str, line: int, col: int):
        # Prevent directory traversal attacks
        normalized = os.path.normpath(path)
        if ".." in normalized.split(os.sep):
            self.errors.append(ValidationError(
                f"Security Violation: Path traversal characters ('..') detected in path: '{path}'",
                line, col, code="PATH_TRAVERSAL_DETECTED"
            ))
