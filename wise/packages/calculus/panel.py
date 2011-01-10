import objects
from wise.worksheet.panel import MathMLPanel

#--------------------
# Integral Operations
#--------------------

calc = (
        ('buttons/integral.xml',  objects.Integral),
)

Calculus = MathMLPanel(name="Calculus", objects=calc)
