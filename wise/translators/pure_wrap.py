from django.conf import settings
from django.utils import importlib
import wise.worksheet.exceptions as exception

from types import ClassType

# Spawn new Interpreter
from pure.pure import PureEnv
env = PureEnv()
env.eval('using pure::prelude')

from wise.pure.pure import PureInt, PureSymbol, PureLevel, \
PureExpr, PureDouble, PureClosure, reduce_with_pure_rules, \
new_level, restore_level, IManager, PureEnv

from wise.pure.prelude import p2i, i2p, nargs
from wise.utils.aggregator import Aggregator
from wise.worksheet.rules import rulesets
from wise.worksheet.utils import trim_docstring

ROOT_MODULE = 'wise'
packages = {}
objects = Aggregator(file='object_cache')
rules = Aggregator(file='rules_cache')

def use(package, library):
    # Paths are relative to the /wise/ directory
    print 'Importing library ' + '/'.join([package, library])
    env.eval('using ' + '::'.join([package, library]))

def jit_compile_interp():
    return env.compile_interp()

def is_pure_expr(obj):
    return isinstance(obj,PureExpr)

def is_rule(obj):
    return isinstance(obj,PublicRule)

for pack in settings.INSTALLED_MATH_PACKAGES:
    try:
        path = '.'.join([ROOT_MODULE,pack,pack])
        packages[pack] = importlib.import_module(path)
        for name, obj in packages[pack].__dict__.iteritems():
            if is_pure_expr(obj):
                #print "Importing symbol '%s' from pack %s" % (name, pack)
                if not name in objects:
                    objects[name] = obj
                else:
                    raise Exception("Namespace collision, tried to import '%s' from package '%s' but symbol already exists")
    except ImportError:
        raise exception.IncompletePackage(pack,'%s.py' % pack)

# This is a statefull change in the interpreter, if this is
# called at the root definition level it applies globally
class ProtoRule:
    _proto = None
    lhs = None
    rhs = None

    def __init__(self, lhs, rhs, guards=None):
        self.lhs = p2i(lhs)
        self.rhs = p2i(rhs)

    def __call__(self):
        self._proto = proto_op(self.lhs, self.rhs)
        print 'Init rule:', self._proto
        # instance ( lhs --> rhs )1/
        instance(self._proto)

    def __repr__(self):
        return str(self._proto)

class PublicRule:
    po = None
    ref = None
    arity = -1
    pure = None

    def __init__(self):
        self.ref = self.pure
        #self.po = PureClosure(self.pure)
        #pure_wrap.objects[self.pure] = self.po
        #self.po.arity = pure_wrap.nargs(self.po)

    @property
    def description(self):
        return self.__doc__

    def reduce_with(self, *expr):
        po = PureClosure(self.pure)
        return po(*expr)

#        pure_expr = po(*pexpr)
#        pyexpr = pure_to_python(pure_expr,expr[0].idgen)
#
#        print 'Reduced Sexp:', pyexpr
#        print 'Reduced Pure:', pure_expr

        return pyexpr

    #@classmethodn
    #def register(self):
    #    if self.pure:

    #        if hasattr(self,'__doc__') and self.__doc__:
    #            self.desc = trim_docstring(self.__doc__)
    #        else:
    #            self.desc = 'No description available'

    #        self.po = PureClosure(self.pure)
    #        pure_wrap.objects[self.pure] = self.po


# And so begin 4 nested for-loops, yah....
for pack in settings.INSTALLED_MATH_PACKAGES:
    #try:
        path = '.'.join([ROOT_MODULE,pack,'rules'])
        packages[pack] = importlib.import_module(path)
        for name, symbol in packages[pack].__dict__.iteritems():

            # Merge dictionary into main
            if name == 'panel':
                rulesets.update(symbol)

            if type(symbol) is ClassType and issubclass(symbol,
                    PublicRule):
                rules[name] = symbol

            # Register the rule in the translation dictionary
            if hasattr(symbol,'register'):
                symbol.register(a)

    #except ImportError:
    #    raise exception.IncompletePackage(pack,'rules.py')

print 'Done importing objects'

if settings.PRECOMPILE:
    jit_compile_interp()

# Traverse the root class and process all classes that inherit from
# it, these are stored in in the internal .po method of the class
def generate_pure_objects(root):
    if root.pure:
        #print 'Building Cython symbol for ... ', root.pure
        if root.pure not in objects:
            root.po = PureSymbol(root.pure)
        else:
            print 'Namespace collision'

    for cls in root.__subclasses__():
        generate_pure_objects(cls)
