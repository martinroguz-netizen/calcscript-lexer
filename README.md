# CalcScript — Analizador Léxico y Sintáctico

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
