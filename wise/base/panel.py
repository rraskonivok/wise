import string
import objects

from objects import Placeholder
from wise.worksheet.panel import TabularPanel, ArrayPanel, ButtonPanel, TexButton
#TODO: @extends decorator to append to existing panel

##--------------------
## Letter Variables
##--------------------
#
letters = [letter for letter in string.lowercase]
lettervariables = map(objects.Variable, letters)
letter_buttons = zip(letters, lettervariables)

Variables = TexButton(name='Variables',
                       objects=letter_buttons)
#
#--------------------
# Greek Variables
#--------------------

# The greek alphabet... LaTeX style
greek_alphabet = ['alpha', 'beta', 'gamma', 'delta', 'epsilon',
'varepsilon', 'zeta', 'eta', 'theta', 'vartheta', 'gamma',
'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'varpi', 'rho',
'varrho', 'sigma', 'varsigma', 'tau', 'upsilon', 'phi', 'varphi',
'chi', 'psi', 'omega', 'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi',
'Pi', 'Sigma', 'Upsilon', 'Phi', 'Psi', 'Omega']

greek_symbols = map(objects.Greek, greek_alphabet)
greek_latex = ['\\' + s for s in greek_alphabet]
greek_buttons = zip(greek_latex, greek_symbols)

Greeks = TexButton(name='Greek',
                    objects=greek_buttons)

#--------------------
# Elementary Operations
#--------------------

elem_operations = [
              ('add.png',       objects.Addition),
              ('mul.png',       objects.Product),
              ('pow.png',       objects.Power),
              ('neg.png',       objects.Negate),
              ('div.png',       objects.Rational),
              ('complex.png',   objects.ComplexCartesian),
              ('sqrt.png',      objects.Sqrt),
              ('exp.png',       objects.Exp),
              ('log.png',  objects.Ln),
#              ('\\text{sgn}',objects.Sgn),
#              ('\\delta',objects.DiracDelta),
#              ('Abs',objects.Abs),
             ]

Operations = ButtonPanel(name='Algebraic Operations',
                         objects=elem_operations)
#
##-------------------------
## Trigonometric Operations
##-------------------------
#
#trig_operations = [('\\sin',objects.Sin),
#                   ('\\cos',objects.Cos),
#                   ('\\tan',objects.Tan),
#                   ('\\text{asin}',objects.Asin),
#                   ('\\text{acos}',objects.Acos),
#                   ('\\text{atan}',objects.Atan),
#                   ('\\text{sinh}',objects.Sinh),
#                   ('\\text{cosh}',objects.Cosh),
#                   ('\\text{tanh}',objects.Tanh),
#                   ('\\text{asinh}',objects.Asinh),
#                   ('\\text{acosh}',objects.Acosh),
#                   ('\\text{atanh}',objects.Atanh),
#                  ]
#
#TrigOperations = ButtonPanel(name='Trigonometric Functions',
#                              objects=trig_operations)
#
##-------------------------
## Number Theory Operations
##-------------------------
#
#numtheory_operations = [('\\Gamma',objects.Gamma),
#                        ('x!',objects.Factorial),
#                        ('\\zeta',objects.Zeta),
#                       ]
#
#NumTheoryOperations = ButtonPanel(name='Number Theory Functions',
#                                   objects=numtheory_operations)
#
##-------------------------
## Constants
##-------------------------
#
#constants = [('i',objects.ImaginaryUnit),
#             ('\\pi',objects.Pi),
#             ('(a,b)',objects.Tuple(Placeholder(),Placeholder())),
##             ('f(x)',objects.FunctionAppl(objects.Variable('f'),Placeholder())),
#             ('Quote',objects.Quote),
#             ('C_n',objects.Catalan),
#            ]
#
#Constants = ButtonPanel(name='Constants',
#                         objects=constants)
