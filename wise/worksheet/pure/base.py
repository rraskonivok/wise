from pure import *

print env.eval('using worksheet::pure::base')

ref = PureSymbol('wiseref')
refop = PureSymbol('wiserefop')

add = PureSymbol('add')
sub = PureSymbol('sub')
mul = PureSymbol('mul')
div = PureSymbol('div')
powr = PureSymbol('pow')
rational = PureSymbol('rational')
neg = PureSymbol('Neg')

sin = PureSymbol('Sin')
cos = PureSymbol('Cos')
tan = PureSymbol('Tan')
csc = PureSymbol('Csc')
sec = PureSymbol('Sec')
cot = PureSymbol('Cot')
sinh = PureSymbol('Sinh')
cosh = PureSymbol('Cosh')
tanh = PureSymbol('Tanh')

var = PureSymbol('var')
eq = PureSymbol('eq')

pluszero = PureSymbol('pluszero')
integral = PureSymbol('integral')
differential = PureSymbol('differential')
diff = PureSymbol('diff')

pi = PureSymbol('Pi')
e = PureSymbol('E')

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
