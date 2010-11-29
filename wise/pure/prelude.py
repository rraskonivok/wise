# Import the Cython interface
try:
    from pure import *
except ImportError:
    raise Exception('Could not load Cython Pure module, perhaps it needs to be built?')

proto_op = PureSymbol('prototype')
instance = PureSymbol('instance')

# Infix to prefix
i2p = PureSymbol('i2p')

#Prefix to infix
p2i = PureSymbol('p2i')

# nargs
nargs = PureSymbol('nargs')
