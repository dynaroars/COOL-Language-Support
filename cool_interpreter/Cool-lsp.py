##################### ##################### ###############
#                 COOL INTERPRETOR IN PY
# Author: Li Linhan
# Date:   7/10/2021
# Dependency:
#       numpy(Int32)
#       PLY 
# Known issue: 
#       check parser and interpreter for details.
##################### ##################### ###############
import argparse
import os
from sys import argv
from functools import reduce
from io import StringIO

from utils.env import Cool_value
from Lexer.lexer import get_toks_stream
from Parser.parser import get_ast_stream
from Typechecker.typechecker import get_type_checked_ast
from Interpreter.interpreter import evaluate_cl_type



stages = [  get_toks_stream,
            get_ast_stream,
            get_type_checked_ast,
            evaluate_cl_type
            ]
file_ext= [ "",
            ".cl-lex",
            ".cl-ast",
            ".cl-type"
            ]

inStream = sys.stdin
outStream= reduce(  lambda val, ele : ele(val), 
                    stages[0:3],
                    inStream 
                    )
