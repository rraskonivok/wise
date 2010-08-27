import string
import objects
from objects import Placeholder

from wise.worksheet.panel import TabularPanel, ArrayPanel
#@extends decorator to append to existing panel

lettervariables = [objects.Variable(letter) for letter in string.lowercase]
Variables = ArrayPanel(name='Variables',
                         objects=lettervariables)
