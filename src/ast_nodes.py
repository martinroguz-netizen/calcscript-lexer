# ── ast_nodes.py ───────────────────────────────────────────────────────────
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
