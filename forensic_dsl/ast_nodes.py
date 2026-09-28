"""
Forensic DSL - Abstract Syntax Tree (AST) Nodes
Problem ID: SIH26148 | NTRO Cyber Forensics Prototype
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ASTNode:
    line: int = 1
    col: int = 1

    def to_dict(self) -> Dict[str, Any]:
        result = {"type": self.__class__.__name__, "line": self.line, "col": self.col}
        for k, v in self.__dict__.items():
            if k not in ("line", "col"):
                if isinstance(v, ASTNode):
                    result[k] = v.to_dict()
                elif isinstance(v, list) and v and isinstance(v[0], ASTNode):
                    result[k] = [item.to_dict() for item in v]
                else:
                    result[k] = v
        return result

@dataclass
class ProgramNode(ASTNode):
    statements: List[ASTNode] = field(default_factory=list)

@dataclass
class CaseStmt(ASTNode):
    case_id: str = ""

@dataclass
class GetStmt(ASTNode):
    target: str = "" # SYSTEM, USERS, PROCESSES, SERVICES, NETWORK, LOGS, FILES, DNS, etc.
    argument: Optional[str] = None # e.g. path "/Documents" or interface name
    options: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HashStmt(ASTNode):
    target_type: str = "FILES" # FILE or FILES
    path: Optional[str] = None
    algorithm: str = "SHA256"

@dataclass
class SearchStmt(ASTNode):
    target_type: str = "FILES"
    query: str = ""
    path: Optional[str] = None

@dataclass
class BuildTimelineStmt(ASTNode):
    options: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyzeStmt(ASTNode):
    options: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GenerateReportStmt(ASTNode):
    report_format: str = "PDF" # PDF, JSON, HTML
    options: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VerifyIntegrityStmt(ASTNode):
    target: str = "EVIDENCE"
    options: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SetStmt(ASTNode):
    key: str = ""
    value: Any = None

@dataclass
class BlockedCommandStmt(ASTNode):
    verb: str = ""
    details: str = ""
    reason: str = "Destructive or unauthorized operation not permitted in Forensic DSL"
