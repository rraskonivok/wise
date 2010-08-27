from wise.library_utils import *
from wise.library_utils import _

import objects

Placeholder = objects.Placeholder
Term = objects.Term

@Map( _( Placeholder , Term ) >> _( Term ) )
def PlaceholderSubstitute( ph, tm ):
    return tm, 'pass'

PlaceholderSubstitute.pretty = 'Substitute'
