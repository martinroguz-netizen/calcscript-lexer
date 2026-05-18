"""
INSTRUCCIONES:
1. Descarga este archivo
2. Ponlo en: C:\\Users\\USER\\Downloads\\calcscript-lexer\\calcscript-lexer\\
3. Abre la terminal de VS Code y corre:
      python setup_proyecto.py
4. Listo. Todos los archivos se crean/reemplazan automáticamente.
"""
import os

# Crear carpetas si no existen
os.makedirs("src", exist_ok=True)
os.makedirs("tests/valid", exist_ok=True)
os.makedirs("tests/invalid", exist_ok=True)
os.makedirs("docs", exist_ok=True)
os.makedirs("grammar", exist_ok=True)
os.makedirs("capturas", exist_ok=True)

def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✓ {path}")

print("Creando archivos del proyecto CalcScript...\n")

# ══════════════════════════════════════════════════════════════════
# src/tokens.py
# ══════════════════════════════════════════════════════════════════
write("src/tokens.py", r'''# ── tokens.py ──────────────────────────────────────────────────────────────
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
''')

# ══════════════════════════════════════════════════════════════════
# src/rules.py
# ══════════════════════════════════════════════════════════════════
write("src/rules.py", r'''# ── rules.py ───────────────────────────────────────────────────────────────
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
''')

# ══════════════════════════════════════════════════════════════════
# src/lexer.py
# ══════════════════════════════════════════════════════════════════
write("src/lexer.py", r'''# ── lexer.py ───────────────────────────────────────────────────────────────
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
''')

# ══════════════════════════════════════════════════════════════════
# src/ast_nodes.py
# ══════════════════════════════════════════════════════════════════
write("src/ast_nodes.py", r'''# ── ast_nodes.py ───────────────────────────────────────────────────────────
# Nodos del Árbol de Sintaxis Abstracta (AST) de CalcScript.

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Program:
    statements: list = field(default_factory=list)

@dataclass
class Block:
    statements: list = field(default_factory=list)

@dataclass
class FuncDecl:
    name: str
    params: list[str]
    body: Block

@dataclass
class IfStmt:
    condition: object
    then_block: Block
    else_block: Block | None = None

@dataclass
class WhileStmt:
    condition: object
    body: Block

@dataclass
class ReturnStmt:
    value: object = None

@dataclass
class PrintStmt:
    value: object

@dataclass
class Assignment:
    name: str
    value: object

@dataclass
class ExprStmt:
    expr: object

@dataclass
class BinaryOp:
    op: str
    left: object
    right: object

@dataclass
class UnaryOp:
    op: str
    operand: object

@dataclass
class Call:
    callee: str
    args: list = field(default_factory=list)

@dataclass
class IntLiteral:
    value: int

@dataclass
class FloatLiteral:
    value: float

@dataclass
class StringLiteral:
    value: str

@dataclass
class Identifier:
    name: str


def ast_to_string(node, indent: int = 0) -> str:
    pad = "  " * indent
    if isinstance(node, IntLiteral):
        return f"{pad}IntLiteral({node.value})"
    if isinstance(node, FloatLiteral):
        return f"{pad}FloatLiteral({node.value})"
    if isinstance(node, StringLiteral):
        return f"{pad}StringLiteral({node.value!r})"
    if isinstance(node, Identifier):
        return f"{pad}Identifier({node.name!r})"
    if isinstance(node, Program):
        lines = [f"{pad}Program"]
        for s in node.statements:
            lines.append(ast_to_string(s, indent + 1))
        return "\n".join(lines)
    if isinstance(node, Block):
        lines = [f"{pad}Block"]
        for s in node.statements:
            lines.append(ast_to_string(s, indent + 1))
        return "\n".join(lines)
    if isinstance(node, FuncDecl):
        params = ", ".join(node.params)
        lines = [f"{pad}FuncDecl(name={node.name!r}, params=[{params}])"]
        lines.append(ast_to_string(node.body, indent + 1))
        return "\n".join(lines)
    if isinstance(node, IfStmt):
        lines = [f"{pad}IfStmt"]
        lines.append(f"{pad}  condition:")
        lines.append(ast_to_string(node.condition, indent + 2))
        lines.append(f"{pad}  then:")
        lines.append(ast_to_string(node.then_block, indent + 2))
        if node.else_block is not None:
            lines.append(f"{pad}  else:")
            lines.append(ast_to_string(node.else_block, indent + 2))
        return "\n".join(lines)
    if isinstance(node, WhileStmt):
        lines = [f"{pad}WhileStmt"]
        lines.append(f"{pad}  condition:")
        lines.append(ast_to_string(node.condition, indent + 2))
        lines.append(f"{pad}  body:")
        lines.append(ast_to_string(node.body, indent + 2))
        return "\n".join(lines)
    if isinstance(node, ReturnStmt):
        if node.value is None:
            return f"{pad}ReturnStmt(no value)"
        lines = [f"{pad}ReturnStmt"]
        lines.append(ast_to_string(node.value, indent + 1))
        return "\n".join(lines)
    if isinstance(node, PrintStmt):
        lines = [f"{pad}PrintStmt"]
        lines.append(ast_to_string(node.value, indent + 1))
        return "\n".join(lines)
    if isinstance(node, Assignment):
        lines = [f"{pad}Assignment(name={node.name!r})"]
        lines.append(ast_to_string(node.value, indent + 1))
        return "\n".join(lines)
    if isinstance(node, ExprStmt):
        lines = [f"{pad}ExprStmt"]
        lines.append(ast_to_string(node.expr, indent + 1))
        return "\n".join(lines)
    if isinstance(node, BinaryOp):
        lines = [f"{pad}BinaryOp(op={node.op!r})"]
        lines.append(ast_to_string(node.left, indent + 1))
        lines.append(ast_to_string(node.right, indent + 1))
        return "\n".join(lines)
    if isinstance(node, UnaryOp):
        lines = [f"{pad}UnaryOp(op={node.op!r})"]
        lines.append(ast_to_string(node.operand, indent + 1))
        return "\n".join(lines)
    if isinstance(node, Call):
        lines = [f"{pad}Call(callee={node.callee!r})"]
        for arg in node.args:
            lines.append(ast_to_string(arg, indent + 1))
        return "\n".join(lines)
    return f"{pad}{type(node).__name__}(?)"
''')

# ══════════════════════════════════════════════════════════════════
# src/parser.py
# ══════════════════════════════════════════════════════════════════
write("src/parser.py", r'''# ── parser.py ──────────────────────────────────────────────────────────────
# Analizador sintáctico de CalcScript (descenso recursivo).

from dataclasses import dataclass
from lexer import Token
from tokens import TokenType
from ast_nodes import (
    Program, Block, FuncDecl, IfStmt, WhileStmt, ReturnStmt, PrintStmt,
    Assignment, ExprStmt, BinaryOp, UnaryOp, Call, IntLiteral,
    FloatLiteral, StringLiteral, Identifier,
)

class _ParseError(Exception):
    pass

@dataclass
class SyntaxError_:
    line: int
    column: int
    message: str
    def __str__(self):
        return f"Line {self.line}, Column {self.column}: {self.message}"

_STMT_KW = {"func", "if", "while", "return", "print"}

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errors: list[SyntaxError_] = []

    def parse(self) -> tuple[Program, list[SyntaxError_]]:
        stmts = []
        while not self._at_end():
            try:
                stmts.append(self._statement())
            except _ParseError:
                self._sync()
        return Program(statements=stmts), self.errors

    # ── statements ──
    def _statement(self):
        t = self._peek()
        if t.type == TokenType.KEYWORD:
            if t.value == "func":   return self._func_decl()
            if t.value == "if":     return self._if_stmt()
            if t.value == "while":  return self._while_stmt()
            if t.value == "return": return self._return_stmt()
            if t.value == "print":  return self._print_stmt()
        if t.type == TokenType.DELIMITER and t.value == "{":
            return self._block()
        nxt = self._peek_at(self.pos + 1)
        if (t.type == TokenType.IDENTIFIER and nxt
                and nxt.type == TokenType.OPERATOR and nxt.value == "="):
            return self._assignment()
        return self._expr_stmt()

    def _func_decl(self):
        self._eat_kw("func")
        name = self._expect(TokenType.IDENTIFIER, "expected function name").value
        self._expect_d("(", "expected '(' after function name")
        params = []
        if not self._chk_d(")"):
            params.append(self._expect(TokenType.IDENTIFIER, "expected param").value)
            while self._match_d(","):
                params.append(self._expect(TokenType.IDENTIFIER, "expected param").value)
        self._expect_d(")", "expected ')' after params")
        return FuncDecl(name=name, params=params, body=self._block())

    def _if_stmt(self):
        self._eat_kw("if")
        cond = self._expression()
        then = self._block()
        els = None
        if self._chk_kw("else"):
            self._advance()
            els = self._block()
        return IfStmt(condition=cond, then_block=then, else_block=els)

    def _while_stmt(self):
        self._eat_kw("while")
        cond = self._expression()
        return WhileStmt(condition=cond, body=self._block())

    def _return_stmt(self):
        self._eat_kw("return")
        val = None
        if not self._chk_d(";"):
            val = self._expression()
        self._expect_d(";", "expected ';' after return")
        return ReturnStmt(value=val)

    def _print_stmt(self):
        self._eat_kw("print")
        self._expect_d("(", "expected '(' after print")
        val = self._expression()
        self._expect_d(")", "expected ')' after print arg")
        self._expect_d(";", "expected ';' after print")
        return PrintStmt(value=val)

    def _assignment(self):
        name = self._expect(TokenType.IDENTIFIER, "expected identifier").value
        self._expect_op("=", "expected '='")
        val = self._expression()
        self._expect_d(";", "expected ';' after assignment")
        return Assignment(name=name, value=val)

    def _expr_stmt(self):
        expr = self._expression()
        self._expect_d(";", "expected ';' after expression")
        return ExprStmt(expr=expr)

    def _block(self):
        self._expect_d("{", "expected '{'")
        stmts = []
        while not self._chk_d("}") and not self._at_end():
            try:
                stmts.append(self._statement())
            except _ParseError:
                self._sync()
        self._expect_d("}", "expected '}'")
        return Block(statements=stmts)

    # ── expressions (precedence climbing) ──
    def _expression(self):
        return self._equality()

    def _equality(self):
        left = self._comparison()
        while self._chk_op("==") or self._chk_op("!="):
            op = self._advance().value
            left = BinaryOp(op=op, left=left, right=self._comparison())
        return left

    def _comparison(self):
        left = self._term()
        while (self._chk_op(">") or self._chk_op("<")
               or self._chk_op(">=") or self._chk_op("<=")):
            op = self._advance().value
            left = BinaryOp(op=op, left=left, right=self._term())
        return left

    def _term(self):
        left = self._factor()
        while self._chk_op("+") or self._chk_op("-"):
            op = self._advance().value
            left = BinaryOp(op=op, left=left, right=self._factor())
        return left

    def _factor(self):
        left = self._unary()
        while self._chk_op("*") or self._chk_op("/"):
            op = self._advance().value
            left = BinaryOp(op=op, left=left, right=self._unary())
        return left

    def _unary(self):
        if self._chk_op("-"):
            op = self._advance().value
            return UnaryOp(op=op, operand=self._unary())
        return self._call()

    def _call(self):
        expr = self._primary()
        if isinstance(expr, Identifier) and self._chk_d("("):
            self._advance()
            args = []
            if not self._chk_d(")"):
                args.append(self._expression())
                while self._match_d(","):
                    args.append(self._expression())
            self._expect_d(")", "expected ')' after call args")
            return Call(callee=expr.name, args=args)
        return expr

    def _primary(self):
        t = self._peek()
        if t.type == TokenType.NUMBER_INT:
            self._advance(); return IntLiteral(value=int(t.value))
        if t.type == TokenType.NUMBER_FLOAT:
            self._advance(); return FloatLiteral(value=float(t.value))
        if t.type == TokenType.STRING:
            self._advance(); return StringLiteral(value=t.value[1:-1])
        if t.type == TokenType.IDENTIFIER:
            self._advance(); return Identifier(name=t.value)
        if t.type == TokenType.DELIMITER and t.value == "(":
            self._advance()
            inner = self._expression()
            self._expect_d(")", "expected ')' after expression")
            return inner
        raise self._error(t, f"expected expression, got '{t.value}'")

    # ── helpers ──
    def _peek(self):
        if self.pos < len(self.tokens): return self.tokens[self.pos]
        ln = self.tokens[-1].line if self.tokens else 1
        return Token(index=-1, type=TokenType.EOF, value="<eof>", line=ln, column=0)

    def _peek_at(self, i):
        return self.tokens[i] if 0 <= i < len(self.tokens) else None

    def _at_end(self): return self.pos >= len(self.tokens)

    def _advance(self):
        t = self._peek()
        if not self._at_end(): self.pos += 1
        return t

    def _chk_d(self, v): t = self._peek(); return t.type == TokenType.DELIMITER and t.value == v
    def _chk_op(self, v): t = self._peek(); return t.type == TokenType.OPERATOR and t.value == v
    def _chk_kw(self, v): t = self._peek(); return t.type == TokenType.KEYWORD and t.value == v
    def _match_d(self, v):
        if self._chk_d(v): self._advance(); return True
        return False

    def _expect(self, tt, msg):
        if self._peek().type == tt: return self._advance()
        raise self._error(self._peek(), msg)
    def _expect_d(self, v, msg):
        if self._chk_d(v): return self._advance()
        raise self._error(self._peek(), msg)
    def _expect_op(self, v, msg):
        if self._chk_op(v): return self._advance()
        raise self._error(self._peek(), msg)
    def _eat_kw(self, v):
        if self._chk_kw(v): return self._advance()
        raise self._error(self._peek(), f"expected '{v}'")

    def _error(self, t, msg):
        self.errors.append(SyntaxError_(line=t.line, column=t.column, message=msg))
        return _ParseError()

    def _sync(self):
        while not self._at_end():
            t = self._peek()
            if t.type == TokenType.DELIMITER and t.value == ";":
                self._advance(); return
            if t.type == TokenType.KEYWORD and t.value in _STMT_KW:
                return
            self._advance()
''')

# ══════════════════════════════════════════════════════════════════
# src/main.py  (VERSIÓN NUEVA CON PARSER + AST)
# ══════════════════════════════════════════════════════════════════
write("src/main.py", r'''# ── main.py ────────────────────────────────────────────────────────────────
# Punto de entrada de CalcScript.
# Uso: python main.py <archivo.csc>
# Pipeline: lectura → lexer → parser → imprime tokens + AST + errores

import sys
from lexer import Lexer
from parser import Parser
from ast_nodes import ast_to_string


def main() -> None:
    if len(sys.argv) != 2:
        print("Uso: python main.py <archivo.csc>")
        sys.exit(1)

    source_path = sys.argv[1]
    try:
        with open(source_path, encoding="utf-8") as fh:
            source = fh.read()
    except FileNotFoundError:
        print(f"Error: no se encontró el archivo '{source_path}'")
        sys.exit(1)

    # Fase 1: análisis léxico
    lexer = Lexer(source)
    tokens, lex_errors = lexer.tokenize()

    print()
    print("Token List:")
    for tok in tokens:
        print(f"  {tok}")

    # Fase 2: análisis sintáctico
    parser = Parser(tokens)
    ast, syntax_errors = parser.parse()

    print()
    print("AST (Abstract Syntax Tree):")
    print(ast_to_string(ast, indent=1))

    print()
    if lex_errors:
        print("Lexical Error List:")
        for err in lex_errors:
            print(f"  {err}")
    else:
        print("No lexical errors found.")

    print()
    if syntax_errors:
        print("Syntax Error List:")
        for err in syntax_errors:
            print(f"  {err}")
    else:
        print("No syntax errors found.")


if __name__ == "__main__":
    main()
''')

# ══════════════════════════════════════════════════════════════════
# Tests
# ══════════════════════════════════════════════════════════════════
write("tests/valid/factorial.csc",
"""func factorial(n) {
    result = 1;
    while n > 1 {
        result = result * n;
        n = n - 1;
    }
    return result;
}

x = factorial(5);
print(x);
""")

write("tests/valid/condicional.csc",
"""a = 3.14;
b = 2.0;

if a > b {
    diff = a - b;
    print(diff);
} else {
    print(b);
}
""")

write("tests/valid/aritmetica.csc",
"""total = (10 + 5) * 2 / 3;
print(total);
""")

write("tests/invalid/errores_simbolos.csc",
"""x = 10 $ 2;
y = @total + 1;
z = x != y;
print(z);
""")

write("tests/invalid/errores_mixtos.csc",
"""123abc = 5;
result = 3. + 2;
x = total # suma parcial
print(x);
""")

write("tests/invalid/errores_sintaxis.csc",
"""x = 5
y = (10 + 2;
if x > y {
    print(x);
""")

# Limpiar __pycache__
import shutil
if os.path.exists("src/__pycache__"):
    shutil.rmtree("src/__pycache__")
    print("  ✓ src/__pycache__/ eliminado")

print("\n¡Listo! Ahora corre:")
print("  python src/main.py tests/valid/factorial.csc")
