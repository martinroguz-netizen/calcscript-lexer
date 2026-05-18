# ── lexer.py ───────────────────────────────────────────────────────────────
# Clase principal del analizador léxico de CalcScript.
# Recibe el texto fuente y produce una lista de Token y una lista de errores.

from dataclasses import dataclass
from tokens import TokenType, KEYWORDS
from rules import RULES


@dataclass
class Token:
    """Unidad léxica reconocida."""
    index: int
    type: TokenType
    value: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"{self.index}: ({self.type.name}, \"{self.value}\")"


@dataclass
class LexError:
    """Error léxico con ubicación exacta."""
    line: int
    column: int
    message: str

    def __str__(self) -> str:
        return f"Line {self.line}, Column {self.column}: {self.message}"


class Lexer:
    """Analizador léxico de CalcScript."""

    def __init__(self, source: str) -> None:
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []
        self.errors: list[LexError] = []
        self._token_index = 0

    def tokenize(self) -> tuple[list[Token], list[LexError]]:
        while self.pos < len(self.source):
            ch = self.source[self.pos]
            if ch == '\n':
                self.line += 1
                self.column = 1
                self.pos += 1
                continue
            if not self._match_rule():
                self._report_unknown_symbol(ch)
                self._advance(1)
        return self.tokens, self.errors

    def _match_rule(self) -> bool:
        for tok_type, pattern in RULES:
            m = pattern.match(self.source, self.pos)
            if not m:
                continue
            lexeme = m.group(0)
            start_line, start_col = self.line, self.column
            if tok_type is None:
                self._advance(len(lexeme))
                return True
            actual_type = tok_type
            if tok_type is TokenType.IDENTIFIER and lexeme in KEYWORDS:
                actual_type = TokenType.KEYWORD
            self._emit(actual_type, lexeme, start_line, start_col)
            self._advance(len(lexeme))
            if tok_type is TokenType.NUMBER_INT and self.pos < len(self.source):
                nxt = self.source[self.pos]
                if nxt.isalpha() or nxt == '_':
                    self.errors.append(LexError(
                        start_line, start_col,
                        f"Invalid identifier: identifiers cannot start "
                        f"with a digit near '{lexeme[0]}'",
                    ))
            return True
        return False

    def _emit(self, tok_type, lexeme, line, column):
        self._token_index += 1
        self.tokens.append(Token(
            index=self._token_index, type=tok_type,
            value=lexeme, line=line, column=column,
        ))

    def _report_unknown_symbol(self, ch):
        self.errors.append(LexError(
            self.line, self.column, f"Unknown symbol '{ch}' detected",
        ))

    def _advance(self, n):
        self.pos += n
        self.column += n
