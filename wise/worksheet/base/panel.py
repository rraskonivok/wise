import string
import objects

from wise.worksheet.panel import TabularPanel, ArrayPanel
#TODO: @extends decorator to append to existing panel

lettervariables = [objects.Variable(letter) for letter in string.lowercase]
greek_alphabet = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'varepsilon', 'zeta', 'eta', 'theta', 'vartheta', 'gamma', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'varpi', 'rho', 'varrho', 'sigma', 'varsigma', 'tau ', 'upsilon', 'phi', 'varphi', 'chi', 'psi', 'omega']
greek_symbols = map(objects.Base_Symbol,greek_alphabet)

Variables = ArrayPanel(name='Variables',
                       objects=lettervariables)

Greeks = ArrayPanel(name='Greek',
                       objects=greek_symbols)

operations = [('Addition',objects.Addition),
              ('Multiplication',objects.Product),
              ('Exponent',objects.Power),
              ('Negate',objects.Negate),
              ('Division',objects.Fraction),
             ]

Operations = TabularPanel(name='Operations',
                          objects=operations)
