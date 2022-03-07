##################### ##################### ###############
# this is for both the typecheker and interpretor
##################### ##################### ###############

from copy import deepcopy, copy
from utils.Helpers import *
from functools import reduce

class Cool_Id():
    def read(fin):
        line = fin.readline()[:-1]
        name = fin.readline()[:-1]
        return Cool_Id(name, line)

    def __init__(self, name, line=""):
        self.name = name
        self.line = line
    def __str__(self):
        return "%s\n%s\n" % (self.line, self.name)
    def __repr__(self):
        return self.__str__()
    def get_name(self):
        return self.name
    def get_line(self):
        return self.line

class Cool_type():
    def __init__(self, tname, selftype = False):
        self.tname = tname
        self.selftype = selftype

    def tostr(self):
        return self.tname

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.tname
        else:
            return self.tname == other.tname
    def static_str(self):
        if self.selftype:
            return "SELF_TYPE"
        else:
            return self.tname
    def __str__(self):
        if self.selftype:
            return "SELF_TYPE(%s)" % self.tname
        else:
            return self.tname
    def __repr__(self):
        return self.__str__()


class Typing_env():
    def __init__(self, o = None, m = None, c = None, inheritance = None):
        self.o = o
        self.m = m
        self.c = c
        self.inheritance = inheritance
    def debug(self):
        print(self.o)
        print(self.m.keys())
        print(self.c)
    def copy(self):
        return Typing_env(  o = copy(self.o),
                            m = self.m,
                            c = self.c,
                            inheritance = self.inheritance)
    def add_var(self, var, type):
        self.o[var] = type
    def add_vars(self, vars):
        self.o.update(vars)
    def get_selftype(self):
        return self.c
    def get_method_signiture(self, c, m):
        if not (c.tname, m.name) in self.m:
            tc_error(  m.get_line(),
                    "unknown method %s in dispatch on %s"
                    % (m.name, c.tname))
        return self.m[(c.tname, m.name)].signiture
    def get_method_return(self, c, m):
        if not (c.tname, m.name) in self.m:
            tc_error(  m.get_line(),
                    "unknown method %s in dispatch on %s"
                    % (m.name, c.tname))
        return self.m[(c.tname, m.name)].return_type
    def typeof(self, cid):
        var_name = cid.get_name()
        if not var_name in self.o:
            tc_error(  cid.get_line(),
                    "unbound identifier %s"
                     % (var_name))
        return self.o[var_name]
    def has_type(self, t):
        return self.inheritance.has_node(t.tostr())
    def is_parent_child(self, p, c):
        if p.selftype == False:
            return self.inheritance.get_node(c.tostr()).has_parent(p)
        else:
            return (p == c) and (p.selftype == c.selftype)
    def lub(self, a, b):
        if a.selftype and b.selftype:
            return Cool_type(self.inheritance.lub(a.tostr(), b.tostr()), selftype = True)
        else:
            return Cool_type(self.inheritance.lub(a.tostr(), b.tostr()))


class Cool_expr():
    def set_MODE(mode):
        Cool_expr.MODE = mode


    def read(fin):
        kwargs = {}  # holds extra details for sub classes
        kwargs["line"] = fin.readline()[:-1]
        # discard the extra type info in annotated ast
        (fin.readline() if Cool_expr.MODE == "ANNOTATED_AST" else 0)
        kwargs["ename"] = fin.readline()[:-1]

        if kwargs["ename"] == "assign":
            return Expr_Assign.read(fin, **kwargs)
        elif kwargs["ename"] == "dynamic_dispatch":
            return Expr_DDispatch.read(fin, **kwargs)
        elif kwargs["ename"] == "static_dispatch":
            return Expr_SDispatch.read(fin, **kwargs)
        elif kwargs["ename"] == "self_dispatch":
            return Expr_SelfDispatch.read(fin, **kwargs)
        elif kwargs["ename"] == "if":
            return Expr_If.read(fin, **kwargs)
        elif kwargs["ename"] == "while":
            return Expr_While.read(fin, **kwargs)
        elif kwargs["ename"] == "block":
            return Expr_Block.read(fin, **kwargs)
        elif kwargs["ename"] == "new":
            return Expr_New.read(fin, **kwargs)
        elif kwargs["ename"] == "isvoid":
            return Expr_Isvoid.read(fin, **kwargs)
        elif kwargs["ename"] in ["plus","minus","times","divide"]:
            return Expr_Arith.read(fin, **kwargs)
        elif kwargs["ename"] == "eq":
            return Expr_Equal.read(fin, **kwargs)
        elif kwargs["ename"] in ["lt","le"]:
            return Expr_Cmp.read(fin, **kwargs)
        elif kwargs["ename"] == "not":
            return Expr_Not.read(fin, **kwargs)
        elif kwargs["ename"] == "negate":
            return Expr_Negate.read(fin, **kwargs)
        elif kwargs["ename"] == "string":
            return Expr_String.read(fin, **kwargs)
        elif kwargs["ename"] == "integer":
            return Expr_Integer.read(fin, **kwargs)
        elif kwargs["ename"] == "identifier":
            return Expr_Id.read(fin, **kwargs)
        elif kwargs["ename"] in ["true", "false"]:
            return Expr_Bool.read(fin, **kwargs)
        elif kwargs["ename"] == "let":
            return Expr_Let.read(fin, **kwargs)
        elif kwargs["ename"] == "case":
            return Expr_Case.read(fin, **kwargs)
        elif kwargs["ename"] == "internal":
            return Expr_Internal.read(fin, **kwargs)
        else:
            raise Exception("expr not yet implemented: "+ kwargs["ename"])

    def __init__(self, line):
        self.line   = line

    def tc(self, env):
        self.flush_types(env)
        return self.static_type

    def flush_types(self, env):
        self.static_type = self.typeCheck(env)
        return self.static_type

    def __str__(self):
        return "%s\n%s\n%s" % (self.line, self.static_type.static_str(), self.tostr())
    def tostr(self):
        raise Exception("TOSTR IS NOT OVERIDDEN IN CLASS: " + str(type(self)))

class Expr_Assign(Cool_expr):
    def typeCheck(self, env):
        if self.var.get_name() == "self":
            tc_error(   self.line,
                    "cannot assign to self")
        vtype = env.typeof(self.var)
        etype = self.expr.flush_types(env)
        if not env.is_parent_child(vtype, etype):
            tc_error(  self.line,
                    "%s does not conform %s in assignment"
                    % (vtype, etype))
        return etype

    def __init__(self, line, var, expr):
        self.var = var
        self.expr = expr
        super().__init__(line)
    def read(fin, **kwargs):
        var = Cool_Id.read(fin)
        expr= Cool_expr.read(fin)
        return Expr_Assign(kwargs["line"], var, expr)
    def tostr(self):
        return "assign\n%s%s" % (self.var, self.expr)

class Expr_DDispatch(Cool_expr):
    def typeCheck(self, env):
        t0 = self.expr.flush_types(env)
        mname = self.method
        signiture = env.get_method_signiture(t0, mname)
        arguments = list(map(lambda x: x.flush_types(env), self.args))
        if not len(signiture) == len(arguments):
            tc_error(  self.line,
                    "wrong number of actual arguments (%d vs. %d)"
                    % (len(arguments), len(signiture)))
        for i in range(len(signiture)):
            if not env.is_parent_child(signiture[i], arguments[i]):
                tc_error(  self.args[i].line,
                        "argument #%d type %s does not conform to formal type %s"
                        % (i+1, arguments[i], signiture[i]))
        rtype = env.get_method_return(t0, mname)
        if rtype == "SELF_TYPE":
            rtype = t0
        return rtype

    def __init__(self, line, expr, method, args):
        self.expr = expr
        self.method = method
        self.args = args
        super().__init__(line)
    def read(fin, **kwargs):
        e       = Cool_expr.read(fin)
        m       = Cool_Id.read(fin)
        args    = read_lst(Cool_expr.read, fin)
        return Expr_DDispatch(kwargs["line"], e, m ,args)
    def tostr(self):
        return "dynamic_dispatch\n%s%s%s" % (self.expr, self.method, elst_to_str(self.args))

class Expr_SDispatch(Cool_expr):
    def typeCheck(self, env):
        t0 = self.expr.flush_types(env)
        t  = Cool_type(self.target.get_name())
        if not env.is_parent_child(t, t0):
            tc_error(  self.line,
                    "%s does not conform to %s in static dispatch"
                    % (t0, t))
        mname = self.method
        signiture = env.get_method_signiture(t, mname)
        arguments = list(map(lambda x: x.flush_types(env), self.args))
        if not len(signiture) == len(arguments):
            tc_error(  self.line,
                    "wrong number of actual arguments (%d vs. %d)"
                    % (len(arguments), len(signiture)))
        for i in range(len(signiture)):
            if not env.is_parent_child(signiture[i], arguments[i]):
                tc_error(  self.args[i].line,
                        "argument #%d type %s does not conform to formal type %s"
                        % (i+1, arguments[i], signiture[i]))
        rtype = env.get_method_return(t0, mname)
        if rtype == "SELF_TYPE":
            rtype = t0
        return rtype

    def __init__(self, line, expr, target, method, args):
        self.expr = expr
        self.target = target
        self.method = method
        self.args = args
        super().__init__(line)
    def read(fin, **kwargs):
        e       = Cool_expr.read(fin)
        t       = Cool_Id.read(fin)
        m       = Cool_Id.read(fin)
        args    = read_lst(Cool_expr.read, fin)
        return Expr_SDispatch(kwargs["line"], e, t, m, args)
    def tostr(self):
        return "static_dispatch\n%s%s%s%s" % (self.expr, self.target, self.method, elst_to_str(self.args))

class Expr_SelfDispatch(Cool_expr):
    def typeCheck(self, env):
        t0 = env.typeof(Cool_Id("self", 0))
        mname = self.method
        signiture = env.get_method_signiture(t0, mname)
        arguments = list(map(lambda x: x.flush_types(env), self.args))
        if not len(signiture) == len(arguments):
            tc_error(  self.line,
                    "wrong number of actual arguments (%d vs. %d)"
                    % (len(arguments), len(signiture)))
        for i in range(len(signiture)):
            if not env.is_parent_child(signiture[i], arguments[i]):
                tc_error(  self.args[i].line,
                        "argument #%d type %s does not conform to formal type %s"
                        % (i+1, arguments[i], signiture[i]))
        rtype = env.get_method_return(t0, mname)
        if rtype == "SELF_TYPE":
            rtype = t0
        return rtype

    def __init__(self, line, method, args):
        self.method = method
        self.args = args
        super().__init__(line)
    def read(fin, **kwargs):
        m       = Cool_Id.read(fin)
        args    = read_lst(Cool_expr.read, fin)
        return Expr_SelfDispatch(kwargs["line"], m, args)
    def tostr(self):
        return "self_dispatch\n%s%s" % (self.method, elst_to_str(self.args))

class Expr_If(Cool_expr):
    def typeCheck(self, env):
        predicate_type = self.predicate.flush_types(env)
        if not predicate_type == "Bool":
            tc_error(  self.predicate.line,
                    "predicate has type %s instead of Bool"
                    % (predicate_type))
        bt_type        = self.bt.flush_types(env)
        bf_type        = self.bf.flush_types(env)
        return env.lub(bt_type, bf_type)

    def __init__(self, line, predicate, bt, bf):
        self.predicate = predicate
        self.bt = bt
        self.bf = bf
        super().__init__(line)
    def read(fin, **kwargs):
        predicate = Cool_expr.read(fin)
        bt        = Cool_expr.read(fin)
        bf        = Cool_expr.read(fin)
        return Expr_If(kwargs["line"], predicate, bt, bf)
    def tostr(self):
        return "if\n%s%s%s" % (self.predicate, self.bt, self.bf)

class Expr_While(Cool_expr):
    def typeCheck(self, env):
        predicate_type = self.predicate.flush_types(env)
        if not predicate_type == "Bool":
            tc_error(  self.predicate.line,
                    "conditional has type %s instead of Bool"
                    % (predicate_type))
        self.body.flush_types(env)

        return Cool_type("Object")

    def __init__(self, line, predicate, body):
        self.predicate = predicate
        self.body = body
        super().__init__(line)
    def read(fin, **kwargs):
        predicate = Cool_expr.read(fin)
        body      = Cool_expr.read(fin)
        return Expr_While(kwargs["line"], predicate, body)
    def tostr(self):
        return "while\n%s%s" % (self.predicate, self.body)


class Expr_Block(Cool_expr):
    def typeCheck(self, env):
        for e in self.exprs:
            rtype = e.flush_types(env)
        return rtype

    def __init__(self, line, exprs):
        self.exprs = exprs
        super().__init__(line)
    def read(fin, **kwargs):
        exprs = read_lst(Cool_expr.read, fin)
        return Expr_Block(kwargs["line"], exprs)
    def tostr(self):
        return "block\n%s" % (elst_to_str(self.exprs))

class Expr_New(Cool_expr):
    def typeCheck(self, env):
        t = Cool_type(self.tname.get_name())
        if t == "SELF_TYPE":
            t = env.get_selftype()
        elif not env.has_type(t):
            tc_error(  self.tname.line,
                    "unknown type %s"
                    % (self.tname))
        return t

    def __init__(self, line, tname):
        self.tname = tname
        super().__init__(line)
    def read(fin, **kwargs):
        cname = Cool_Id.read(fin)
        return Expr_New(kwargs["line"], cname)
    def tostr(self):
        return "new\n%s" % (self.tname)

class Expr_Isvoid(Cool_expr):
    def typeCheck(self, env):
        self.expr.flush_types(env)
        return Cool_type("Bool")

    def __init__(self, line, expr):
        self.expr = expr
        super().__init__(line)
    def read(fin, **kwargs):
        e = Cool_expr.read(fin)
        return Expr_Isvoid(kwargs["line"], e)
    def tostr(self):
        return "isvoid\n%s" % (self.expr)

class Expr_Arith(Cool_expr):
    def typeCheck(self, env):
        t1 = self.e1.flush_types(env)
        t2 = self.e2.flush_types(env)
        if (not t1 == "Int") or (not t2 == "Int"):
            tc_error(  self.line,
                    "arithmetic on %s %s instead of Ints"
                    % (t1, t2))
        return Cool_type("Int")

    def __init__(self, line, op, e1, e2):
        self.e1 = e1
        self.e2 = e2
        self.op = op
        super().__init__(line)
    def read(fin, **kwargs):
        e1 = Cool_expr.read(fin)
        e2 = Cool_expr.read(fin)
        return Expr_Arith(kwargs["line"], kwargs["ename"], e1, e2)
    def tostr(self):
        return "%s\n%s%s" % (self.op, self.e1, self.e2)

class Expr_Equal(Cool_expr):
    def typeCheck(self, env):
        t1 = self.lhs.flush_types(env)
        t2 = self.rhs.flush_types(env)
        if  (t1 in ["Int", "String", "Bool"] or \
            t2 in ["Int", "String", "Bool"]) and \
                t1 != t2:
            tc_error(  self.line,
                    "comparison between %s and %s"
                    % (t1, t2))
        return Cool_type("Bool")
    def __init__(self, line, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        super().__init__(line)
    def read(fin, **kwargs):
        lhs = Cool_expr.read(fin)
        rhs = Cool_expr.read(fin)
        return Expr_Equal(kwargs["line"], lhs, rhs)
    def tostr(self):
        return "eq\n%s%s" % (self.lhs, self.rhs)


class Expr_Cmp(Cool_expr):
    def typeCheck(self, env):
        t1 = self.lhs.flush_types(env)
        t2 = self.rhs.flush_types(env)
        if  (t1 in ["Int", "String", "Bool"] or \
            t2 in ["Int", "String", "Bool"]) and \
                t1 != t2:
            tc_error(  self.line,
                    "comparison between %s and %s"
                    % (t1, t2))
        return Cool_type("Bool")

    def __init__(self, line, op, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.op  = op
        super().__init__(line)
    def read(fin, **kwargs):
        lhs = Cool_expr.read(fin)
        rhs = Cool_expr.read(fin)
        return Expr_Cmp(kwargs["line"], kwargs["ename"], lhs, rhs)
    def tostr(self):
        return "%s\n%s%s" % (self.op, self.lhs, self.rhs)

class Expr_Not(Cool_expr):
    def typeCheck(self, env):
        t = self.expr.flush_types(env)
        if not t == "Bool":
            tc_error(  self.line,
                    "not applied to type %s instead of Bool"
                    % (t))
        return Cool_type("Bool")

    def __init__(self, line, expr):
        self.expr = expr
        super().__init__(line)
    def read(fin, **kwargs):
        e = Cool_expr.read(fin)
        return Expr_Not(kwargs["line"], e)
    def tostr(self):
        return "not\n%s" % (self.expr)

class Expr_Negate(Cool_expr):
    def typeCheck(self, env):
        t = self.expr.flush_types(env)
        if not t == "Int":
            tc_error(  self.line,
                    "not applied to type %s instead of Int"
                    % (t))
        return Cool_type("Int")

    def __init__(self, line, expr):
        self.expr = expr
        super().__init__(line)
    def read(fin, **kwargs):
        e = Cool_expr.read(fin)
        return Expr_Negate(kwargs["line"], e)
    def tostr(self):
        return "negate\n%s" % (self.expr)

class Expr_Integer(Cool_expr):
    def typeCheck(self, env):
        return Cool_type("Int")

    def __init__(self, line, int_value):
        self.int_value = int_value
        super().__init__(line)
    def read(fin, **kwargs):
        int_value = fin.readline()[:-1]
        return Expr_Integer(kwargs["line"], int_value)
    def tostr(self):
        return "integer\n%s\n" % (self.int_value)

class Expr_String(Cool_expr):
    def typeCheck(self, env):
        return Cool_type("String")

    def __init__(self, line, str_value):
        self.str_value = str_value
        super().__init__(line)
    def read(fin, **kwargs):
        s = fin.readline()[:-1]
        return Expr_String(kwargs["line"], s)
    def tostr(self):
        return "string\n%s\n" % (self.str_value)

class Expr_Id(Cool_expr):
    def typeCheck(self, env):
        return env.typeof(self.cool_id)

    def __init__(self, line, cool_id):
        self.cool_id = cool_id
        super().__init__(line)
    def read(fin, **kwargs):
        i = Cool_Id.read(fin)
        return Expr_Id(kwargs["line"], i)
    def tostr(self):
        return "identifier\n%s" % (self.cool_id)

class Expr_Bool(Cool_expr):
    def typeCheck(self, env):
        return Cool_type("Bool")

    def __init__(self, line, bool_value):
        self.bool_value = bool_value
        super().__init__(line)
    def read(fin, **kwargs):
        return Expr_Bool(kwargs["line"], kwargs["ename"])
    def tostr(self):
        return "%s\n" % (self.bool_value)

class Expr_Let(Cool_expr):
    def typeCheck(self, env):
        env = env.copy()
        o = {}
        for b in self.bindings:
            bname, btype, expr = (b.get_name(), Cool_type(b.get_type()), b.get_expr())
            if bname == "self":
                tc_error(  self.line,
                        "binding self in a let is not allowed")
            if btype == "SELF_TYPE":
                btype = env.get_selftype()
            if not env.has_type(btype):
                tc_error(  b.btype.line,
                        "unknown type %s"
                        % (btype))
            if expr:
                etype = expr.flush_types(env)
                if not env.is_parent_child(btype, etype):
                    tc_error(  self.line,
                            "initializer type %s does not conform to type %s"
                            % (etype, btype))
            env.add_var(bname, btype)
        return self.body.flush_types(env)

    class Binding():
        def __init__(self, name, btype, expr = None):
            self.name = name
            self.btype= btype
            self.expr = expr
        def read(fin):
            init = fin.readline()[:-1]
            name = Cool_Id.read(fin)
            btype= Cool_Id.read(fin)
            if init == "let_binding_no_init":
                init = None
            elif init == "let_binding_init":
                init = Cool_expr.read(fin)
            return Expr_Let.Binding(name, btype, init)
        def get_name(self):
            return self.name.get_name()
        def get_type(self):
            return self.btype.get_name()
        def get_expr(self):
            return self.expr
        def __str__(self):
            if self.expr:
                return "let_binding_init\n%s%s%s" % (self.name, self.btype, self.expr)
            return "let_binding_no_init\n%s%s" % (self.name, self.btype)

    def __init__(self, line, bindings, body):
        self.bindings = bindings
        self.body = body
        super().__init__(line)
    def read(fin, **kwargs):
        bindings = read_lst(Expr_Let.Binding.read, fin)
        body     = Cool_expr.read(fin)
        return Expr_Let(kwargs["line"], bindings, body)
    def tostr(self):
        return "let\n%s%s" % (elst_to_str(self.bindings), self.body)

class Expr_Case(Cool_expr):
    def typeCheck(self, env):
        self.expr.flush_types(env)
        seen = []
        for t in self.elements:
            if t.get_type() in seen:
                tc_error(   t.name.line,
                        "case branch type %s is bound twice" % t.get_type())
            seen.append(t.get_type())
            
        types = map(lambda x: x.typeCheck(env), self.elements)
        return reduce(lambda a,b: env.lub(a,b), types)




    class CaseElement(Cool_expr):
        def typeCheck(self, env):
            env = env.copy()
            vname = self.name.get_name()
            vtype = self.ctype.get_name()
            expr  = self.expr
            if vname == "self":
                tc_error(  self.name.line,
                        "binding self in a case expression is not allowed")
            if vtype == "SELF_TYPE":
                tc_error(  self.ctype.line,
                        "using SELF_TYPE as a case branch type is not allowed")
            if not env.has_type(Cool_type(vtype)):
                tc_error(  self.ctype.line,
                        "unknown type %s" % vtype)
            env.add_var(vname, Cool_type(vtype))
            return expr.flush_types(env)
        def __init__(self, name, ctype, expr):
            self.name = name
            self.ctype= ctype
            self.expr = expr
        def read(fin):
            var     = Cool_Id.read(fin)
            vtype   = Cool_Id.read(fin)
            body    = Cool_expr.read(fin)
            return Expr_Case.CaseElement(var, vtype, body)
        def get_type(self):
            return self.ctype.name
        def get_name(self):
            return self.name.name        
        def __str__(self):
            return "%s%s%s" % (self.name, self.ctype, self.expr)
    def __init__(self, line, expr, elements):
        self.expr = expr
        self.elements = elements
        super().__init__(line)
    def read(fin, **kwargs):
        expr     = Cool_expr.read(fin)
        elements = read_lst(Expr_Case.CaseElement.read, fin)
        return Expr_Case(kwargs["line"], expr, elements)
    def tostr(self):
        return "case\n%s%s" % (self.expr, elst_to_str(self.elements))

class Expr_Internal(Cool_expr):
    def typeCheck(self, env):
        if self.stype == "SELF_TYPE":
            return env.get_selftype()
        else:
            return self.stype

    def __init__(self, stype, details):
        self.details = details
        self.stype = Cool_type(stype)
        super().__init__(0)
    def tostr(self):
        return "internal\n%s\n" % (self.details)
    def read(fin, **kwargs):
        return Expr_Internal(None, fin.readline()[:-1])
