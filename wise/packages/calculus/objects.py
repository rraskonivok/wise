from django import template
from wise.worksheet.utils import load_haml_template
from wise.packages.loader import load_package_module
from wise.worksheet.utils import purify
base_objects = load_package_module('base','objects')

def initialize():
    super_classes = [Integral, Diff, Taylor]
    nullary_types = {}

    return super_classes, nullary_types

class Integral(base_objects.Term):
    """
    This symbol is used to represent indefinite integration of
    unary functions. The first argument is the unary function the
    second argument is a variable of integration.
    """

    show_parenthesis = True
    html = load_haml_template('integral.tpl')
    pure = 'integrate'

    def __init__(self, f, dx):
        self.integrand = f
        self.variable = dx
        self.terms = [f, dx]

    def _pure_(self):
        return self.po(self.integrand._pure_(),self.variable._pure_())

    def get_html(self):
        c = template.Context({
            'id': self.id,
            'integrand': self.integrand.get_html(),
            'variable': self.variable.get_html(),
            })

        return self.html.render(c)

class Diff(base_objects.Term):
    """
    This symbol is used to represent indefinite integration of
    unary functions. The first argument is the unary function the
    second argument is a variable of integration.
    """

    show_parenthesis = True
    html = load_haml_template('diff.tpl')
    pure = 'diff'

    def __init__(self, f, dx):
        self.operand = f
        self.variable = dx
        self.terms = [f, dx]

    def _pure_(self):
        return self.po(self.operand._pure_(),self.variable._pure_())

    def get_html(self):
        c = template.Context({
            'id': self.id,
            'operand': self.operand.get_html(),
            'variable': self.variable.get_html(),
        })

        return self.html.render(c)

class Taylor(base_objects.Term):
    """
    This symbol represents the exponentiation function.
    """
    symbol = 'Taylor'
    pure = 'Taylor'
    html = load_haml_template('funcapp.tpl')

    def __init__(self, f, x, x0, n):
        self.terms = [f,x,x0,n]

    def _pure_(self):
        return self.po(*purify(self.terms))

    def get_html(self):
        objects = [o.get_html() for o in self.terms]

        c = template.Context({
            'id': self.id,
            'operand': objects,
            'symbol': self.symbol,
            'type': self.classname,
            'operand': objects,
        })

        return self.html.render(c)
