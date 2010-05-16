from decorator import decorator, FunctionMaker

'''
class condition(object):
    def __new__(self,statement):
        def decorator(cls):
            def wrapper(*args):
                wrapped = cls(*args)
                if statement(wrapped):
                    return wrapped
                else:
                    raise Exception('Condition violated')
            return wrapper
        return decorator
'''

def Mapping(x, y):
    def f1(func):

        func.case = {}
        func.mapping = True
        func.domain = x.args
        func.codomain = y.args

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

    def __ge__(self,other):
        return Coercion(self,other)

def _mapping(func, *args, **kw):
    return func(*args,**kw)

def Map(f):
    return decorator(_mapping, f )

######

#class Real(object):
#    def __init__(self, number):
#        self.number = number
#
#    def __repr__(self):
#        return str(self.number)
#
#    def __add__(self, other):
#        return self.__class__(self.number + other.number)
#
#    def __hash__(self):
#        return hash(self.number)
#
#    def __gt__(self, other):
#        return self.number > other
#
#    def __eq__(self, other):
#        return self.number == other
#
#    def __or__(self, other):
#        return other(self)
#
#class Integer(Real):
#    pass

#add.case[Real(1),Real(0)] = 3
#print add.case[Real(1),Real(0)]
#
#add.pretty = 'Addition'

#print add(Real(1), Real(0))
#print add(Real(1), Real(0))
#print add(Integer(1), Real(-3))
#
#print add.case

for name, obj in locals().items():
    if hasattr(obj,'mapping'):
        print obj.pretty, obj.domain, obj.codomain

