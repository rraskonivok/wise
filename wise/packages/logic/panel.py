import objects
from wise.worksheet.panel import TabularPanel, ArrayPanel, ButtonPanel

logicsymbols = [('\\text{True}',objects.LogicTrue),
                ('\\text{False}', objects.LogicFalse),
                ('\\wedge',objects.And),
                ('\\vee',objects.Or),
                ('\\neg',objects.LogicNeg)]

Logic = ButtonPanel(name='Logic',
                    objects=logicsymbols)
