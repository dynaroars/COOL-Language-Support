# COOL-Compiler-In-Py
Another COOL compiler impelmented in Py

Cool-compiler.py is the complete compiler.

Cool-lsp.py is for the COOL language server. (take input from stdin)
## Usage:
```
usage:
        cool [options] source.{cl,cl-lex,cl-parse,cl-type}

  --lex         stop after lexing (produce source.cl-lex file)
  --parse       stop after parsing (produce source.cl-ast file)
  --type        stop after type checking (produce source.cl-type file)
  --class-map   stop after type checking (produce source.cl-type class map file)
  --imp-map     stop after type checking (produce source.cl-type imp map file)
  --parent-map  stop after type checking (produce source.cl-type parent map file)
```
