# ── main.py ────────────────────────────────────────────────────────────────
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
