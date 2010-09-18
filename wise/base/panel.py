import string
import objects

from wise.worksheet.panel import TabularPanel, ArrayPanel
#TODO: @extends decorator to append to existing panel

#--------------------
# Letter Variables
#--------------------

lettervariables = [objects.Variable(letter) for letter in string.lowercase]

Variables = ArrayPanel(name='Variables',
                       objects=lettervariables)

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


Greeks = ArrayPanel(name='Greek',
                    objects=greek_symbols)

#--------------------
# Elementary Operations
#--------------------

elem_operations = [('Addition',objects.Addition),
              ('Multiplication',objects.Product),
              ('Power',objects.Power),
              ('Negate',objects.Negate),
              ('Rational',objects.Rational),
              ('Complex',objects.ComplexNumeric),
              ('Sign',objects.Sgn),
              ('Dirac Delta',objects.DiracDelta),
#              ('Abs',objects.Abs),
              ('Sqrt',objects.Sqrt),
              ('Exp',objects.Exp),
              ('Ln',objects.Ln),
#              ('Gamma',objects.Gamma),
#              ('Factorial',objects.Factorial),
#              ('Zeta',objects.Zeta),
             ]

Operations = TabularPanel(name='Algebraic Operations',
                          objects=elem_operations)

#-------------------------
# Trigonometric Operations
#-------------------------

trig_operations = [('Sin',objects.Sin),
                   ('Cos',objects.Cos),
                   ('Tan',objects.Tan),
                   ('Asin',objects.Asin),
                   ('Acos',objects.Acos),
                   ('Atan',objects.Atan),
                   ('Sinh',objects.Sinh),
                   ('Cosh',objects.Cosh),
                   ('Tanh',objects.Tanh),
                   ('Asinh',objects.Asinh),
                   ('Acosh',objects.Acosh),
                   ('Atanh',objects.Atanh),
                  ]

TrigOperations = TabularPanel(name='Trigonometric Functions',
                              objects=trig_operations)

#-------------------------
# Number Theory Operations
#-------------------------

numtheory_operations = [('Gamma',objects.Gamma),
                        ('Factorial',objects.Factorial),
                        ('Zeta',objects.Zeta),
                       ]

NumTheoryOperations = TabularPanel(name='Number Theory Functions',
                                   objects=numtheory_operations)

#-------------------------
# Constants
#-------------------------

constants = [('Imaginary Unit',objects.ImaginaryUnit),
             ('Catalan Number',objects.Catalan),
            ]

Constants = TabularPanel(name='Constants',
                         objects=constants)
