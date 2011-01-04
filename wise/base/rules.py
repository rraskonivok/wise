from wise.translators.pure_wrap import PublicRule

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
    """Reduce addition, multiplication, and division to the their
    respective normal forms.
    """
    pure = 'algebra_normal'

class commute_elementary(PublicRule):
    """Commute binary addition and multiplication."""
    pure = 'commute_elementary'

class algebra_expand(PublicRule):
    """Expand multiplication subject with the formula:
        $$ m \cdot (a+b) = m \cdot a + m \cdot b $$
    """
    pure = 'algebra_expand'

class pull_numeric_left(PublicRule):
    """Associate all numerical terms to the left."""
    pure = 'pull_numeric_left'

class pull_numeric_right(PublicRule):
    """Associate all numerical terms to the right."""
    pure = 'pull_numeric_right'

class iter_left(PublicRule):
    """Given a container as the first argument, associate the second
    argument (if it occurs inside the first argument) one element
    to the left
    """

    pure = 'iter_left'

panel['Commutative Algebra'] = [

        ('Algebraic Normal Form'     , algebra_normal),
        ('Commute Elementary'        , commute_elementary),
        ('Expand Multiplication'     , algebra_expand),
#        ('Pull Left'                 , PublicRule('pull_left')),
#        ('Pull Right'                , PublicRule('pull_right')),
        ('Pull Constants Left'       , pull_numeric_left),
        ('Pull Constants Right'      , pull_numeric_right),
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
    """
   Seperates rational expressions according to the rules:
   $$\\frac{a}{c} + \\frac{b}{c} =  \\frac{a+b}{c} $$
   """
    pure = 'combine_rational'

class seperate_rational(PublicRule):
    """
   Seperates rational expressions according to the rules:
   $$\\frac{a}{c}  = a \cdot \\frac{1}{c} $$
   """
    pure = 'seperate_rational'

panel['Rational'] = [

        ('Split Rational'            , split_rational),
        ('Combine Ratiional'         , combine_rational),
        ('Seperate Ratiional'        , seperate_rational),

    ]
