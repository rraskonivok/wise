from wise.base.objects import Term

def initialize():
    super_classes = [LogicalOperator,LogicTrue,LogicFalse]

    nullary_types = {
        'true' : LogicTrue,
        'false' : LogicFalse,
    }

    return super_classes, nullary_types

class LogicTrue(Term):
    latex = '\\text{True}'
    symbol = 'true'
    pure = 'True'
    args = "'true'"

class LogicFalse(Term):
    latex = '\\text{False}'
    symbol = 'false'
    pure = 'False'
    args = "'false'"

    def __pure__(self):
        return self.po()

class LogicalOperator(Term):
    pass

class And(LogicalOperator):
    symbol = '\\wedge'
    show_parenthesis = True
    pure = 'And'

    def __init__(self,fst,snd):
        self.terms = list([fst,snd])

class Or(LogicalOperator):
    symbol = '\\vee'
    show_parenthesis = True
    pure = 'Or'

    def __init__(self,fst,snd):
        self.terms = list([fst,snd])

class LogicNeg(LogicalOperator):
    symbol = '\\neg'
    show_parenthesis = False
    pure = 'LogicNeg'
