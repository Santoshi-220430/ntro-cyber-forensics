"""
Forensic DSL - Lexer Implementation
Problem ID: SIH26148 | NTRO Cyber Forensics Prototype
"""

from typing import List
from .tokens import Token, TokenType, KEYWORDS, TARGETS, FORBIDDEN_VERBS

class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Lexer Error at line {line}, col {column}: {message}")
        self.message = message
        self.line = line
        self.column = column

class Lexer:
    def __init__(self, source_code: str):
        self.source = source_code
        self.length = len(source_code)
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def _peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        if idx < self.length:
            return self.source[idx]
        return ""

    def _advance(self) -> str:
        if self.pos < self.length:
            char = self.source[self.pos]
            self.pos += 1
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            return char
        return ""

    def tokenize(self) -> List[Token]:
        self.tokens = []
        while self.pos < self.length:
            char = self._peek()

            # Skip single-line comments (# or //)
            if char == '#' or (char == '/' and self._peek(1) == '/'):
                while self.pos < self.length and self._peek() != '\n':
                    self._advance()
                continue

            # Whitespace handling
            if char in ' \t\r':
                self._advance()
                continue

            if char == '\n':
                tok_line = self.line
                tok_col = self.column
                self._advance()
                # Deduplicate consecutive newlines
                if self.tokens and self.tokens[-1].type != TokenType.NEWLINE:
                    self.tokens.append(Token(TokenType.NEWLINE, "\n", tok_line, tok_col, "\n"))
                continue

            # String literals
            if char in ('"', "'"):
                quote_char = char
                start_line = self.line
                start_col = self.column
                self._advance() # consume opening quote
                val_chars = []
                while self.pos < self.length and self._peek() != quote_char:
                    c = self._advance()
                    if c == '\\':
                        # Escape sequences
                        next_c = self._advance()
                        if next_c == 'n': val_chars.append('\n')
                        elif next_c == 't': val_chars.append('\t')
                        elif next_c == '\\': val_chars.append('\\')
                        elif next_c == quote_char: val_chars.append(quote_char)
                        else: val_chars.append(next_c)
                    else:
                        val_chars.append(c)

                if self.pos >= self.length and self._peek() != quote_char:
                    raise LexerError(f"Unterminated string literal starting at line {start_line}, col {start_col}", start_line, start_col)
                self._advance() # consume closing quote
                self.tokens.append(Token(TokenType.STRING, "".join(val_chars), start_line, start_col, f'"{val_chars}"'))
                continue

            # Punctuation
            if char == '[':
                self.tokens.append(Token(TokenType.LBRACKET, "[", self.line, self.column, "["))
                self._advance()
                continue
            if char == ']':
                self.tokens.append(Token(TokenType.RBRACKET, "]", self.line, self.column, "]"))
                self._advance()
                continue
            if char == '=':
                self.tokens.append(Token(TokenType.EQUALS, "=", self.line, self.column, "="))
                self._advance()
                continue
            if char == ',':
                self.tokens.append(Token(TokenType.COMMA, ",", self.line, self.column, ","))
                self._advance()
                continue

            # Numbers
            if char.isdigit():
                start_line = self.line
                start_col = self.column
                num_chars = []
                while self.pos < self.length and (self._peek().isdigit() or self._peek() == '.'):
                    num_chars.append(self._advance())
                num_str = "".join(num_chars)
                val = float(num_str) if '.' in num_str else int(num_str)
                self.tokens.append(Token(TokenType.NUMBER, val, start_line, start_col, num_str))
                continue

            # Words (Keywords, Targets, Identifiers, Forbidden Verbs)
            if char.isalpha() or char in '_-':
                start_line = self.line
                start_col = self.column
                word_chars = []
                while self.pos < self.length and (self._peek().isalnum() or self._peek() in '_-.'):
                    word_chars.append(self._advance())
                word = "".join(word_chars)
                upper_word = word.upper()

                if upper_word in FORBIDDEN_VERBS:
                    self.tokens.append(Token(TokenType.BLOCKED_VERB, upper_word, start_line, start_col, word))
                elif upper_word in KEYWORDS:
                    self.tokens.append(Token(KEYWORDS[upper_word], upper_word, start_line, start_col, word))
                elif upper_word in TARGETS:
                    self.tokens.append(Token(TARGETS[upper_word], upper_word, start_line, start_col, word))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, word, start_line, start_col, word))
                continue

            # Unrecognized character
            raise LexerError(f"Unexpected character: {char!r}", self.line, self.column)

        # Append final EOF
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column, ""))
        return self.tokens
