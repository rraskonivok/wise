import string
import objects

from wise.worksheet.panel import TabularPanel, ArrayPanel
#TODO: @extends decorator to append to existing panel

lettervariables = [objects.Variable(letter) for letter in string.lowercase]
greek_alphabet = ['alpha', 'beta', 'gamma', 'delta', 'epsilon',
'varepsilon', 'zeta', 'eta', 'theta', 'vartheta', 'gamma',
'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'varpi', 'rho',
'varrho', 'sigma', 'varsigma', 'tau', 'upsilon', 'phi', 'varphi',
'chi', 'psi', 'omega', 'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi',
'Pi', 'Sigma', 'Upsilon', 'Phi', 'Psi', 'Omega']

greek_symbols = map(objects.Greek, greek_alphabet)

Variables = ArrayPanel(name='Variables',
                       objects=lettervariables)

Greeks = ArrayPanel(name='Greek',
                       objects=greek_symbols)

operations = [('Addition',objects.Addition),
              ('Multiplication',objects.Product),
              ('Power',objects.Power),
              ('Negate',objects.Negate),
              ('Rational',objects.Rational),
              ('Complex',objects.ComplexNumeric),
              ('Sign',objects.Sgn),
              ('Dirac Delta',objects.DiracDelta),
#              ('Abs',objects.Abs),
              ('Sqrt',objects.Sqrt),
              ('Sin',objects.Sin),
              ('Cos',objects.Cos),
              ('Tan',objects.Tan),
              ('Exp',objects.Exp),
              ('Ln',objects.Ln),
              ('Asin',objects.Asin),
              ('Acos',objects.Acos),
              ('Atan',objects.Atan),
              ('Sinh',objects.Sinh),
              ('Cosh',objects.Cosh),
              ('Tanh',objects.Tanh),
              ('Asinh',objects.Asinh),
              ('Acosh',objects.Acosh),
              ('Atanh',objects.Atanh),
              ('Gamma',objects.Gamma),
              ('Factorial',objects.Factorial),
              ('Zeta',objects.Zeta),
             ]

Operations = TabularPanel(name='Operations',
                          objects=operations)

constants = [('Imaginary Unit',objects.ImaginaryUnit),
              ('Catalan Number',objects.Catalan),
             ]

Constants = TabularPanel(name='Constants',
                          objects=constants)
