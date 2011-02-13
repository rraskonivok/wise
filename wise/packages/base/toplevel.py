from django import template
from worksheet.utils import *
from term import ph


#-------------------------------------------------------------
# Top Level Elements
#-------------------------------------------------------------

class Relation(object):
    """A statement relating two symbols (LHS, RHS)."""
    # Infix symbol placed between LHS and RHS
    symbol = None

    args = [] # Static arguments used to initialze object
    terms = []  # Term objects as arguments to
    parent = None

    id = None # The unique ID used to track the object clientside
    idgen = None # A instance of a uid generator

    lhs = None
    rhs = None

    annotation = ''
    toplevel = False

    # Database index
    sid = None

    # HTML / HAML template used to render object
    html = load_haml_template('relation.tpl')
    latex = None # LaTeX code used in rendering object
    css_class = None # Extra styling in addition to .term class
    show_parenthesis = False

    side = None # 0 if on LHS, 1 if on RHS

    # Note: If no pure property is specified the object is
    # entirely internal and cannot be used except in Python

    pure = None # A string containing the name symbol in Pure
    po = None # Reference to the type of object

    toplevel = True

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

        self.terms = [self.lhs, self.rhs]

    def _pure_(self):
        return self.po(self.lhs._pure_(),self.rhs._pure_())

    def get_math(self):
        return msexp(self, self.terms)

    @property
    def description(self):
        return self.__doc__

    @property
    def classname(self):
        return self.__class__.__name__

    @property
    def math(self):
        return self.get_math()

    def __repr__(self):
         return self.get_math()

    def get_html(self):

        c = template.Context({
            'id': self.id,
            'lhs': self.lhs.get_html(),
            'rhs': self.rhs.get_html(),
            'annotation': self.annotation,
            'symbol': self.symbol,
            'classname': self.classname,
            'css_class': self.css_class,
        })

        return self.html.render(c)

    def set_side(self, side):
        for term in self.terms:
            term.side = side
            term.set_side(side)

    def json_flat(self,lst=None):
        if not lst:
            lst = []

        if self.sid:
            resource_uri = '/api/exp/' + str(self.sid)
        else:
            resource_uri = None

        lst.append({'id': self.id,
                    'type': self.classname,
                    'toplevel': self.toplevel,
                    'resource_uri': resource_uri,
                    'sid': self.sid,
                    'children': [term.id for term in self.terms]})

        for term in self.terms:
            term.json_flat(lst)

        return lst

    def ensure_id(self):
        """Make sure there is a unique id set, if there isn't
        make one, but never overwrite preexisting one"""

        if not self.id:
            self.id = self.idgen.next()

    def uid_walk(self, uid, overwrite=False):
        """Walk the expression tree handing out uids to anyone
        who needs one
        """
        if overwrite or not self.id:
            self.id = uid.next()

        for term in self.terms:
            term.uid_walk(uid, overwrite)
        return self

class Equation(Relation):
    """This symbol represents the binary equality function.
    Equality is associative and commutative in both arguments.
    """
    symbol = '='
    pure = 'eq'
    toplevel = True

    def _pure_(self):
        return self.po(self.lhs._pure_(),self.rhs._pure_())

def EquationPrototype():
    return Equation(ph(), ph())

class Lt(Relation):
    symbol = '<'
    pure = 'lt'

class Gt(Relation):
    symbol = '>'
    pure = 'gt'

class Gte(Relation):
    symbol = '\\ge'
    pure = 'gte'

class Lte(Relation):
    symbol = '\\le'
    pure = 'lte'

class Neq(Relation):
    symbol = '\\neq'
    pure = 'neq'

class Approx(Relation):
    symbol = '\\approx'
    pure = 'approx'

class Definition(Relation):
    symbol = ':='

    def _pure_(self):
        lhs = self.lhs._pure_()
        rhs = self.rhs._pure_()

        return ProtoRule(lhs, rhs)

class Function(Equation):
    symbol = "\\rightarrow"
    html = load_haml_template('function.tpl')
    confluent = True
    public = True
    pure = None

    def __init__(self,head=None,lhs=None,rhs=None):

        self.head = head
        self.lhs = lhs
        self.rhs = rhs

        self.terms = [self.head, self.lhs, self.rhs]

    def _pure_(self):
        lhs = self.lhs._pure_()
        rhs = self.rhs._pure_()

        # TODO: replace this with a lambda (\x -> ) expression
        return ProtoRule(lhs , rhs)

    def get_html(self):

        c = template.Context({
            'id': self.id,
            'head': self.head.get_html(),
            'lhs': self.lhs.get_html(),
            'rhs': self.rhs.get_html(),
            'annotation': self.annotation,
            'symbol': self.symbol,
            'classname': self.classname
            })

        return self.html.render(c)
