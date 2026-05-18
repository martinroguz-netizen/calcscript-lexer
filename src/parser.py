# ── parser.py ──────────────────────────────────────────────────────────────
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
