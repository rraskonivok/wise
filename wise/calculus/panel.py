import objects
from wise.worksheet.panel import TabularPanel, ArrayPanel

calculusobjs = [
        ('Derivative',objects.Diff),
        ('Integral', objects.Integral),
        ('Del', objects.Del)
        ]

Calculus = TabularPanel(name='Calculus',
                      objects=calculusobjs)
