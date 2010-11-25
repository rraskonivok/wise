from wise.base.cell import Cell
from wise.base.term import Term

from math import modf

from wise.worksheet.utils import render_haml_to_response
from wise.translators.pure_wrap import PureSymbol, PureInt, PureDouble, ProtoRule, p2i, i2p

import worksheet.exceptions as exception
from worksheet.utils import *

from django import template

#-------------------------------------------------------------
# Top Level Elements
#-------------------------------------------------------------

class Relational(object):
    '''A statement relating some LHS to RHS'''
    pass

class Equation(object):
    html = load_haml_template('equation.tpl')

    lhs = None
    rhs = None
    id = None

    # Infix symbol placed between LHS and RHS
    symbol = "="

    side = None
    annotation = ''

    pure = 'eq'

    po = None

    # Database index
    sid = None

    def __init__(self,lhs=None,rhs=None):

        self.rhs = rhs
        self.lhs = lhs

        self.terms = [self.lhs, self.rhs]

    def get_math(self):
        return msexp(self, self.terms)

    @property
    def math(self):
        l1 = cats(self.classname, self.lhs.get_math(), self.rhs.get_math())
        return cat('(',l1,')')

    def __repr__(self):
         return self.math

    def _pure_(self):
        return self.po(self.lhs._pure_(),self.rhs._pure_())

    @property
    def classname(self):
        return self.__class__.__name__

    def set_side(self, side):
        for term in self.terms:
            term.side = side
            term.set_side(side)

    def json_flat(self,lst=None):
        if not lst:
            lst = []

        lst.append({'id': self.id,
                    'type': self.classname,
                    'toplevel': True,
                    'sid': self.sid,
                    'children': [term.id for term in self.terms]})

        for term in self.terms:
            term.json_flat(lst)

        return lst

    def get_html(self):

        c = template.Context({
            'id': self.id,
            'lhs': self.lhs.get_html(),
            'rhs': self.rhs.get_html(),
            'annotation': self.annotation,
            'symbol': self.symbol,
            'classname': self.classname
            })

        return self.html.render(c)

    def ensure_id(self):
        '''Make sure there is a unique id set, if there isn't
        make one, but never overwrite preexisting one'''

        if not self.id:
            self.id = self.idgen.next()

class Definition(Equation):
    symbol = ":="
    html = load_haml_template('def.tpl')
    confluent = True
    public = True
    pure = None

    def _pure_(self):
        lhs = self.lhs._pure_()
        rhs = self.rhs._pure_()

        return ProtoRule(lhs , rhs)

    def get_html(self):

        self.rhs.id = self.idgen.next()
        self.lhs.id = self.idgen.next()

        c = template.Context({
            'id': self.id,
            'lhs': self.lhs.get_html(),
            'rhs': self.rhs.get_html(),
            'annotation': self.annotation,
            'symbol': self.symbol,
            'confluent': int(self.confluent),
            'public': self.public,
            'classname': self.classname
            })

        return self.html.render(c)

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
            'math': self.math,
            'head': self.head.get_html(),
            'lhs': self.lhs.get_html(),
            'rhs': self.rhs.get_html(),
            'annotation': self.annotation,
            'symbol': self.symbol,
            'classname': self.classname
            })

        return self.html.render(c)
