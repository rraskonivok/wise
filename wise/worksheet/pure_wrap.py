# Import the Cython interface
import pure.base

# Traverse the root class and process all classes that inherit from
# it
def generate_pure_objects(root):
    if root.pure:
        #print 'Building Cython symbol for ... ', root.pure
        root.po = PureSymbol(root.pure)

    for cls in root.__subclasses__():
        generate_pure_objects(cls)

# Wrap the atomic Pure objects

PureInt = pure.base.PureInt
PureSymbol = pure.base.PureSymbol
PureLevel = pure.base.PureLevel

reduce_with_pure_rules = pure.base.reduce_with_pure_rules
