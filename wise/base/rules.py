import wise.translators.pytopure as translate
import wise.translators.pure_wrap as pure_wrap
from wise.translators.pure_wrap import PureLevel, PureSymbol, reduce_with_pure_rules, PureClosure

class PublicRule:
    po = None
    ref = None

    def __init__(self, pure_symbol_name):
        self.ref = pure_symbol_name
        self.po = PureClosure(pure_symbol_name)
        pure_wrap.objects[pure_symbol_name] = self.po

        self.po.arity = pure_wrap.nargs(self.po)

    @property
    def description(self):
        return self.__doc__

# -------------------
# Equational Calculus
# -------------------

def eq_add():
    po = 'eq_div'

def eq_mul():
    po = 'eq_mul'

def eq_div():
    po = 'eq_div'

def eq_sub():
    po = 'eq_sub'

panel = {}

panel['Relational'] = [

        ('Add To Both Sides'        , PublicRule('eq_add')),
        ('Subtract From Both Sides' , PublicRule('eq_sub')),
        ('Multiply To Both Sides'   , PublicRule('eq_mul')),
        ('Divide Both Sides'        , PublicRule('eq_div')),
        ('Algebraic Normal Form'    , PublicRule('algebra_normal')),
        ('Commute Left'             , PublicRule('commute_left')),

    ]

panel['Commutative Algebra'] = [

        ('Commute Elementary'        , PublicRule('commute_elementary')),
        ('Expand Multiplication'     , PublicRule('algebra_expand')),
        ('Pull Left'                 , PublicRule('pull_left')),
        ('Pull Right'                , PublicRule('pull_right')),
        ('Pull Constants Left'       , PublicRule('pull_numeric_left')),
        ('Pull Constants Right'      , PublicRule('pull_numeric_right')),
        ('Iterate Left'              , PublicRule('iter_left')),

    ]

panel['Rational'] = [

        ('Split Rational'            , PublicRule('split_rational')),
        ('Combine Ratiional'         , PublicRule('combine_rational')),
        ('Seperate Ratiional'        , PublicRule('seperate_rational')),

    ]
