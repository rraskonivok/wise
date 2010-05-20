from decorator import decorator
from itertools import islice

#from wise.worksheet.models import MathematicalTransform
#from wise.worksheet.models import MathematicalIdentity

def Mapping(x, y):
    def f1(func):

        func.case = {}
        func.mapping = True

        func.domain = x.args
        func.codomain = y.args

        func.context = None

        def wrapper(*args):
            domain = args[1:]

            codomain = func(*domain)
            if domain in func.case:
                print 'abc'

            domain_check = all(isinstance(a,b) for a,b in zip(domain,x.args))
            codomain_check =  all(isinstance(a,b) for a,b in zip((codomain,),y.args))

            if not domain_check or not codomain_check:
                print "%s takes [%s -> %s ] instead is [ %s -> %s ]" % (func.__name__, x.args , y.args, map(type,domain), map(type,(codomain,)))
                return None
            else:
                return codomain

        return decorator(wrapper, func)
    return f1

class _(object):
    def __init__(self,*args):
        self.args = args

    def __rshift__(self,other):
        return Mapping(self,other)

    def __hash__(self):
        args = map(lambda o: o.__name__, self.args)
        return hash(tuple(args))

    def __ge__(self,other):
        return Coercion(self,other)

def _mapping(func, *args, **kw):
    return func(*args,**kw)

def Map(f):
    return decorator(_mapping, f )

def iter_mappings(module):
    for name, obj in module.items():
        if hasattr(obj,'mapping'):
            yield obj
