# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
from django import template
from term import Term

import worksheet.exceptions as exception
from worksheet.utils import load_haml_template, purify, html

#-------------------------------------------------------------
# Operations
#-------------------------------------------------------------

class Operation(Term):
    """
    An generic operation acting on n>0 operands.
    """

    pure = None

    # Templates are assigned from 'ui_style':
    # * prefix  ~  base/templates/prefix.tpl
    # * postfix ~  base/templates/postfix.tpl
    # * infix   ~  base/templates/infix.tpl

    ui_style = 'prefix'
    symbol = None
    show_parenthesis = False
    arity = None

    def __init__(self,*operands):
        self.terms = list(operands)

        if len(operands) > 1:
            self.operand = self.terms
        elif len(operands) == 1:
            self.operand = self.terms[0]

        self.arity = len(self.terms)

    def _pure_(self):
        if self.po:
            return self.po(*purify(self.terms))
        else:
            raise exception.PureError('No pure representation of %s.' % self.classname)

    def get_html(self):

        #Infix Formatting
        if self.ui_style == 'infix':
            self.html = load_haml_template('infix.tpl')
            objects = [o.get_html() for o in self.terms]

            c = template.Context({
                'id': self.id,
                'type': self.classname,
                'operand': objects,
                'symbol': self.symbol,
                'parenthesis': self.show_parenthesis,
                })

            return self.html.render(c)

        #Outfix Formatting
        elif self.ui_style == 'outfix':
            self.html = load_haml_template('outfix.tpl')

            c = template.Context({
                'id': self.id,
                'type': self.classname,
                'operand': self.operand.get_html(),
                'symbol1': self.symbol1,
                'symbol2': self.symbol2,
                'parenthesis': self.show_parenthesis,
                })

            return self.html.render(c)

        #Prefix Formatting
        elif self.ui_style == 'prefix':
            objects = [o.get_html() for o in self.terms]

            c = template.Context({
                'id': self.id,
                'type': self.classname,
                'operand': objects,
                'symbol': self.symbol,
                'parenthesis': self.show_parenthesis,
                })

        #Postfix Formatting
        elif self.ui_style == 'postfix':
            self.html = load_haml_template('postfix.tpl')

            c = template.Context({
                'id': self.id,
                'type': self.classname,
                'operand': self.operand.get_html(),
                'symbol': self.symbol,
                'parenthesis': self.show_parenthesis,
                })

        #Superscript Formatting
        elif self.ui_style == 'sup':
            self.html = load_haml_template('sup.tpl')

            c = template.Context({
                'id': self.id,
                'type': self.classname,
                'operand': self.operand.get_html(),
                'symbol1': self.symbol1.get_html(),
                'parenthesis': self.show_parenthesis,
                })

        #Subscript Formatting
        elif self.ui_style == 'sub':
            self.html = load_haml_template('sub.tpl')

            c = template.Context({
                'id': self.id,
                'type': self.classname,
                'operand': self.operand.get_html(),
                'symbol1': self.symbol1,
                'parenthesis': self.show_parenthesis,
                })

        return self.html.render(c)

    def get_symbol(self):
        return self.symbol

    def has_single_term(self):
        if len(self.terms) == 1:
            return True

class PrefixOperation(Operation):
    html = load_haml_template('prefix.tpl')
    ui_style = 'prefix'
    show_parenthesis = True

class InfixOperation(Operation):
    ui_style = 'infix'

class PostfixOperation(Operation):
    ui_style = 'postfix'

class SupOperation(Operation):
    ui_style = 'sup'

class SubOperation(Operation):
    ui_style = 'sub'

class OutfixOperation(Operation):
    ui_style = 'outfix'
