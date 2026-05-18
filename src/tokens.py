# ── tokens.py ──────────────────────────────────────────────────────────────
# Define los tipos de token reconocidos por CalcScript y las palabras
# reservadas que no pueden usarse como identificadores.

from enum import Enum, auto


class TokenType(Enum):
    """Tipos de token reconocidos por el analizador léxico de CalcScript."""
    NUMBER_INT = auto()
    NUMBER_FLOAT = auto()
    STRING = auto()
    IDENTIFIER = auto()
    KEYWORD = auto()
    OPERATOR = auto()
    DELIMITER = auto()
    EOF = auto()
    ERROR = auto()


KEYWORDS: set[str] = {
    "if", "else", "while", "func", "return", "print",
}
