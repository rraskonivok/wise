from objects import Placeholder, Term, FunctionAppl

def PlaceholderSubstitute( ph, tm ):
    return tm, 'pass'

def GenFunc( func, term ):
    return 'pass', FunctionAppl(func, Placeholder())

def Delete( first ):
    return Placeholder(),
