# Import the Cython interface
try:
    from pure import *
except ImportError:
    raise Exception('Could not load Cython Pure module, perhaps it needs to be built?')

env.eval('using worksheet::pure::prelude')
stupid = env.eval('stupid')
print 'Stupid', stupid

ref = PureSymbol('wiseref')
refop = PureSymbol('wiserefop')

is_numeric = PureSymbol('is_numeric')
is_zero = PureSymbol('is_zero')
is_positive = PureSymbol('is_positive')
is_negative = PureSymbol('is_negative')
is_integer = PureSymbol('is_integer')
is_pos_integer = PureSymbol('is_pos_integer')
is_nonneg_integer = PureSymbol('is_nonneg_integer')
is_even = PureSymbol('is_even')
is_odd = PureSymbol('is_odd')
is_prime = PureSymbol('is_prime')
is_rational = PureSymbol('is_rational')
is_real = PureSymbol('is_real')
is_complex = PureSymbol('is_complex')

