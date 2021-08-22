# COOL Language Support

## Overview
This extension aims to make COOL more accessible to those who are learning it, leverage the burden of repeated manual works.

It provides support for COOL(Classroom Object Oriented Language), a programming language designed by [Alexander Aiken](http://theory.stanford.edu/~aiken/) at Stanford. 




## Features:

- ### Static error checking
 This extension is connected with a COOL compiler backend that validates your program in real-time. 
 Whenever a lexical/syntax/typing error is made, an error message will be displayed. 
 ![alt-text](https://raw.githubusercontent.com/unsat/COOL-Language-Support/main/GIFs/error_message.gif)

- ### Auto-Completion
 This extension also provides auto-completion support based on lexical analysis and code snippets.
 Semantic-based autocomplete is under development and will be added in the future.
 ![alt-text](https://raw.githubusercontent.com/unsat/COOL-Language-Support/main/GIFs/COOL_snippet.gif)

## Note
 - This extension is built based on the lsp-sample by Microsoft. For details, check "https://github.com/microsoft/vscode-extension-samples/tree/main/lsp-sample"
 - The COOL interpreter submodule used in this extension "https://github.com/unsat/COOL-Compiler-In-Py"

