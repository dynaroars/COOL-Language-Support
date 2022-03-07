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



arg_parser = argparse.ArgumentParser(description="Cool Interpretor")
arg_parser.add_argument("input_file", type=str, nargs=1,
                        help="path of the input file")
arg_parser.add_argument("--lex", action="store_true",
                        help="emit cl-lex file(tokenized input)")
arg_parser.add_argument("--parse", action="store_true",
                        help="emit cl-ast file(cool abstract syntax tree)")
arg_parser.add_argument("--type", action="store_true",
                        help="emit cl-type file(type checked ast)")

args = arg_parser.parse_args()
fname, fext = os.path.splitext(args.input_file[0])

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


if fext == ".cl":
    s = 0
elif fext == ".cl-lex":
    s = 1
elif fext == ".cl-ast":
    s = 2
elif fext == ".cl-type":
    s = 3
else:
    raise Exception("Unknown File type")

if args.lex:
    e = 1
elif args.parse:
    e = 2
elif args.type:
    e = 3
else:
    e = 4

inStream = open(args.input_file[0], "r")
outStream= reduce(  lambda val, ele : ele(val), 
                    stages[s:e],
                    inStream 
                    )
inStream.close()

if inStream is outStream:
    pass
elif isinstance(outStream, StringIO):
    fout = open( fname + file_ext[e], "w+")
    fout.write( outStream.getvalue() )
    fout.close()
elif isinstance(outStream, Cool_value):
    print("Program exited with value: %s" % outStream)
    pass
else:
    raise Exception("sth wrong...")