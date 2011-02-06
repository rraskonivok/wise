from django.template import Template, Context
from wise.worksheet.panel import MathMLPanel

import objects
from utils import latex

# The instance of the panels is completely irrelevant, you can
# name them whatever you want. worksheet/panels.py extracts all
# instances of any sublcass of wise.worksheet.panel.Panel

#--------------------
# Elementary Operations
#--------------------

ops = (
        ('buttons/add.xml',       objects.Addition),
        ('buttons/mul.xml',       objects.Product),
        ('buttons/pow.xml',       objects.Power),
        ('buttons/neg.xml',       objects.Negate),
        ('buttons/div.xml',       objects.Rational),
        ('buttons/complex.xml',   objects.ComplexCartesian),
        ('buttons/sqrt.xml',      objects.Sqrt),
        ('buttons/exp.xml',       objects.Exp),
        ('buttons/log.xml',       objects.Ln),
        ('buttons/nroot.xml',     objects.NRoot),
        ('buttons/abs.xml',       objects.Abs),
)

Algebraic = MathMLPanel(name="Algebraic", objects=ops)

#-------------------------
# Matrix Operations
#-------------------------

def mat_constructor(rows, cols):
    return objects.Matrix(
        *( objects.MRow(
            *(objects.Placeholder(),)*rows
        ),) * cols
    )

mat_ops = (
    ('1x3', mat_constructor(1,3)),
    ('3x1', mat_constructor(3,1)),
    ('1x2', mat_constructor(1,2)),
    ('2x1', mat_constructor(2,1)),
    ('1x4', mat_constructor(1,4)),
    ('4x1', mat_constructor(4,1)),
    ('1x4', mat_constructor(1,4)),
    ('4x1', mat_constructor(4,1)),
    ('2x2', mat_constructor(2,2)),
    ('3x3', mat_constructor(3,3)),
)

Matrix = MathMLPanel(name="Matrix", objects=mat_ops,
        use_template='True')


#-------------------------
# Tensors
#-------------------------

generic_tensor = objects.AbstractTensor(
    objects.Variable('T'),
    objects.Idx(objects.Placeholder()),
    objects.Idx(objects.Placeholder())
)

tens_ops = (
    ('buttons/generic_tensor.xml', generic_tensor),
)

Tensor = MathMLPanel(name="Tensor", objects=tens_ops)

#-------------------------
# Trigonometric Operations
#-------------------------

trig_operations = (
        ('buttons/sin.xml',objects.Sin),
        ('buttons/cos.xml',objects.Cos),
        ('buttons/tan.xml',objects.Tan),
        ('buttons/sinh.xml',objects.Sinh),
        ('buttons/cosh.xml',objects.Cosh),
        ('buttons/tanh.xml',objects.Tanh),
        ('buttons/asin.xml',objects.Asin),
        ('buttons/acos.xml',objects.Acos),
        ('buttons/atan.xml',objects.Atan),
        ('buttons/asinh.xml',objects.Asinh),
        ('buttons/acosh.xml',objects.Acosh),
        ('buttons/atanh.xml',objects.Atanh),
)

Trig = MathMLPanel(name="Trigonometric", objects=trig_operations)

#-------------------------
# Number Theory Operations
#-------------------------

numtheory = (
        ('buttons/gamma.xml',objects.Gamma),
        ('buttons/zeta.xml',objects.Zeta),
        ('buttons/factorial.xml',objects.Factorial),
)

NumTheory = MathMLPanel(name='Number Theory', objects=numtheory)

#--------------------
# Variables
#--------------------

variable_template = Template('''
<math display="block" xmlns="http://www.w3.org/1998/Math/MathML">
    <mrow>
        <mn>{{symbol}}</mn>
    </mrow>
</math>
''')

def mml_var(symbol):
    return variable_template.render(
        Context({'symbol': symbol})
    )

def make_letters():
    letters = ['x','y','z','u','v','w','t','a','b','c']

    return [ (mml_var(symbol), objects.Variable(symbol)) for symbol in letters]

def make_greeks():
    return [ (mml_var(symbol), objects.Variable(letter)) for letter,
            symbol in latex.greek_unicode_list ]

Letters = MathMLPanel(name="Letters",
                      objects=make_letters(),
                      use_template=True)


Greeks = MathMLPanel(name="Greeks",
                     objects=make_greeks(),
                     use_template=True)
