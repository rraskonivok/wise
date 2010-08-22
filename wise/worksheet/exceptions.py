class ParseError(Exception):
    def __init__(self,expr):
        self.value = expr

    def __str__(self):
        return self.value

class InternalMathObjectNotFound(Exception):
    def __init__(self,expr):
        self.value = 'Could not find class: ',expr.type

    def __str__(self):
        return self.value

class PureError(Exception):
    def __init__(self,expr):
        self.value = expr

    def __str__(self):
        return self.value

class PlaceholderInExpression(Exception):
    def __init__(self):
        self.value = 'A Placeholder was found in the equation and cannot be evaluated'

    def __str__(self):
        return self.value

class NoWrapper(Exception):
    def __init__(self,expr):
        self.value = "No translation for %s" % expr

    def __str__(self):
        return self.value
