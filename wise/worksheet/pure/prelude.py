# Import the Cython interface
try:
    from pure import *
except ImportError:
    raise Exception('Could not load Cython Pure module, perhaps it needs to be built?')

env.eval('using worksheet::pure::prelude')

ref = PureSymbol('wiseref')
refop = PureSymbol('wiserefop')

proto_op = PureSymbol('prototype')
instance = PureSymbol('instance')

i2p = PureSymbol('i2p')
p2i = PureSymbol('p2i')
