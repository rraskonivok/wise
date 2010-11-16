from django.conf import settings
from django.utils import importlib
import wise.worksheet.exceptions as exception

from wise.worksheet.utils import haml
from types import ClassType, InstanceType
from inspect import getargspec
from django.template import Template, Context

import sys

# Import the Cython interface
try:
    import wise.pure as pure
# Gotta catch em' all, this is justified since if Pure fails to
# load then nothing will work.
except:
    raise Exception('Could not load Pure prelude, all other Pure dependencies will fail.')
    sys.exit(0)

# Pull the atomic Pure objects up into this namespace.
PureInt = pure.prelude.PureInt
PureSymbol = pure.prelude.PureSymbol
PureLevel = pure.prelude.PureLevel
PureExpr = pure.prelude.PureExpr
PureDouble = pure.prelude.PureDouble

env = pure.prelude.env

p2i = pure.prelude.p2i
i2p = pure.prelude.i2p

# This is called freqently enough that we'll push it up.
reduce_with_pure_rules = pure.prelude.reduce_with_pure_rules

proto_op = pure.prelude.proto_op
instance = pure.prelude.instance
new_level = pure.prelude.new_level
restore_level = pure.prelude.restore_level

ROOT_MODULE = 'wise'
packages = {}
objects = {}

def use(package, library):
    print 'using ' + '::'.join([package, library])
    env.eval('using ' + '::'.join([package, library]))

def jit_compile_interp():
    return env.compile_interp()

def is_pure_expr(obj):
    return isinstance(obj,PureExpr)

for pack in settings.INSTALLED_MATH_PACKAGES:
    try:
        path = '.'.join([ROOT_MODULE,pack,pack])
        packages[pack] = importlib.import_module(path)
        #use(pack,'prelude')
        for name, obj in packages[pack].__dict__.iteritems():
            if is_pure_expr(obj):
                #print "Importing symbol '%s' from pack %s" % (name, pack)
                if not name in objects:
                    objects[name] = obj
                else:
                    raise Exception("Namespace collision, tried to import '%s' from package '%s' but symbol already exists")
    except ImportError:
        raise exception.IncompletePackage(pack,'%s.py' % pack)

print 'Done importing objects'

if settings.PRECOMPILE:
    jit_compile_interp()

# Traverse the root class and process all classes that inherit from
# it, these are stored in in the internal .po method of the class
def generate_pure_objects(root):
    if root.pure:
        #print 'Building Cython symbol for ... ', root.pure
        root.po = PureSymbol(root.pure)

    for cls in root.__subclasses__():
        generate_pure_objects(cls)

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
        # instance ( lhs --> rhs )
        instance(self._proto)

    def __repr__(self):
        return str(self._proto)
