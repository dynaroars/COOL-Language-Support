##################### ##################### ###############
# utils for interpretor.
# defines runtime enviroment and cool values
##################### ##################### ###############
from copy import deepcopy
from numpy import int32

class Store():
    MALLOC_COUNTER = 10000
    def __init__(self):
        self.map = {}

    def malloc(self):
        Store.MALLOC_COUNTER += 1
        return Store.MALLOC_COUNTER

    def set(self, add, val):
        self.map[add] = val

    def update(self, dict):
        self.map.update(dict)

    def __getitem__(self, key):
        assert key in self.map
        return self.map[key]

class Env():
    def __init__(self, map={}):
        self.map = map

    def add(self, var, add):
        self.map[var] = add

    def copy(self):
        return Env(self.map.copy())

class Cool_value():
    def init_for(cname):
        if cname == "Int":
            return Cool_int()
        elif cname == "String":
            return Cool_string()
        elif cname == "Bool":
            return Cool_bool()
        else:
            return Cool_void()

    def __init__(self, type, value):
        self.type = type
        self.value= value
    def __eq__(self, o):
        return self.value == o.value
    def __lt__(self, o):
        return self.value < o.value
    def __le__(self, o):
        return self.value <= o.value
    def get_type(self):
        return self.type
    def get_attris(self):
        if isinstance(self, Cool_obj):
            return self.value
        else:
            return {}
    def copy(self):
        return deepcopy(self)
    def __str__(self):
        return str(self.value)

class Cool_int(Cool_value):
    def __init__(self, value = int32(0)):
        if isinstance(value, int):
            try:
                value = int32(value)
            except:
                value = int32(0)
        super().__init__("Int", value)
    def __add__(self, o):
        return Cool_int( int32(self.value + o.value) )
    def __mul__(self, o):
        return Cool_int( int32(self.value * o.value) )
    def __truediv__(self, o):
        return Cool_int( int32(self.value / o.value) )
    def __sub__(self, o):
        return Cool_int( int32(self.value - o.value))

class Cool_string(Cool_value):
    def __init__(self, value = ""):
        self.length = len(value)
        super().__init__("String", value)
    
class Cool_bool(Cool_value):
    def __init__(self, value = False):
        super().__init__("Bool", value in ["true", True])

class Cool_obj(Cool_value):
    def __init__(self, type, attris):
        super().__init__(type, attris)
    def __str__(self):
        return "%s: %s" % (self.type, self.value)

class Cool_void(Cool_value):
    def __init__(self):
        super().__init__("void", None)
