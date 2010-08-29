from django.conf import settings
from django.utils import importlib
import wise.worksheet.exceptions as exception

from wise.worksheet.utils import haml
from types import ClassType, InstanceType
from inspect import getargspec
from django.template import Template, Context

# Import the Cython interface
try:
    import pure.prelude
# Gotta catch em' all, this is justified since if Pure fails to
# load then nothing will work.
except:
    raise Exception('Could not load Pure prelude, all other Pure dependencies will fail.')

ROOT_MODULE = 'wise.worksheet'
packages = {}
objects = {}

def is_pure_expr(obj):
    return isinstance(obj,pure.prelude.PureExpr)

for pack in settings.INSTALLED_MATH_PACKAGES:
    try:
        path = '.'.join([ROOT_MODULE,pack,'prelude'])
        packages[pack] = importlib.import_module(path)
        for name, obj in packages[pack].__dict__.iteritems():
            print 'looking at', name
            if is_pure_expr(obj):
                objects[name] = obj
    except ImportError:
        raise exception.IncompletePackage(pack,'prelude.py')

print objects


# Traverse the root class and process all classes that inherit from
# it
def generate_pure_objects(root):
    if root.pure:
        #print 'Building Cython symbol for ... ', root.pure
        root.po = PureSymbol(root.pure)

    for cls in root.__subclasses__():
        generate_pure_objects(cls)

# Wrap the atomic Pure objects up into this namespace.
PureInt = pure.prelude.PureInt
PureSymbol = pure.prelude.PureSymbol
PureLevel = pure.prelude.PureLevel
stupid = pure.prelude.stupid

# This is called freqently enough that we'll push it up.
reduce_with_pure_rules = pure.prelude.reduce_with_pure_rules
