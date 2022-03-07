##################### ##################### ###############
#                 COOL LEXER IN PY
# Author: Li Linhan
# Date:   5/22/2021
# Dependency:
#     PLY (Python Lex-Yacc) 
# Known issue: 
#       - None
##################### ##################### ###############

import ply.lex as lex
from io import StringIO
from sys import exit

MAX_INT_32 = 2147483647
KEY_WORDS_HASH = {
    "@":"at",       "case":"case",      "class":"class",        ",":"comma",
    ":":"colon",    "/":"divide",       ".":"dot",              "else":"else",
    "=":"equals",   "esac":"esac",      "false":"false",        "fi":"fi",
    "if":"if",      "in":"in",          "inherits":"inherits",  "isvoid":"isvoid",
    "<-":"larrow",  "{":"lbrace",       "<=":"le",              "let":"let",
    "loop":"loop",  "(":"lparen",       "<":"lt",               "-":"minus",
    "new":"new",    "not":"not",        "of":"of",              "+":"plus",
    "pool":"pool",  "=>":"rarrow",      "}":"rbrace",           ")":"rparen",
    ";":"semi",     "then":"then",      "~":"tilde",            "*":"times",
    "true":"true",  "while":"while"
}

tokens = (
    "KEY_WORDS",
    "IDENTIFIER",
    "TYPE",
    "INTEGER",
    "STRING",
    "COMMENT",
    "SPACE"
)

states = (
    ("single", "exclusive"),
    ("multi" , "exclusive")
)

#####################  STATE: single   ####################
#  rules for comment --                                   #
##################### ##################### ###############
def t_single_COMMENT(t):
    r"""
    \n|
    .
    """
    if t.value == "\n":
        t.lexer.lineno += 1
        t.lexer.pop_state()

def t_single_eof(t):
    t.lexer.pop_state()

def t_single_error(t):
    print("ERROR: %d: Lexer: error in single line comment" % (t.lexer.lineno))
####################  END    ############## ###############


#####################  STATE: multi   #####################
#  rules for comment (* *)                                #
##################### ##################### ###############
def t_multi_COMMENT(t):
    r"""
    \(\*|
    \*\)|
    [\s\S]
    """
    if t.value == "\n":
        t.lexer.lineno += t.value.count("\n")
    elif t.value == "(*":
        t.lexer.push_state("multi")
    elif t.value == "*)":
        t.lexer.pop_state()

def t_multi_eof(t):
    t.lexer.pop_state()
    print("ERROR: %d: Lexer: EOF in (* comment *)" % (t.lexer.lineno))
    exit(0)

def t_multi_error(t):
    print("ERROR: %d: Lexer: invalid character in (* comment *) %s" % (t.lexer.lineno, t.value[0]))
####################  END    ############## ###############


#####################   Entry state   #####################
#  lexer state with this inital state                     #
##################### ##################### ###############
def t_STRING(t):
    r"""
    \"(\\.|[^\"])*?\"
    """
    str_in = t.value[1:-1]
    buffer = StringIO()
    idx = 0

    while(idx < len(str_in)):
        ptr = str_in[idx]
        if ptr in ['\n', '\0']:
            print("ERROR: %d: Lexer: invalid character in  string: %s" % (t.lexer.lineno, ptr))
            exit(0)
        else:
            buffer.write(ptr)
        idx += 1
    buffer = buffer.getvalue()
    if len(buffer) > 1024:
        print("ERROR: %d: Lexer: string constant is too long (%d > 1024) " % (t.lexer.lineno, len(str_in)))
        exit(0)
    t.value = buffer
    t.line = t.lexer.lineno
    return t

def t_COMMENT(t):
    r"""
    --|
    \(\*
    """
    # enter a state by pushing into the state stack
    if t.value == "--":
        t.lexer.push_state("single")
    elif t.value == "(*":
        t.lexer.push_state("multi")

def t_SPACE(t):
    r"""
    [
    \n|
    \r|
    \f|
    \t|
    \v|

    ]
    """
    if t.value == "\n":
        t.lexer.lineno += 1
    t.line = t.lexer.lineno
    return t

def t_KEY_WORDS(t):
    # though it is called key words, it also matches TYPEs and IDENTIFIERs
    r"""
    [a-z][a-zA-Z0-9_]*|
    [A-Z]\w*|
    @|
    [Cc][Aa][Ss][Ee]|
    [Cc][Ll][Aa][Ss][Ss]|
    ,|
    :|
    /|
    \.|
    [Ee][Ll][Ss][Ee]|
    <=|
    =>|
    [Ee][Ss][Aa][Cc]|
    [Ff][Ii]|
    [Ii][Ff]|
    [Ii][Nn][Hh][Ee][Rr][Ii][Tt][Ss]|
    [Ii][Nn]|
    [Ii][Ss][Vv][Oo][Ii][Dd]|
    <-|
    {|
    [Ll][Ee][Tt]|
    [Ll][Oo][Oo][Pp]|
    [/(]|
    <|
    -|
    [Nn][Ee][Ww]|
    [Nn][Oo][Tt]|
    [Oo][Ff]|
    \+|
    [Pp][Oo][Oo][Ll]|
    =|
    }|
    [/)]|
    ;|
    [Tt][Hh][Ee][Nn]|
    ~|
    \*|
    [Ww][Hh][Ii][Ll][Ee]|
    t[Rr][Uu][Ee]|
    f[Aa][Ll][Ss][Ee]
    """
    lower_case_str = str.lower(t.value)

    t.line = t.lexer.lineno
    if lower_case_str in {"false", "true"} and str.isupper(t.value[0]):
        t.type = "TYPE"
        return t

    if lower_case_str in KEY_WORDS_HASH:
        t.type = "KEY_WORDS"
        t.value = lower_case_str
    else:
        if str.isupper(t.value[0]):
            t.type = "TYPE"
        else:
            t.type = "IDENTIFIER"


    return t


def t_INTEGER(t):
    r"\d+"
    int_value = int(t.value)
    if int_value > MAX_INT_32:
        print("ERROR: %d: Lexer: not a non-negative 32-bit signed integer: %s" % (t.lexer.lineno, t.value))
        exit(0)
    t.value = str(int_value)
    t.line = t.lexer.lineno
    return t

def t_error(t):
    print("ERROR: %d: Lexer: invalid character: %s" % (t.lexer.lineno, t.value[0]))

####################  END   OF RULES   ############## ###############
####################  END   OF RULES   ############## ###############

def get_toks_stream(inStream):
    lex.lex()
    lex.input(inStream.read())
    out_buffer = StringIO()
    for tok in iter(lex.token, None):
        if      tok.type == "COMMENT":
            pass
        elif    tok.type == "TYPE":
            out_buffer.write(str(tok.line))
            out_buffer.write('\n')

            out_buffer.write("type")
            out_buffer.write('\n')

            out_buffer.write(tok.value)
            out_buffer.write('\n')

        elif    tok.type == "IDENTIFIER":
            out_buffer.write(str(tok.line))
            out_buffer.write('\n')

            out_buffer.write("identifier")
            out_buffer.write('\n')

            out_buffer.write(tok.value)
            out_buffer.write('\n')

        elif    tok.type == "STRING":
            out_buffer.write(str(tok.line))
            out_buffer.write('\n')

            out_buffer.write("string")
            out_buffer.write('\n')

            out_buffer.write(tok.value)
            out_buffer.write('\n')

        elif    tok.type == "INTEGER":
            out_buffer.write(str(tok.line))
            out_buffer.write('\n')

            out_buffer.write("integer")
            out_buffer.write('\n')

            out_buffer.write(tok.value)
            out_buffer.write('\n')

        elif    tok.type == "SPACE":
            pass
        elif    tok.type == "KEY_WORDS":
            out_buffer.write(str(tok.line))
            out_buffer.write('\n')

            out_buffer.write(KEY_WORDS_HASH[tok.value])
            out_buffer.write('\n')
    out_buffer.seek(0)
    return out_buffer


if __name__ == '__main__':
    import sys
    fin = open(sys.argv[1], "r")
    out_buffer = get_toks_stream(fin)
    fin.close()

    f = open(sys.argv[1]+"-lex", "w")
    f.write(out_buffer.getvalue())
    f.close()
