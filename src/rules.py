# ── rules.py ───────────────────────────────────────────────────────────────
# Pares (TokenType, regex) evaluados en orden por el lexer principal.
# IMPORTANTE: NUMBER_FLOAT debe ir antes que NUMBER_INT.

import re
from tokens import TokenType

RULES: list[tuple[TokenType | None, re.Pattern]] = [
    (None, re.compile(r'[ \t\r]+')),
    (None, re.compile(r'#[^\n]*')),
    (TokenType.NUMBER_FLOAT, re.compile(r'\d+\.\d+')),
    (TokenType.NUMBER_INT,   re.compile(r'\d+')),
    (TokenType.STRING, re.compile(r'"[^"\n]*"')),
    (TokenType.IDENTIFIER, re.compile(r'[A-Za-z_][A-Za-z_0-9]*')),
    (TokenType.OPERATOR, re.compile(r'==|!=|>=|<=')),
    (TokenType.OPERATOR, re.compile(r'[+\-*/=<>]')),
    (TokenType.DELIMITER, re.compile(r'[;,(){}]')),
]
