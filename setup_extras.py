"""Crea los archivos que faltan en el repo. Corre desde la raíz del proyecto."""
import os
def write(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✓ {path}")

print("Creando archivos extras...\n")

write("README.md", """# CalcScript — Analizador Léxico y Sintáctico

Analizador léxico y sintáctico para **CalcScript**, un lenguaje imperativo
educativo orientado a cálculos aritméticos, variables, estructuras de control
(`if`/`else`, `while`) y funciones.

El lexer tokeniza archivos `.csc` y el parser genera un **Árbol de Sintaxis
Abstracta (AST)** como representación intermedia. Implementado en Python 3.12
puro, sin dependencias externas.

---

## Información del Curso

- **Materia:** Programación de Sistemas Base 1
- **Institución:** Universidad Autónoma de Tamaulipas
- **Semestre:** 2026-1
- **Profesor:** Muñoz Quintero Dante Adolfo

## Integrantes

| Nombre | Matrícula |
| --- | --- |
| Romero Guzmán Martín Gastón | … |
| Mar Saucedo Duilio Alessandro | … |

---

## Cómo ejecutar

Requisitos: Python 3.12+. Sin dependencias externas.

```bash
git clone https://github.com/martinroguz-netizen/calcscript-lexer.git
cd calcscript-lexer
python src/main.py tests/valid/factorial.csc
python src/main.py tests/valid/condicional.csc
python src/main.py tests/valid/aritmetica.csc
python src/main.py tests/invalid/errores_simbolos.csc
python src/main.py tests/invalid/errores_sintaxis.csc
python src/main.py tests/invalid/errores_mixtos.csc
```

Cada ejecución imprime: lista de tokens, AST, errores léxicos y errores sintácticos.

Si `python` no funciona, usar `python3` (Mac/Linux) o `py` (Windows).

---

## Tokens Reconocidos

| Categoría | Ejemplos |
| --- | --- |
| KEYWORD | `if`, `else`, `while`, `func`, `return`, `print` |
| IDENTIFIER | `x`, `total`, `my_var` |
| NUMBER_INT | `0`, `42`, `1024` |
| NUMBER_FLOAT | `3.14`, `0.5`, `2.0` |
| OPERATOR | `+ - * / = > < >= <= == !=` |
| DELIMITER | `; , ( ) { }` |
| STRING | `"hola"` |
| COMMENT | `# texto` (descartado) |

---

## Estructura del Proyecto

```
calcscript-lexer/
├── README.md
├── .gitignore
├── LICENSE
├── src/
│   ├── main.py          # pipeline lexer → parser
│   ├── lexer.py         # analizador léxico
│   ├── tokens.py        # tipos de token
│   ├── rules.py         # expresiones regulares
│   ├── parser.py        # analizador sintáctico (descenso recursivo)
│   └── ast_nodes.py     # nodos del AST
├── grammar/
│   └── calcscript.txt   # gramática EBNF
├── tests/
│   ├── valid/
│   └── invalid/
├── docs/
│   ├── entregable_final.pdf
│   └── diagrama_automata.png
└── capturas/
```

## Licencia

MIT
""")

write(".gitignore", """__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
.idea/
.vscode/
.DS_Store
*.log
""")

write("LICENSE", """MIT License

Copyright (c) 2026 Romero Guzmán M.G. & Mar Saucedo D.A. — UAT

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
""")

write("grammar/calcscript.txt", """CalcScript — Gramática del lenguaje (EBNF)
==========================================

GRAMÁTICA LÉXICA (implementada en src/rules.py):

  identifier    = ( letra | "_" ) { letra | dígito | "_" }
  keyword       = "if" | "else" | "while" | "func" | "return" | "print"
  number_int    = dígito { dígito }
  number_float  = dígito { dígito } "." dígito { dígito }
  string        = '"' { cualquier_char_excepto_comilla } '"'
  operator      = "+" | "-" | "*" | "/" | "=" | ">" | "<" | ">=" | "<=" | "==" | "!="
  delimiter     = ";" | "," | "(" | ")" | "{" | "}"
  comment       = "#" { cualquier_char } newline
  whitespace    = " " | "\\t" | "\\r"

  Orden de evaluación: whitespace → comment → number_float → number_int
    → string → identifier → operator(2ch) → operator(1ch) → delimiter → error

GRAMÁTICA SINTÁCTICA (implementada en src/parser.py):

  program     = { statement }
  statement   = funcDecl | ifStmt | whileStmt | returnStmt
              | printStmt | block | assignment | exprStmt
  funcDecl    = "func" IDENT "(" [paramList] ")" block
  ifStmt      = "if" expression block [ "else" block ]
  whileStmt   = "while" expression block
  returnStmt  = "return" [ expression ] ";"
  printStmt   = "print" "(" expression ")" ";"
  assignment  = IDENT "=" expression ";"
  exprStmt    = expression ";"
  block       = "{" { statement } "}"

  expression  = equality
  equality    = comparison { ("==" | "!=") comparison }
  comparison  = term { (">" | "<" | ">=" | "<=") term }
  term        = factor { ("+" | "-") factor }
  factor      = unary { ("*" | "/") unary }
  unary       = "-" unary | call
  call        = primary [ "(" [argList] ")" ]
  primary     = NUMBER_INT | NUMBER_FLOAT | STRING | IDENT | "(" expression ")"

  Precedencia (menor a mayor): == != < > <= >= < + - < * / < unario < llamada
  Recuperación de errores: sincronización a ";" o keyword de inicio de sentencia
""")

os.makedirs("docs", exist_ok=True)
os.makedirs("capturas", exist_ok=True)

print("\n¡Listo! Ahora pon el PDF y el diagrama en docs/")
print("Luego corre:")
write("capturas/README.txt", """Capturas de pantalla de la ejecución del proyecto.
Ver docs/entregable_final.pdf para las capturas integradas.
""")

print("\n¡Listo! Ahora pon el PDF y el diagrama en docs/")
print("Después corre:")
print("  git add .")
print('  git commit -m "Agregar README, docs y gramática"')
print("  git push")
