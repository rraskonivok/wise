import string
import objects

from objects import Placeholder
from wise.worksheet.panel import TabularPanel, ArrayPanel, \
ButtonPanel, MathMLPanel

#TODO: @extends decorator to append to existing panel

##--------------------
## Letter Variables
##--------------------

#letters = [letter for letter in string.lowercase]
#lettervariables = map(objects.Variable, letters)
#letter_buttons = zip(letters, lettervariables)
#
#Variables = TexButton(name='Variables',
#                       objects=letter_buttons)
#
#--------------------
# Greek Variables
#--------------------

# The greek alphabet... LaTeX style
#greek_alphabet = ['alpha', 'beta', 'gamma', 'delta', 'epsilon',
#'varepsilon', 'zeta', 'eta', 'theta', 'vartheta', 'gamma',
#'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'varpi', 'rho',
#'varrho', 'sigma', 'varsigma', 'tau', 'upsilon', 'phi', 'varphi',
#'chi', 'psi', 'omega', 'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi',
#'Pi', 'Sigma', 'Upsilon', 'Phi', 'Psi', 'Omega']
#
#greek_symbols = map(objects.Greek, greek_alphabet)
#greek_latex = ['\\' + s for s in greek_alphabet]
#greek_buttons = zip(greek_latex, greek_symbols)
#
#Greeks = TexButton(name='Greek',
#                    objects=greek_buttons)

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
