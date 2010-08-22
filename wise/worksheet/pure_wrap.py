# Import the Cython interface
from pure.base import *

# Traverse the root class and process all class that inherit from
# it

def generate_pure_objects(root):
    if root.pure:
        #print 'Building Cython symbol for ... ', root.pure
        root.po = pure.PureSymbol(root.pure)

    for cls in root.__subclasses__():
        generate_pure_objects(cls)
