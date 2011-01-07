import objects
from wise.worksheet.panel import TabularPanel, ArrayPanel, ButtonPanel

calculusobjs = [
        ('\\frac{d}{dx}',objects.Diff),
        ('\\int', objects.Integral),
        ('\\nabla', objects.Del)
        ]

Calculus = ButtonPanel(name='Calculus',
                      objects=calculusobjs)
