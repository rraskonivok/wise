import string
import objects

from objects import Placeholder
from wise.worksheet.panel import MathMLPanel

from utils import latex
from django.template import Template, Context

#TODO: @extends decorator to append to existing panel

#--------------------
# Elementary Operations
#--------------------

ops = [
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
      ]

Algebraic = MathMLPanel(name="Algebraic", objects=ops)

#-------------------------
# Trigonometric Operations
#-------------------------

trig_operations = [('buttons/sin.xml',objects.Sin),
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
                  ]

Trig = MathMLPanel(name="Trigonometric", objects=trig_operations)

#-------------------------
# Number Theory Operations
#-------------------------

numtheory = [('buttons/gamma.xml',objects.Gamma),
             ('buttons/zeta.xml',objects.Zeta),
             ('buttons/factorial.xml',objects.Factorial),
            ]

NumTheoryOperations = MathMLPanel(name='Number Theory',
                                  objects=numtheory)

#--------------------
# Letter Variables
#--------------------

#--------------------
# Greek Variables
#--------------------

greek_template = Template('''
<math display="block" xmlns="http://www.w3.org/1998/Math/MathML">
    <mrow>
        <mn>{{symbol}}</mn>
    </mrow>
</math>
''')

greeks = []

for letter, symbol in latex.greek_unicode_list:
    mml = greek_template.render(Context({'symbol':symbol}))
    greeks.append( (mml, objects.Variable(letter)) )

Greeks = MathMLPanel(name="Greeks", objects=greeks,
        use_template=True)
