from wise.worksheet.mathobjects import Base_Symbol, InfixOperation, PrefixOperation

class Diff(PrefixOperation):
    symbol = '\\frac{d}{dx}'
    show_parenthesis = False
    pure = 'diff'

# Note: "int" is a reserved keyword in Pure
class Del(PrefixOperation):
    symbol = '\\nabla'
    show_parenthesis = False
    pure = 'Del'

# Note: "int" is a reserved keyword in Pure
class Integral(PrefixOperation):
    symbol = '\\int'
    show_parenthesis = False
    pure = 'integral'
