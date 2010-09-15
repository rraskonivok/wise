import objects
from wise.worksheet.panel import TabularPanel, ArrayPanel

logicsymbols = [objects.LogicTrue, objects.LogicFalse, objects.And]

Logic = ArrayPanel(name='Logic',
                   objects=logicsymbols)
