from django import template
from wise.worksheet.utils import load_haml_template
from wise.packages.loader import load_package_module
Term = load_package_module('base','term').Term

def initialize():
    super_classes = [Integral]
    nullary_types = {}

    return super_classes, nullary_types

class Integral(Term):
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
        objects = [o.get_html() for o in self.terms]

        c = template.Context({
            'id': self.id,
            'integrand': self.integrand.get_html(),
            'variable': self.variable.get_html(),
            })

        return self.html.render(c)

