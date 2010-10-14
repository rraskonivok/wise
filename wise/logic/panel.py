import objects
from wise.worksheet.panel import TabularPanel, ArrayPanel

logicsymbols = [('True',objects.LogicTrue),
                ('False', objects.LogicFalse),
                ('And',objects.And),
                ('Or',objects.Or),
                ('Complement',objects.LogicNeg)]

Logic = TabularPanel(name='Logic',
                   objects=logicsymbols)
