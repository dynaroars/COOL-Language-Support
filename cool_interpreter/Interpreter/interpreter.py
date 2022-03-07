##################### ##################### ###############
#                 COOL INTERPRETER IN PY
# Author: Li Linhan
# Date:   6/20/2021
# Known issue:  
#       - does not work well for recuisive COOL 
#       programs, as the stack depth limit for python is
#       kinda small and no tail-call optimization. 
#       - Check this out: https://chrispenner.ca/posts/python-tail-recursion 
#       - a tree traversal based evaluation could be another possible solution?
##################### ##################### ###############

from utils.Helpers import *
from utils.env import *
from utils.Cool_expr import *
import sys
from sys import exit

# this is dangerous.
# and it does not work, the program just quit without giving any error message...
sys.setrecursionlimit(99999)


class Cool_Prog():
    def __init__(self, inStream):
        self.fin = inStream
        self.cmap = {}
        self.imap = {}
        self.pmap = {}

    def read(self):
        Cool_expr.set_MODE("ANNOTATED_AST")
        self.read_class_map()
        self.read_imp_map()
        self.read_parent_map()

    def read_class_map(self):
        assert self.fin.readline() == "class_map\n"
        class_num = int(self.fin.readline())
        for i in range(class_num):
            cname = self.fin.readline()[:-1]
            self.cmap[cname] = read_lst(Cool_attri.read, self.fin)
    def read_imp_map(self):
        assert self.fin.readline() == "implementation_map\n"
        class_num = int(self.fin.readline())
        for i in range(class_num):
            cname = self.fin.readline()[:-1]
            methods = read_lst(Cool_method.read, self.fin)
            for m in methods:
                self.imap[ (cname, m.name) ] = m
    def read_parent_map(self):
        assert self.fin.readline() == "parent_map\n"
        class_num = int(self.fin.readline())
        for i in range(class_num):
            cname = self.fin.readline()[:-1]
            self.pmap[cname] = self.fin.readline()[:-1]

    def get_attris(self, cname):
        return self.cmap[cname]

    def get_formals(self, cname, mname):
        return self.imap[ (cname, mname) ].formals

    def get_mbody(self, cname, mname):
        return self.imap[ (cname, mname) ].body

    def dist(self, tname, btype):
        current = btype
        count = 0 
        while current != tname:
            try:
                current = self.pmap[current]
                count += 1
            except:
                return -1
        return count


class Cool_attri():
    def read(fin):
        init = fin.readline()[:-1]
        name = fin.readline()[:-1]
        type = fin.readline()[:-1]
        if init == "initializer":
            init = Cool_expr.read(fin)
            return Cool_attri(name, type, init)
        return Cool_attri(name, type)

    def __init__(self, name, type, init = None):
        self.name = name
        self.type = type
        self.init = init


class Cool_method():
    def read(fin):
        name = fin.readline()[:-1]
        formals = read_lst( lambda x: x.readline()[:-1], fin)
        owner = fin.readline()[:-1]
        body = Cool_expr.read(fin)
        return Cool_method(name, formals, body)

    def __init__(self, name, formals, body):
        self.name = name
        self.formals = formals
        self.body = body


class Evaluator():
    def __init__(self, prog):
        self.prog = prog
        self.s    = Store()
        self.call_stack = 0

    def push(self, line):
        if self.call_stack > 1000:
            runtime_error(line, "stack overflow")
        self.call_stack += 1

    def pop(self):
        self.call_stack -= 1
    
    def run(self):
        entry = Expr_DDispatch("", Expr_New("",Cool_Id("Main")), Cool_Id("main"), [])

        return self.eval(Cool_void(), {}, entry)

    
    def eval(self, so, e, exp):
        while True:
            try:
                if isinstance(exp, Expr_Assign):
                    var = exp.var.name
                    loc = e[var]
                    rhs = exp.expr
                    val = self.eval(so, e, rhs)
                    self.s.set(loc, val)
                    return val

                elif isinstance(exp, Expr_Integer):
                    return Cool_int(int32(exp.int_value))

                elif isinstance(exp, Expr_String):
                    str = exp.str_value
                    return Cool_string(str.replace("\\n", "\n").replace("\\t", "\t"))

                elif isinstance(exp, Expr_Bool):
                    return Cool_bool(exp.bool_value)

                elif isinstance(exp, Expr_Id):
                    name = exp.cool_id.name
                    if  name == "self":
                        return so
                    else:
                        return self.s[ e[name] ]

                elif isinstance(exp, Expr_Arith):
                    v1 = self.eval(so, e, exp.e1)
                    v2 = self.eval(so, e, exp.e2)
                    if exp.op == "plus":
                        return v1+v2
                    elif exp.op == "times":
                        return v1*v2
                    elif exp.op == "minus":
                        return v1-v2
                    elif exp.op == "divide":
                        if v2 == Cool_int(0):
                            runtime_error(exp.line, "division by zero")
                        return v1/v2

                elif isinstance(exp, Expr_New):
                    self.push(exp.line)
                    cname = exp.tname.name
                    if cname == "SELF_TYPE":
                        cname = so.get_type()

                    attris = self.prog.get_attris(cname)
                    anames = [x.name for x in attris]
                    atypes = [x.type for x in attris]
                    ainits = [x.init for x in attris]
                    locs   = [self.s.malloc() for x in attris]
                    init_values = [Cool_value.init_for(t) for t in atypes]
                    name_loc    = {name:loc for name,loc in zip(anames, locs)}
                    # Ojb creation
                    if cname == "Int":
                        v1 = Cool_int()
                    elif cname == "String":
                        v1 = Cool_string()
                    elif cname == "Bool":
                        v1 = Cool_bool()
                    else:
                        v1 = Cool_obj(cname, name_loc )
                    # attris init
                    self.s.update( {loc:val for loc,val in zip(locs, init_values) } )
                    # evaluate init
                    for var,init in zip(anames, ainits):
                        if init:
                            self.eval(v1, name_loc, Expr_Assign("", Cool_Id(var), init))
                    self.pop()
                    return v1

                elif isinstance(exp, Expr_DDispatch):
                    self.push(exp.line)
                    line      = exp.line
                    expr      = exp.expr
                    mname     = exp.method.name
                    arg_exprs = exp.args
                    # eval args
                    arg_vals  = [ self.eval(so, e, arg_e) for arg_e in arg_exprs ]
                    # eval expr/so
                    v0 = self.eval(so, e, expr)
                    cname = v0.get_type()
                    if cname == "void":
                        runtime_error(line, "dispatch on void")
                    # get method
                    formals = self.prog.get_formals(cname, mname)
                    locs    = [self.s.malloc() for f in formals]
                    body    = self.prog.get_mbody(cname, mname)
                    # bind args 
                    args_locs = {arg:loc for arg,loc in zip(formals, locs)}
                    self.s.update( {loc:val for loc,val in zip(locs, arg_vals)} )
                    # get object env
                    new_e = v0.get_attris().copy()
                    new_e.update(args_locs)
                    val = self.eval(v0, new_e, body)
                    self.pop()
                    return val

                elif isinstance(exp, Expr_SDispatch):
                    self.push(exp.line)
                    line      = exp.line
                    expr      = exp.expr
                    target    = exp.target.name
                    mname     = exp.method.name
                    arg_exprs = exp.args
                    # eval args
                    arg_vals  = [ self.eval(so, e, arg_e) for arg_e in arg_exprs ]
                    # eval expr/so
                    v0 = self.eval(so, e, expr)
                    cname = v0.get_type()
                    if cname == "void":
                        runtime_error(line, "static dispatch on void")
                    # get method
                    formals = self.prog.get_formals(target, mname)
                    locs    = [self.s.malloc() for f in formals]
                    body    = self.prog.get_mbody(target, mname)
                    # bind args 
                    args_locs = {arg:loc for arg,loc in zip(formals, locs)}
                    self.s.update( {loc:val for loc,val in zip(locs, arg_vals)} )
                    # get object env
                    new_e = v0.get_attris().copy()
                    new_e.update(args_locs)
                    val = self.eval(v0, new_e, body)
                    self.pop()
                    return val

                elif isinstance(exp, Expr_SelfDispatch):
                    line = exp.line
                    expr = Expr_Id("", Cool_Id("self"))
                    mname= exp.method
                    args = exp.args
                    Expr_DDispatch(line, expr, mname, args)
                    return self.eval(so, e, Expr_DDispatch(line, expr, mname, args))

                elif isinstance(exp, Expr_Block):
                    v0 = None
                    for expr in exp.exprs:
                        v0 = self.eval(so, e, expr)
                    return v0

                elif isinstance(exp, Expr_If):
                    v0 = self.eval(so, e, exp.predicate)
                    assert isinstance(v0, Cool_bool)
                    if v0.value:
                        raise Recurse(so, e, exp.bt)
                    else:
                        raise Recurse(so, e, exp.bf)
                
                elif isinstance(exp, Expr_While):
                    predicate = exp.predicate
                    body      = exp.body
                    val = self.eval(so, e, predicate)
                    if val.value:
                        self.eval(so, e, body)
                        raise Recurse(so, e, exp)
                    else:
                        return Cool_void()

                elif isinstance(exp, Expr_Isvoid):
                    v0 = self.eval(so, e, exp)
                    if isinstance(v0, Cool_void):
                        return Cool_bool(True)
                    else:
                        return Cool_bool(False)

                elif isinstance(exp, Expr_Cmp):
                    v_lhs = self.eval(so, e, exp.lhs)
                    v_rhs = self.eval(so, e, exp.rhs)
                    op  = exp.op
                    if op == "lt":
                        return Cool_bool(v_lhs.value < v_rhs.value)
                    elif op == "le":
                        return Cool_bool(v_lhs.value <= v_rhs.value)
                    else:
                        runtime_error("0", "CMP MISS MATHCING")

                elif isinstance(exp, Expr_Equal):
                    v_lhs = self.eval(so, e, exp.lhs)
                    v_rhs = self.eval(so, e, exp.rhs)
                    return Cool_bool(v_lhs.value == v_rhs.value)

                elif isinstance(exp, Expr_Not):
                    v0 = self.eval(so, e, exp.expr)
                    return Cool_bool(not v0.value)
                
                elif isinstance(exp, Expr_Negate):
                    v0 = self.eval(so, e, exp.expr)
                    return Cool_int( -v0.value )
                
                elif isinstance(exp, Expr_Let):
                    e = e.copy()
                    bindings = exp.bindings
                    ebody    = exp.body
                    for b in bindings:
                        name= b.get_name()
                        loc = self.s.malloc()
                        type= b.get_type()
                        init= b.expr
                        if init:
                            init_val = self.eval(so, e, init)
                        else:
                            init_val = Cool_value.init_for(type)
                        e[name] = loc
                        self.s.set(loc, init_val)
                    raise Recurse(so, e, ebody)

                elif isinstance(exp, Expr_Case):
                    e = e.copy()
                    v0 = self.eval(so, e, exp.expr)
                    branches = exp.elements
                    vt = v0.get_type()
                    if isinstance(v0, Cool_void):
                        runtime_error(exp.line, "case on void")
                    branches = [ (self.prog.dist(b.get_type(), vt), b ) for b in branches ]
                    branches = sorted([ b for b in branches if b[0] > -1])
                    if not branches:
                        runtime_error(exp.line, "case without matching branch: %s(...)" % vt)
                    matched = branches[0][1]
                    
                    loc = self.s.malloc()
                    e[matched.get_name()] = loc
                    self.s.set(loc, v0)

                    raise Recurse(so, e, matched.expr)

                elif isinstance(exp, Expr_Internal):
                    if exp.details == "IO.in_int":
                        return Cool_int( read_int_32() )
                    elif exp.details == "IO.in_string":
                        str = input()
                        if "\0" in str or "":
                            return Cool_string()
                        str = str.replace("\\n", "\n").replace("\\t", "\t")
                        return Cool_string(str)
                    elif exp.details == "IO.out_int":
                        arg = self.s[ e["x"] ]
                        print(arg.value, end="")
                        return so
                    elif exp.details == "IO.out_string":
                        arg = self.s[ e["x"] ]
                        print(arg.value, end="")
                        return so
                    elif exp.details == "Object.abort":
                        print("abort\n", end="")
                        exit(1)
                    elif exp.details == "Object.copy":
                        return so.copy()
                    elif exp.details == "Object.type_name":
                        return Cool_string(so.get_type())
                    elif exp.details == "String.concat":
                        s1 = so
                        s2 = self.s[ e["s"] ]
                        return Cool_string(s1.value + s2.value)
                    elif exp.details == "String.length":
                        return Cool_int( len(so.value) )
                    elif exp.details == "String.substr":
                        try:
                            str = so.value
                            i = self.s[ e["i"] ].value
                            l = self.s[ e["l"] ].value
                            assert i<=len(str) and (i+l)<=len(str)
                            return Cool_string(str[i:i+l])
                        except:
                            runtime_error("0", "String.substr out of range")
                    else:
                        runtime_error("","UNKNOWN INTERNAL")
            except Recurse as r:
                so = r.so
                e  = r.e
                exp= r.exp
                continue
                        

def evaluate_cl_type(inStream):
    prog = Cool_Prog(inStream)
    prog.read()
    e = Evaluator(prog)
    return e.run()


if __name__ == "__main__":
    # prog = Cool_Prog("D:\\SysDir\\Documents\\COOL-Compiler-In-Py\Interpreter\\test_cases\\good\\primes.cl-type")
    fin = open(sys.argv[1], "r")
    evaluate_cl_type(fin)
    fin.close()

    
