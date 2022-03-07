##################### ##################### ###############
#                 COOL PARSER IN PY
# Author: Li Linhan
# Date:   5/31/2021
# Dependency:
#     PLY (Python Lex-Yacc) 
# Known issue: 
#       - Might have some issue with some white-space 
#       character that works differently in UNIX/Windows
##################### ##################### ###############

from io import StringIO
import ply.yacc as yacc
from ply.lex import LexToken
from sys import exit

# Defines terminals
tokens = (
    "IDENTIFIER",       "TYPE",     "INTEGER",      "STRING",       "AT",
    "CASE",             "CLASS",    "COMMA",        "COLON",        "DIVIDE",
    "DOT",              "ELSE",     "EQUALS",       "ESAC",         "FALSE",
    "FI",               "IF",       "IN",           "INHERITS",     "ISVOID",
    "LARROW",           "LBRACE",   "LE",           "LET",          "LOOP",
    "LPAREN",           "LT",       "MINUS",        "NEW",          "NOT",
    "OF",               "PLUS",     "POOL",         "RARROW",       "RBRACE",
    "RPAREN",           "SEMI",     "THEN",         "TILDE",        "TIMES",
    "TRUE",             "WHILE"
)

precedence = (
    ("left", "LARROW"),
    ("left", "NOT"),
    ("nonassoc", "LE", "LT", "EQUALS"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
    ("left", "ISVOID"),
    ("left", "TILDE"),
    ("left", "AT"),
    ("left", "DOT"),
)

# The first rule is used as entry point by default
def p_cool_prog(p):
    '''
    cool_prog   : cool_class SEMI cool_prog
                |
    '''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[1]] + p[3]

def p_cool_class(p):
    '''
    cool_class  : CLASS TYPE INHERITS TYPE LBRACE feature_list RBRACE
                | CLASS TYPE LBRACE feature_list RBRACE
    '''
    if len(p) == 8:
        p[0] = ("inherits", (p[2],p.lineno(2)), (p[4],p.lineno(4)), p[6])
    else:
        p[0] = ("no_inherits", (p[2],p.lineno(2)), None, p[4])

def p_feature_list(p):
    '''
    feature_list : feature SEMI feature_list
                 |
    '''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[1]] + p[3]

def p_feature_method(p):
    '''
    feature : IDENTIFIER LPAREN formal_list RPAREN COLON TYPE LBRACE expression RBRACE
    '''
    p[0] = ("method", (p[1],p.lineno(1)), p[3], (p[6],p.lineno(6)), p[8])

def p_feature_attri_init(p):
    '''
    feature : IDENTIFIER COLON TYPE LARROW expression
    '''
    p[0] = ("attribute_init", (p[1],p.lineno(1)), (p[3],p.lineno(3)), p[5])

def p_feature_attri_no_init(p):
    '''
    feature : IDENTIFIER COLON TYPE
    '''
    p[0] = ("attribute_no_init", (p[1],p.lineno(1)), (p[3],p.lineno(3)))

def p_formal_list(p):
    '''
    formal_list : formal formal_tail
                |
    '''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[1]] + p[2]

def p_formal_tail(p):
    '''
    formal_tail : COMMA formal formal_tail
                |
    '''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[2]] + p[3]

def p_formal(p):
    '''
    formal : IDENTIFIER COLON TYPE
    '''
    p[0] = ((p[1],p.lineno(1)), (p[3],p.lineno(3)))

##################################################
##  Expression are represented as below
##  (expr_type, arg1, arg2....., expr_line_number)
##################################################
def p_expression_assign(p):
    '''
    expression : IDENTIFIER LARROW expression
    '''
    p[0] = ("assign", (p[1],p.lineno(1)), p[3], p.lineno(1))

def p_expression_static_dispatch(p):
    '''
    expression : expression AT TYPE DOT IDENTIFIER LPAREN arg_list RPAREN
    '''
    p[0] = ("static_dispatch", p[1], (p[3],p.lineno(3)), (p[5],p.lineno(5)), p[7], p[1][-1])

def p_expression_dynamic_dispatch(p):
    '''
    expression : expression DOT IDENTIFIER LPAREN arg_list RPAREN
    '''
    p[0] = ("dynamic_dispatch", p[1], (p[3],p.lineno(3)), p[5], p[1][-1])

def p_expression_self_dispatch(p):
    '''
    expression : IDENTIFIER LPAREN arg_list RPAREN
    '''
    p[0] = ("self_dispatch", (p[1],p.lineno(1)), p[3], p.lineno(1))

def p_expression_if(p):
    '''
    expression : IF expression THEN expression ELSE expression FI
    '''
    p[0] = ("if", p[2], p[4], p[6], p.lineno(1))

def p_expression_while(p):
    '''
    expression : WHILE expression LOOP expression POOL
    '''
    p[0] = ("while", p[2], p[4], p.lineno(1))

def p_expression_block(p):
    '''
    expression  : LBRACE block RBRACE
    '''
    p[0] = ("block", p[2], p.lineno(1))

def p_expression_let(p):
    '''
    expression : LET binding_list IN expression
    '''
    p[0] = ("let", p[2], p[4], p.lineno(1))

def p_expression_case(p):
    '''
    expression : CASE expression OF case_list ESAC
    '''
    p[0] = ("case", p[2], p[4], p.lineno(1))

def p_expression_new(p):
    '''
    expression : NEW TYPE
    '''
    p[0] = ("new", (p[2],p.lineno(2)), p.lineno(1))

def p_expression_isvoid(p):
    '''
    expression : ISVOID expression
    '''
    p[0] = ("isvoid", p[2], p.lineno(1))

def p_expression_arith(p):
    '''
    expression  : expression PLUS expression
                | expression MINUS expression
                | expression TIMES expression
                | expression DIVIDE expression
    '''
    p[0] = (p[2], p[1], p[3], p[1][-1])

def p_expression_negate(p):
    '''
    expression : TILDE expression
    '''
    p[0] = ("negate", p[2], p.lineno(1))

def p_expression_lt(p):
    '''
    expression : expression LT expression
    '''
    p[0] = ("lt", p[1], p[3], p[1][-1])

def p_expression_LE(p):
    '''
    expression : expression LE expression
    '''
    p[0] = ("le", p[1], p[3], p[1][-1])

def p_expression_eqals(p):
    '''
    expression : expression EQUALS expression
    '''
    p[0] = ("eq", p[1], p[3], p[1][-1])

def p_expression_not(p):
    '''
    expression : NOT expression
    '''
    p[0] = ("not", p[2], p.lineno(1))

def p_expression_paran(p):
    '''
    expression : LPAREN expression RPAREN
    '''
    # the last element of the tuple is the line number
    # so here we just change the lineno of the inner expression to the lineno of LPAREN
    p[0] = p[2][:-1] + (p.lineno(1),)

def p_expression_id(p):
    '''
    expression : IDENTIFIER
    '''
    p[0] = ("identifier", (p[1],p.lineno(1)), p.lineno(1))

def p_expression_int(p):
    '''
    expression : INTEGER
    '''
    p[0] = ("integer", p[1], p.lineno(1))

def p_expression_str(p):
    '''
    expression : STRING
    '''
    p[0] = ("string", p[1], p.lineno(1))

def p_expression_true(p):
    '''
    expression : TRUE
    '''
    p[0] = ("true", p.lineno(1))

def p_expression_false(p):
    '''
    expression : FALSE
    '''
    p[0] = ("false", p.lineno(1))

def p_arg_list(p):
    '''
    arg_list : expression arg_list_tail
             |
    '''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[1]] + p[2]

def p_arg_list_tail(p):
    '''
    arg_list_tail : COMMA expression arg_list_tail
                  |
    '''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[2]] + p[3]

def p_block(p):
    '''
    block : expression SEMI block
          |
    '''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[1]] + p[3]

def p_binding_list(p):
    '''
    binding_list : binding binding_list_tail
    '''
    p[0] = [p[1]] + p[2]

def p_binding_list_tail(p):
    '''
    binding_list_tail : COMMA binding binding_list_tail
                      |
    '''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[2]] + p[3]

def p_binding(p):
    '''
    binding : IDENTIFIER COLON TYPE LARROW expression
            | IDENTIFIER COLON TYPE
    '''
    if len(p) == 4:
        p[0] = ("let_binding_no_init", (p[1],p.lineno(1)), (p[3],p.lineno(3)))
    else:
        p[0] = ("let_binding_init", (p[1],p.lineno(1)), (p[3],p.lineno(3)), p[5])

def p_case_list(p):
    '''
    case_list : case_element
              | case_element case_list
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_case_element(p):
    '''
    case_element : IDENTIFIER COLON TYPE RARROW expression SEMI
    '''
    p[0] = ((p[1],p.lineno(1)), (p[3],p.lineno(3)), p[5])

# Error rule for syntax errors
def p_error(p):
    SYMBOLS = {
        "at":"@",       "comma":",",        "rparen":")",
        "colon":":",    "divide":"/",       "dot":".",
        "larrow":"<-",  "lbrace":"{",       "le":"<=",
        "lparen":"(",   "lt":"<",           "minus":"-",
        "plus":"+",     "rarrow":"=>",      "rbrace":"}",
        "semi":";",     "tilde":"~",        "times":"*",
        "equals":"="
    }
    token_value = SYMBOLS[p.value] if p.value in SYMBOLS else p.value
    print("ERROR: %s: Parser: syntax error near %s" % (p.lineno, token_value) )
    exit(1)

# Build the parser
parser = yacc.yacc()

########################   Parser rules ends       ############################
########################   Parser rules ends       ############################
########################   Parser rules ends       ############################

class AST_Printer():
    def __init__(self, ast):
        self.out_buffer = StringIO()
        self.print_lst(self.print_class, ast)

    def get_buff(self):
        self.out_buffer.seek(0)
        return self.out_buffer

    def print_lst(self, func, lst):
        self.out_buffer.write(str(len(lst)))
        self.out_buffer.write("\n")
        for item in lst:
            func(item)

    def print_id(self, i):
        self.out_buffer.write(str(i[-1]))
        self.out_buffer.write("\n")
        self.out_buffer.write(i[0])
        self.out_buffer.write("\n")

    def print_formal(self, f):
        self.print_id(f[0])
        self.print_id(f[1])

    def print_feature(self, f):
        if f[0] == "method":
            self.out_buffer.write(f[0])
            self.out_buffer.write("\n")
            self.print_id(f[1])
            self.print_lst(self.print_formal, f[2])
            self.print_id(f[3])
            self.print_expr(f[4])
        elif f[0] == "attribute_init":
            self.out_buffer.write(f[0])
            self.out_buffer.write("\n")
            self.print_id(f[1])
            self.print_id(f[2])
            self.print_expr(f[3])
        elif f[0] == "attribute_no_init":
            self.out_buffer.write(f[0])
            self.out_buffer.write("\n")
            self.print_id(f[1])
            self.print_id(f[2])

    def print_binding(self, b):
        if b[0] == "let_binding_no_init":
            self.out_buffer.write(b[0])
            self.out_buffer.write("\n")
            self.print_id(b[1])
            self.print_id(b[2])
        elif b[0] == "let_binding_init":
            self.out_buffer.write(b[0])
            self.out_buffer.write("\n")
            self.print_id(b[1])
            self.print_id(b[2])
            self.print_expr(b[3])

    def print_case(self, c):
        self.print_id(c[0])
        self.print_id(c[1])
        self.print_expr(c[2])

    def print_expr(self, e):
        self.out_buffer.write(str(e[-1]))
        self.out_buffer.write("\n")
        self.out_buffer.write(e[0])
        self.out_buffer.write("\n")
        if e[0] == "assign":
            self.print_id(e[1])
            self.print_expr(e[2])
        elif e[0] == "static_dispatch":
            self.print_expr(e[1])
            self.print_id(e[2])
            self.print_id(e[3])
            self.print_lst(self.print_expr, e[4])
        elif e[0] == "dynamic_dispatch":
            self.print_expr(e[1])
            self.print_id(e[2])
            self.print_lst(self.print_expr, e[3])
        elif e[0] == "self_dispatch":
            self.print_id(e[1])
            self.print_lst(self.print_expr, e[2])
        elif e[0] == "if":
            self.print_expr(e[1])
            self.print_expr(e[2])
            self.print_expr(e[3])
        elif e[0] == "while":
            self.print_expr(e[1])
            self.print_expr(e[2])
        elif e[0] == "block":
            self.print_lst(self.print_expr, e[1])
        elif e[0] == "let":
            self.print_lst(self.print_binding, e[1])
            self.print_expr(e[2])
        elif e[0] == "case":
            self.print_expr(e[1])
            self.print_lst(self.print_case, e[2])
        elif e[0] == "new":
            self.print_id(e[1])
        elif e[0] == "isvoid":
            self.print_expr(e[1])
        elif e[0] in ["plus","minus","times","divide"]:
            self.print_expr(e[1])
            self.print_expr(e[2])
        elif e[0] == "negate":
            self.print_expr(e[1])
        elif e[0] == "lt":
            self.print_expr(e[1])
            self.print_expr(e[2])
        elif e[0] == "le":
            self.print_expr(e[1])
            self.print_expr(e[2])
        elif e[0] == "eq":
            self.print_expr(e[1])
            self.print_expr(e[2])
        elif e[0] == "not":
            self.print_expr(e[1])
        elif e[0] == "identifier":
            self.print_id(e[1])
        elif e[0] == "integer":
            self.out_buffer.write(e[1])
            self.out_buffer.write("\n")
        elif e[0] == "string":
            self.out_buffer.write(e[1])
            self.out_buffer.write("\n")
        elif e[0] in ["true", "false"]:
            pass
        else:
            raise TypeError("unknown expression type" + e[0])

    def print_class(self, cl):
        self.print_id(cl[1])
        self.out_buffer.write(cl[0])
        self.out_buffer.write("\n")
        if cl[2]:
            self.print_id(cl[2])
        self.print_lst(self.print_feature, cl[3])

class CL_LEX_tokenizer():
    def __init__(self, inStream):
        self.inStream = inStream
        self.tokens = []
        self.read_tokens()

    # ugly code that works for valid .cl-lex file
    def read_tokens(self):
        fin = self.inStream

        while True:
            tok = LexToken()
            tok.lineno = fin.readline()[:-1]
            if not tok.lineno:
                break
            tok.value   = fin.readline()[:-1]
            tok.type = str.upper(tok.value)
            if tok.type in ["INTEGER","STRING","TYPE","IDENTIFIER"]:
                tok.value = fin.readline()[:-1]
            tok.lexpos = 0
            self.tokens.append(tok)

        self.ptr = -1
        self.len = len(self.tokens)
        fin.close()

    # x.token() function required by the parser.
    def token(self):
        self.ptr += 1
        if self.ptr == self.len:
            return None
        else:
            return self.tokens[self.ptr]


def get_ast_stream(inStream):
    lexer = CL_LEX_tokenizer(inStream)
    ast = parser.parse(lexer=lexer)
    out_buffer = AST_Printer(ast).get_buff()
    out_buffer.seek(0)
    return out_buffer

if __name__ == '__main__':
    import sys
    input_file_name = sys.argv[1]
    out_file_name = input_file_name[:-3] + "ast"

    inputStream = open(input_file_name, "r")
    ast_buff = get_ast_stream(inputStream)
    inputStream.close()

    f_out = open(out_file_name, "w")
    f_out.write(ast_buff.getvalue())
    f_out.close()
