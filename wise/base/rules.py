import wise.translators.pytopure as translate
import wise.translators.pure_wrap as pure_wrap
from wise.translators.pure_wrap import PureLevel, PureSymbol, reduce_with_pure_rules, PureClosure

from wise.worksheet.utils import trim_docstring

class PublicRule:
    po = None
    ref = None
    arity = -1
    pure = None

    def __init__(self, pure_symbol_name):
        self.pure = pure_symbol_name
        self.ref = self.pure
        self.po = PureClosure(self.pure)
        pure_wrap.objects[self.pure] = self.po

        self.po.arity = pure_wrap.nargs(self.po)

    @property
    def description(self):
        return self.__doc__

    @classmethod
    def register(self):
        if self.pure:

            if hasattr(self,'__doc__') and self.__doc__:
                self.desc = trim_docstring(self.__doc__)
            else:
                self.desc = 'No description available'

            self.po = PureClosure(self.pure)
            pure_wrap.objects[self.pure] = self.po

# Toplevel Panel dictionary, must be called 'panel'

panel = {}

# -------------------
# Relational Calculus
# -------------------

class eq_add(PublicRule):
    """Add second argument to the equation given in the first
    argument.
    """

    pure = 'eq_add'

class eq_mul(PublicRule):
    """Multiply second argument to the equation given in the first
    argument.
    """
    pure = 'eq_mul'

class eq_div(PublicRule):
    """Divide second argument to the equation given in the first
    argument.
    """
    pure = 'eq_div'

class eq_sub(PublicRule):
    """Subtract second argument to the equation given in the first
    argument.
    """
    pure = 'eq_sub'


panel['Relational'] = [

        ('Add To Both Sides'        , eq_add),
        ('Subtract From Both Sides' , eq_sub),
        ('Multiply To Both Sides'   , eq_mul),
        ('Divide Both Sides'        , eq_div),

    ]

# -------------------
# Commutative Algebra
# -------------------

class algebra_normal(PublicRule):
    """Subtract second argument to the equation given in the first
    argument.
    """
    pure = 'algebra_normal'

class commute_elementary(PublicRule):
    pure = 'commute_elementary'

class algebra_expand(PublicRule):
    pure = 'algebra_expand'

class pull_numeric_left(PublicRule):
    pure = 'pull_numeric_left'

class pull_numeric_right(PublicRule):
    pure = 'pull_numeric_right'

class iter_left(PublicRule):
    pure = 'iter_left'

panel['Commutative Algebra'] = [

        ('Algebraic Normal Form'     , algebra_normal),
        ('Commute Elementary'        , commute_elementary),
        ('Expand Multiplication'     , algebra_expand),
#        ('Pull Left'                 , PublicRule('pull_left')),
#        ('Pull Right'                , PublicRule('pull_right')),
        ('Pull Constants Left'       , pull_numeric_right),
        ('Pull Constants Right'      , pull_numeric_left),
        ('Iterate Left'              , iter_left),

    ]

# -------------------
# Rational 
# -------------------

class split_rational(PublicRule):
    """
   Seperates rational expressions according to the rules:
   $$\\frac{a+b}{c} = \\frac{a}{c} + \\frac{b}{c}$$
   """

    pure = 'split_rational'

class combine_rational(PublicRule):
    pure = 'combine_rational'

class seperate_rational(PublicRule):
    pure = 'seperate_rational'

panel['Rational'] = [

        ('Split Rational'            , split_rational),
        ('Combine Ratiional'         , combine_rational),
        ('Seperate Ratiional'        , seperate_rational),

    ]
