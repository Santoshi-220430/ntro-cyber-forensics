"""
Forensic DSL - Recursive Descent Parser
Problem ID: SIH26148 | NTRO Cyber Forensics Prototype
"""

from typing import List, Optional, Dict, Any
from .tokens import Token, TokenType
from .ast_nodes import (
    ProgramNode, ASTNode, CaseStmt, GetStmt, HashStmt,
    SearchStmt, BuildTimelineStmt, AnalyzeStmt, GenerateReportStmt,
    VerifyIntegrityStmt, SetStmt, BlockedCommandStmt
)

class ParserError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Parser Error at line {line}, col {column}: {message}")
        self.message = message
        self.line = line
        self.column = column

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def _current(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def _peek(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]

    def _advance(self) -> Token:
        tok = self._current()
        if self.pos < len(self.tokens):
            self.pos += 1
        return tok

    def _match(self, *expected_types: TokenType) -> bool:
        if self._current().type in expected_types:
            self._advance()
            return True
        return False

    def _expect(self, expected_type: TokenType, error_msg: Optional[str] = None) -> Token:
        tok = self._current()
        if tok.type != expected_type:
            msg = error_msg or f"Expected token {expected_type.name}, but found {tok.type.name} ('{tok.value}')"
            raise ParserError(msg, tok.line, tok.column)
        return self._advance()

    def _skip_newlines(self):
        while self._current().type == TokenType.NEWLINE:
            self._advance()

    def parse(self) -> ProgramNode:
        statements: List[ASTNode] = []
        self._skip_newlines()

        while self._current().type != TokenType.EOF:
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
            self._skip_newlines()

        return ProgramNode(statements=statements)

    def _parse_options_block(self) -> Dict[str, Any]:
        options = {}
        if self._match(TokenType.LBRACKET):
            while self._current().type != TokenType.RBRACKET and self._current().type != TokenType.EOF:
                opt_key_tok = self._current()
                if opt_key_tok.type in (TokenType.IDENTIFIER, TokenType.STRING) or opt_key_tok.type.name in ('SEVERITY', 'LIMIT', 'FORMAT', 'ALGORITHM', 'PATH'):
                    key = str(opt_key_tok.value).upper()
                    self._advance()
                    # optional equals
                    self._match(TokenType.EQUALS)
                    val_tok = self._current()
                    val = val_tok.value
                    self._advance()
                    options[key] = val
                    self._match(TokenType.COMMA)
                else:
                    self._advance()
            self._expect(TokenType.RBRACKET, "Expected ']' at end of options block")
        return options

    def _parse_statement(self) -> ASTNode:
        tok = self._current()

        # Handle Blocked/Forbidden Verbs immediately
        if tok.type == TokenType.BLOCKED_VERB:
            verb = str(tok.value)
            line = tok.line
            col = tok.column
            self._advance()
            # gather remainder of line for context
            rest_parts = []
            while self._current().type not in (TokenType.NEWLINE, TokenType.EOF):
                rest_parts.append(str(self._advance().value))
            return BlockedCommandStmt(
                line=line, col=col,
                verb=verb,
                details=f"{verb} {' '.join(rest_parts)}".strip(),
                reason=f"Destructive or mutating operation '{verb}' is prohibited by forensic integrity rules"
            )

        # CASE command
        if tok.type == TokenType.CASE:
            self._advance()
            val_tok = self._current()
            if val_tok.type in (TokenType.STRING, TokenType.IDENTIFIER):
                case_id = str(val_tok.value)
                self._advance()
                return CaseStmt(line=tok.line, col=tok.column, case_id=case_id)
            raise ParserError("Expected Case ID string or identifier after CASE", val_tok.line, val_tok.column)

        # GET command
        if tok.type == TokenType.GET:
            self._advance()
            target_tok = self._current()
            valid_targets = (
                TokenType.SYSTEM, TokenType.USERS, TokenType.PROCESSES,
                TokenType.SERVICES, TokenType.NETWORK, TokenType.CONNECTIONS,
                TokenType.INTERFACES, TokenType.DNS, TokenType.LOGS,
                TokenType.FILES, TokenType.FILE, TokenType.PCAP, TokenType.EVIDENCE
            )
            if target_tok.type in valid_targets or target_tok.type == TokenType.IDENTIFIER:
                target_name = str(target_tok.value).upper()
                self._advance()

                argument = None
                # Check for argument (e.g. path or filter string)
                if self._current().type in (TokenType.STRING, TokenType.IDENTIFIER):
                    argument = str(self._current().value)
                    self._advance()

                options = self._parse_options_block()
                return GetStmt(
                    line=tok.line, col=tok.column,
                    target=target_name, argument=argument, options=options
                )
            raise ParserError(f"Unexpected target '{target_tok.value}' for GET command. Expected SYSTEM, USERS, PROCESSES, etc.", target_tok.line, target_tok.column)

        # HASH command
        if tok.type == TokenType.HASH:
            self._advance()
            next_tok = self._current()
            if next_tok.type == TokenType.FILE:
                self._advance()
                path = None
                if self._current().type in (TokenType.STRING, TokenType.IDENTIFIER):
                    path = str(self._current().value)
                    self._advance()
                else:
                    raise ParserError("Expected file path after HASH FILE", self._current().line, self._current().column)
                options = self._parse_options_block()
                return HashStmt(
                    line=tok.line, col=tok.column,
                    target_type="FILE", path=path,
                    algorithm=options.get("ALGORITHM", "SHA256")
                )
            elif next_tok.type == TokenType.FILES or next_tok.type == TokenType.EVIDENCE:
                self._advance()
                path = None
                if self._current().type in (TokenType.STRING, TokenType.IDENTIFIER):
                    path = str(self._current().value)
                    self._advance()
                options = self._parse_options_block()
                return HashStmt(
                    line=tok.line, col=tok.column,
                    target_type="FILES", path=path,
                    algorithm=options.get("ALGORITHM", "SHA256")
                )
            else:
                # Default to HASH FILES
                return HashStmt(line=tok.line, col=tok.column, target_type="FILES")

        # SEARCH command
        if tok.type == TokenType.SEARCH:
            self._advance()
            target_type = "FILES"
            if self._current().type in (TokenType.FILES, TokenType.LOGS):
                target_type = str(self._current().value).upper()
                self._advance()
            query_tok = self._current()
            if query_tok.type in (TokenType.STRING, TokenType.IDENTIFIER):
                query = str(query_tok.value)
                self._advance()
                path = None
                if self._current().type in (TokenType.STRING, TokenType.IDENTIFIER):
                    path = str(self._current().value)
                    self._advance()
                return SearchStmt(line=tok.line, col=tok.column, target_type=target_type, query=query, path=path)
            raise ParserError("Expected search term after SEARCH", query_tok.line, query_tok.column)

        # BUILD TIMELINE
        if tok.type == TokenType.BUILD:
            self._advance()
            next_tok = self._current()
            if next_tok.type == TokenType.TIMELINE or str(next_tok.value).upper() == "TIMELINE":
                self._advance()
                options = self._parse_options_block()
                return BuildTimelineStmt(line=tok.line, col=tok.column, options=options)
            raise ParserError("Expected TIMELINE after BUILD", next_tok.line, next_tok.column)

        # ANALYZE
        if tok.type == TokenType.ANALYZE:
            self._advance()
            options = self._parse_options_block()
            return AnalyzeStmt(line=tok.line, col=tok.column, options=options)

        # GENERATE REPORT
        if tok.type == TokenType.GENERATE:
            self._advance()
            next_tok = self._current()
            if next_tok.type == TokenType.REPORT or str(next_tok.value).upper() == "REPORT":
                self._advance()
                fmt = "PDF"
                if self._current().type in (TokenType.IDENTIFIER, TokenType.STRING):
                    fmt = str(self._current().value).upper()
                    self._advance()
                options = self._parse_options_block()
                return GenerateReportStmt(line=tok.line, col=tok.column, report_format=fmt, options=options)
            raise ParserError("Expected REPORT after GENERATE", next_tok.line, next_tok.column)

        # VERIFY INTEGRITY
        if tok.type == TokenType.VERIFY:
            self._advance()
            target = "EVIDENCE"
            if self._current().type in (TokenType.INTEGRITY, TokenType.EVIDENCE) or str(self._current().value).upper() in ("INTEGRITY", "EVIDENCE"):
                target = str(self._current().value).upper()
                self._advance()
            options = self._parse_options_block()
            return VerifyIntegrityStmt(line=tok.line, col=tok.column, target=target, options=options)

        # SET MODE / SET VAR
        if tok.type == TokenType.SET:
            self._advance()
            key_tok = self._current()
            key = str(key_tok.value).upper()
            self._advance()
            self._match(TokenType.EQUALS)
            val_tok = self._current()
            val = val_tok.value
            self._advance()
            return SetStmt(line=tok.line, col=tok.column, key=key, value=val)

        # Catch unrecognized commands
        unknown_val = str(tok.value)
        line = tok.line
        col = tok.column
        self._advance()
        raise ParserError(f"Unrecognized forensic command '{unknown_val}'", line, col)
