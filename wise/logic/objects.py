from wise.worksheet.mathobjects import Base_Symbol, InfixOperation, PrefixOperation

class LogicTrue(Base_Symbol):
    latex = '\\text{True}'
    symbol = 'true'
    pure = 'True'
    args = "'true'"

class LogicFalse(Base_Symbol):
    latex = '\\text{False}'
    symbol = 'false'
    pure = 'False'
    args = "'false'"

    def __pure__(self):
        return self.po()

class And(InfixOperation):
    symbol = '\\wedge'
    show_parenthesis = True
    pure = 'And'

    def __init__(self,fst,snd):
        self.terms = list([fst,snd])

class Or(InfixOperation):
    symbol = '\\vee'
    show_parenthesis = True
    pure = 'Or'

    def __init__(self,fst,snd):
        self.terms = list([fst,snd])

class LogicNeg(PrefixOperation):
    symbol = '\\neg'
    show_parenthesis = True
    pure = 'LogicNeg'
