from wise.translators.pure_wrap import PublicRule

# Toplevel Panel dictionary, must be called 'panel'

panel = {}

# -------------------
# Evaluations
# -------------------

class evals(PublicRule):
    """
    Evaluate the expression to alternative symbolic form.
    """

    pure = 'evals'

class evalf(PublicRule):
    """
    Evaluate the expression to floating point value.
    """

    pure = 'evalf'

panel['Evaluations'] = (

        ('Evaluate Symbolically'    , evals),
        ('Evaluate Float'           , evalf),

)

# -------------------
# Matrix Operations
# -------------------

class transpose(PublicRule):
    """
    Evaluate the expression to floating point value.
    """
    pure = 'transpose'

# -------------------
# Indical Operations
# -------------------

class incrows(PublicRule):
    """
    Evaluate the expression to floating point value.
    """
    pure = 'incrows'

class inccols(PublicRule):
    """
    Evaluate the expression to floating point value.
    """
    pure = 'inccols'

class addcvi(PublicRule):
    """
    Evaluate the expression to floating point value.
    """
    pure = 'addcvi'

class addcoi(PublicRule):
    """
    Evaluate the expression to floating point value.
    """
    pure = 'addcoi'

panel['Indices'] = (

        ('Increment Rows',         incrows),
        ('Increment Columns',      inccols),
        ('Add Covariant Index'    , addcvi),
        ('Add Contraviarnt Index' , addcoi),

)

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


panel['Relational'] = (

        ('Add To Both Sides'        , eq_add),
        ('Subtract From Both Sides' , eq_sub),
        ('Multiply To Both Sides'   , eq_mul),
        ('Divide Both Sides'        , eq_div),

)

# -------------------
# Commutative Algebra
# -------------------

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

panel['Commutative Algebra'] = (

        ('Commute Elementary'        , commute_elementary),
        ('Expand Multiplication'     , algebra_expand),
#        ('Pull Left'                 , PublicRule('pull_left')),
#        ('Pull Right'                , PublicRule('pull_right')),
        ('Pull Constants Left'       , pull_numeric_left),
        ('Pull Constants Right'      , pull_numeric_right),
        ('Iterate Left'              , iter_left),

)

# -------------------
# Trigonometry
# -------------------

# -------------------
# Rational
# -------------------

class split_rational(PublicRule):
   """
   """
   pure = 'split_rational'

class combine_rational(PublicRule):
   """
   """
   pure = 'combine_rational'

class seperate_numerator(PublicRule):
   """
   """
   pure = 'seperate_numerator'

class simplify_rational(PublicRule):
    """
    """
    pure = 'simplify_rational'

class rationalize(PublicRule):
    """
    """
    pure = 'rationalize'

class make_rational(PublicRule):
    """
    """
    pure = 'make_rational'

panel['Rational'] = (
        ('Make Rational'               , make_rational)      ,
        ('Split Rational'              , split_rational)     ,
        ('Combine Rational'            , combine_rational)   ,
        ('Seperate Numerator'          , seperate_numerator) ,
        ('Convert to Numeric Fraction' , seperate_numerator) ,
        ('Simplify Rational'           , simplify_rational)  ,
        ('Rationalize'                 , rationalize)        ,
)

# -------------------
# Simplification
# -------------------

class algebra_normal(PublicRule):
    """Reduce addition, multiplication, and division to the their
    respective normal forms.
    """
    pure = 'algebra_normal'

class simplify_trig(PublicRule):
    """Reduce addition, multiplication, and division to the their
    respective normal forms.
    """
    pure = 'simplify_trig'

panel['Simplification'] = (
        ('Simplify Trig Functions'   , simplify_trig),
        ('Algebraic Normal Form'     , algebra_normal),
)
