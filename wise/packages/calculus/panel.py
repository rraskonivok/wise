import objects
from wise.worksheet.panel import MathMLPanel

#--------------------
# Integral Operations
#--------------------

calc = (
        ('buttons/integral.xml',  objects.Integral),
        ('buttons/diff.xml',  objects.Diff),
)

Calculus = MathMLPanel(name="Calculus", objects=calc)

series = (
        ('Taylor',  objects.Taylor),
)

Series = MathMLPanel(name="Series", objects=series,
        use_template='True')
