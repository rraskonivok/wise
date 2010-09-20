import objects
from wise.worksheet.panel import TabularPanel, ArrayPanel

logicsymbols = [objects.LogicTrue, objects.LogicFalse,
        objects.And, objects.Or, objects.LogicNeg]

Logic = ArrayPanel(name='Logic',
                   objects=logicsymbols)
