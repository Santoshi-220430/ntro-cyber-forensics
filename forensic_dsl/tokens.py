"""
Forensic DSL - Token Definitions
Problem ID: SIH26148 | NTRO Cyber Forensics Prototype
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional

class TokenType(Enum):
    # Keywords / Command Verbs
    CASE = auto()
    GET = auto()
    HASH = auto()
    SEARCH = auto()
    BUILD = auto()
    ANALYZE = auto()
    GENERATE = auto()
    VERIFY = auto()
    CORRELATE = auto()
    SET = auto()

    # Targets / Entities
    SYSTEM = auto()
    USERS = auto()
    PROCESSES = auto()
    SERVICES = auto()
    NETWORK = auto()
    CONNECTIONS = auto()
    INTERFACES = auto()
    DNS = auto()
    LOGS = auto()
    FILES = auto()
    FILE = auto()
    TIMELINE = auto()
    REPORT = auto()
    EVIDENCE = auto()
    INTEGRITY = auto()
    PCAP = auto()
    MODE = auto()

    # Explicitly Blocked / Destructive Verbs for Safety
    BLOCKED_VERB = auto()

    # Literals & Syntax
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    EQUALS = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    NEWLINE = auto()
    EOF = auto()

@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int
    raw: str = ""

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {repr(self.value)}, L{self.line}:C{self.column})"

# Recognized allowed command keywords
KEYWORDS = {
    "CASE": TokenType.CASE,
    "GET": TokenType.GET,
    "HASH": TokenType.HASH,
    "SEARCH": TokenType.SEARCH,
    "BUILD": TokenType.BUILD,
    "ANALYZE": TokenType.ANALYZE,
    "GENERATE": TokenType.GENERATE,
    "VERIFY": TokenType.VERIFY,
    "CORRELATE": TokenType.CORRELATE,
    "SET": TokenType.SET,
}

# Recognized entity targets
TARGETS = {
    "SYSTEM": TokenType.SYSTEM,
    "USERS": TokenType.USERS,
    "PROCESSES": TokenType.PROCESSES,
    "SERVICES": TokenType.SERVICES,
    "NETWORK": TokenType.NETWORK,
    "CONNECTIONS": TokenType.CONNECTIONS,
    "INTERFACES": TokenType.INTERFACES,
    "DNS": TokenType.DNS,
    "LOGS": TokenType.LOGS,
    "FILES": TokenType.FILES,
    "FILE": TokenType.FILE,
    "TIMELINE": TokenType.TIMELINE,
    "REPORT": TokenType.REPORT,
    "EVIDENCE": TokenType.EVIDENCE,
    "INTEGRITY": TokenType.INTEGRITY,
    "PCAP": TokenType.PCAP,
    "MODE": TokenType.MODE,
}

# Explicitly forbidden/destructive commands that will be blocked
FORBIDDEN_VERBS = {
    "DELETE", "REMOVE", "DROP", "MODIFY", "UPDATE", "EXEC", "EXECUTE",
    "RUN", "KILL", "TERMINATE", "FORMAT", "SHUTDOWN", "REBOOT",
    "WIPE", "INJECT", "HOOK", "UNHOOK", "BYPASS", "DISABLE", "CLEAR"
}
