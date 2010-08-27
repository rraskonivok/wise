# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import worksheet.js as js
import worksheet.exceptions
from worksheet.utils import *

#from worksheet.mathobjects import *

from django import template
from django.utils.safestring import SafeUnicode

term_html = haml('''
#{{id}}.{{class}}.{{sensitive}}.term math="{{math}}" math-type="{{type}}" title="{{type}}" math-meta-class="term" group="{{group}}"
    .noselect
        ${{latex}}$
''')

class Term(object):

    args = None

    latex = '$Error$'
    is_negative = False
    html = template.Template(term_html)
    javascript_template = js.javascript_template
    group = None
    css_class = ''
    id = None
    terms = []
    javascript = SafeUnicode()
    has_sort = False

    _is_constant = False
    idgen = None
    parent = None
    side = None # 0 if on LHS, 1 if on RHS
    pure = None # The symbol used in pure expression
    po = None   # Reference to the type of object

    def __init__(self,*ex):
        print 'Anonymous Term was caught with arguments',ex

    #############################################################
    ######### Essential Methods for All Math Objects ############
    #############################################################

    # Every interaction between Math Objects requires that these
    # methods exist

    def _pure_(self):
        raise PureError('No pure representation of %s.' % self.classname)

    def _latex_(self):
        raise PureError('No LaTeX representation of %s.' % self.classname)

    def get_html(self):
        c = template.Context({
            'id': self.id,
            'class': self.css_class,
            'sensitive':self.get_sensitive(),
            'latex':self.latex,
            'math': self.get_math(),
            'type': self.classname,
            'group': self.group
            })

        if self.javascript:
            return self.html.render(c) + self.get_javascript()
        else:
            return self.html.render(c)

    def get_math(self):
        '''This generates the sexp that is parsable on the Javascript side'''

        #Container-type Objects, Example: (Addition 1 2 3)
        if len(self.terms) > 1:
            return '(' + self.classname + ' ' + spaceiter(map(lambda o: o.get_math(), self.terms)) + ')'
        #Term-type Objects Example: (Numeric 3)
        elif len(self.terms) == 1:
            return '(' + self.classname + ' ' + self.terms[0].get_math() + ')'
        #Terms with primitve arguments (no nested sexp)
        else:
            return '(' + self.classname + ' ' + str(self.args) + ')'

    def __repr__(self):
         return self.get_math()

    def set_side(self, side):
        for term in self.terms:
            term.side = side
            term.set_side(side)

    #############################################################

    #These can (and often should) be overloaded
    def __add__(self,other):
        return Addition(*[self,other])

    def __mul__(self,other):
        return Product(*[self,other])

    def wrap(self,other):
        '''Take one object and wrap it in container object, return
        the container'''
        return other(self)

    def get_sensitive(self):
        if self.sensitive is False:
            return 'ui-state-disabled'
        else:
            return ''

    def ensure_id(self):
        '''Make sure there is a unique id set, if there isn't
        make one, but never overwrite preexisting one'''

        if not self.id:
            self.id = self.idgen.next()
        self.associate_terms()

    def associate_terms(self):
        '''Iterate through any child terms and associate their
        group property with the id of thet parent'''
        for term in self.terms:
            term.group = self.id

    def negate(self):
        return Negate(self)

    @property
    def classname(self):
        return self.__class__.__name__

    def map_recursive(self,function):
        '''Apply a function to self and all descendants'''
        function(self)
        for term in self.terms:
            term.map_recursive(function)

    def json_flat(self,lst=None):
        if not lst:
            lst = []

        lst.append({"id": self.id,
                    "type": self.classname,
                    "children": [term.id for term in self.terms]})

        for term in self.terms:
            term.json_flat(lst)

        return lst

    def get_javascript(self):
        c = template.Context({'javascript':self.javascript})
        return self.javascript_template.render(c)

    def combine_fallback(self,other,context):
        '''Just slap an operator between two terms and leave it as is'''

        # This differs slightly from the the transformations called on
        # expressions in that we return both the json and the
        # html for the new object, the reason being that often
        # include syntatic sugar in the response sent to the
        # client 

        if context == 'Addition':
            if isinstance(other,Term):

                if type(other) is Negate:
                    # Don't add a plus sign if we have a negation
                    # to avoid verbose expressions like 3 + -4
                    result = self.get_html() + other.get_html()

                elif type(other) is Numeric:
                    if other.is_zero():
                        result = self.get_html()
                        other = None;
                    else:
                        result = self.get_html() + infix_symbol_html(Addition.symbol) + other.get_html()

                else:
                    result = self.get_html() + infix_symbol_html(Addition.symbol) +  other.get_html()

                return result,[self,other]

        elif context == 'Product':
            if isinstance(other,Term):
                result = self.get_html() + infix_symbol_html(Product.symbol) +  other.get_html()
                return result,[self,other]

        elif context == 'Wedge':
            if isinstance(other,Term):
                result = self.get_html() + infix_symbol_html(Wedge.symbol) +  other.get_html()
                return result,[self,other]

    def combine(self,other,context):
        return self.combine_fallback(other,context)

    def ui_id(self):
        '''Returns the jquery code to reference to the html tag'''
        return '$("#workspace").find("#%s")' % (self.id)

    def ui_sortable(self,other=None):
        self.ensure_id()
        other.ensure_id()

        self.has_sort = True
        #TODO: add support for binding callbacks to python methods... later
        self.javascript = js.make_sortable(self,other).get_html()
        return self.get_javascript()


placeholder_html = haml('''
#{{id}} {{class}} .{{sensitive}} .drag_placeholder .term math="{{math}}" math-type="{{type}}" title="{{type}}" math-meta-class="term" group="{{group}}"
    span.empty
''')

class Placeholder(Term):
    '''A placeholder for substitution'''

    sensitive = False
    html = template.Template(placeholder_html)

    def __init__(self):
        self.latex = '$\\text{Placeholder}$'

    def _pure_(self):
        raise exceptions.PlaceholderInExpression()

    def get_math(self):
        return '(Placeholder )'

class Empty(Term):
    sensitive = False
    def __init__(self):
        self.latex = '$\\text{Empty}$'

    def get_math(self):
        return 'Empty'

    def combine(self,other,context):
        return other.get_html()

#-------------------------------------------------------------
# Lower Level Elements 
#-------------------------------------------------------------

class Text(Term):
    type = 'text'
    sensitive = True

    def __init__(self,text):
        self.latex = '\\text{' + text + '}'

pureblob_template = '''
div
    img src="/static/pure.png" style="vertical-align: middle"
    Pure Blob - <em>{{annotation}}</em>
'''

class PureBlob(Term):
    '''Pure code with no internal representation, Pure Blob'''
    def __init__(self):
        pass

    def get_html(self):
        c = template.Context({'annotation': self.annotation})

        return template.Template(pureblob_template).render(c)

tex_template = '''
.operator math-type="operator" math-meta-class="operator" group="{{group}}" title="{{type}}"
    $${{tex}}$$

'''

class Tex(object):
    '''LaTeX sugar for operators'''
    tex = None

    def __init__(self,tex):
        self.tex = tex

    def get_html(self):
        c = template.Context({
            'group': self.group,
            'type': 'Tex',
            'tex': self.tex})

        return template.Template(tex_template).render(c)

greek_alphabet = {
        'alpha': '\\alpha',
        'beta': '\\beta',
        'gamma': '\\gamma',
        'delta': '\\delta',
        'epsilon': '\\varepsilon',
        'pi': '\\pi',
        }

def greek_lookup(s):
    try:
        return greek_alphabet[s]
    except KeyError:
        return s

class Base_Symbol(Term):
    sensitive = True

    def __init__(self,symbol):
        self.args = "'%s'" % symbol
        self.symbol = greek_lookup(symbol)
        self.latex = greek_lookup(symbol)

    def _pure_(self):
        return pure.var(self.symbol)

class Greek(Base_Symbol):
    sensitive = True
    def __init__(self,symbol):
        self.symbol = symbol
        self.args = "'%s'" % symbol

#A free variable
class Variable(Base_Symbol):
    assumptions = None
    bounds = None
    pure = 'var'

    def __init__(self,symbol):
        self.symbol = symbol
        self.latex = '$%s$' % symbol
        self.args = str(symbol)

    def _pure_(self):
        return pure.PureSymbol(self.symbol)

#Free abstract function (of a single variable at this time)
class FreeFunction(Base_Symbol):
    assumptions = None
    bounds = None

    def __init__(self,symbol):
        self.symbol = symbol
        self.latex = '$%s(u)$' % symbol
        self.args = str(symbol)

    def _pure_(self):
        #LHS
        if self.side is 0:
            return pure.PureSymbol(self.symbol + '@_')(pure.PureSymbol('u'))
        #RHS
        else:
            return pure.PureSymbol(self.symbol)(pure.PureSymbol('u'))

class Wildcard(Variable):
    def _pure_(self):
        return pure.PureSymbol('_')

#Reference to a user-defined symbol
class RefSymbol(Variable):
    assumptions = None
    bounds = None

    def __init__(self, obj):
        if isinstance(obj, unicode) or isinstance(obj,str):
            obj = Symbol.objects.get(id=int(obj))

        if isinstance(obj, Numeric):
            obj = Symbol.objects.get(id=obj.number)

        self.symbol = obj.tex
        self.latex = '$%s$' % self.symbol
        self.args = str(obj.id)

    def _pure_(self):
        return pure.ref(pure.PureInt(int(self.args)))

fraction_html = haml('''
#{{id}}.fraction.container math-meta-class="term" math-type="{{type}}" group="{{group}}"

    .num
        {{num}}

    .den
        {{den}}

''')

class Fraction(Term):
    type = "Fraction"
    sensitive = True
    html = template.Template(fraction_html)
    pure = 'rational'

    def __init__(self,num,den):
        self.num = num
        self.den = den
        self.den.css_class = 'middle'
        self.terms = [num,den]

    def _pure_(self):
       return pure.po(self.num._pure_(), self.den._pure_())

    def get_html(self):
        self.num.group = self.id
        self.den.group = self.id

        c = template.Context({
            'id': self.id,
            'math': self.get_math(),
            'num': self.num.get_html(),
            'den': self.den.get_html(),
            'group': self.group,
            'type': self.classname
            })

        return self.html.render(c)

    @fallback(Term.combine_fallback)
    def combine(self,other,context):
        pass
        #TODO: This breaks a heck of a lot
        #if isinstance(other,Fraction):
        #    num = Addition(Product(self.num,other.den),Product(self.den,other.num))
        #    den = Product(self.den,other.den)
        #    return Fraction(num,den).get_html()
        #elif isinstance(other,Numeric):
        #    num = Addition(self.num,Product(self.den,other))
        #    den = self.den
        #    return Fraction(num,den).get_html()

class Numeric(Term):
    type = 'numeric'
    sensitive = True
    _is_constant = True

    def __init__(self,number):

        # TODO We shouldn't assume integers
        self.number = int(number)
        self.args = str(number)
        self.latex = number

    def _pure_(self):
        return pure.PureInt(self.number)

    def get_html(self):
        c = template.Context({
            'id': self.id,
            'class': self.css_class,
            'sensitive':self.get_sensitive(),
            'latex':self.latex,
            'math': self.get_math(),
            'type': self.classname,
            'group': self.group})

        return self.html.render(c)

    def is_zero(self):
        return self.number == 0

    def is_one(self):
        return self.number == 1

    def negate(self):
        #Zero is its own negation
        if self.is_zero():
            return self
        else:
            return Negate(self)

    @fallback(Term.combine_fallback)
    def combine(self,other,context):
        if context == 'Addition':
            if self.is_zero():
                result = other.get_html()
                return result,[self,other]
            elif isinstance(other,Numeric):
                result = Numeric(self.number + other.number).get_html()
                return result,[self,other]

        elif context == 'Product':
            if isinstance(other,Numeric):
                if self.is_zero():
                    return self.get_html()
                if self.is_one():
                    return other.get_html()
                else:
                    return Numeric(self.number * other.number).get_html()

            elif isinstance(other,Base_Symbol):
                #Multiplication by zero clears symbols
                if self.is_zero():
                    return self.get_html()

#Constants should be able to be represented by multiple symbols
class Constant(Term):
    sensitive = True
    representation = None

    def __init__(self,*symbol):
        self.args = self.representation.args
        self.latex = self.representation.latex

def Zero():
    return Numeric(0)

def One():
    return Numeric(1)

#-------------------------------------------------------------
# Top Level Elements
#-------------------------------------------------------------

equation_html = haml('''
    tr#{{id}}.equation math="{{math}}" math-type="{{classname}}" toplevel="true"
        td
            button.ui-icon.ui-icon-triangle-1-w onclick="select_term(get_lhs(this))"
                {{lhs_id}}

            button.ui-icon.ui-icon-triangle-2-e-w onclick="select_term(get_equation(this))"
                {{id}}

            button.ui-icon.ui-icon-triangle-1-e onclick="select_term(get_rhs(this))"
                {{rhs_id}}

        td
            {{lhs}}

        td.equalsign
           $${{symbol}}$$

        td
            {{rhs}}

        td.guard 
            {{guard}}

        td.annotation
            div contenteditable=true
                {{annotation}}
''')

class Equation(object):
    '''A statement relating some LHS to RHS'''
    lhs = None
    rhs = None
    html = template.Template(equation_html)
    id = None
    symbol = "="
    sortable = True
    parent = None
    side = None
    annotation = ''
    pure = 'eq'
    po = None

    def __init__(self,lhs=None,rhs=None):

        # Conviencence definition so that we can call Equation()
        # to spit out an empty equation
        if not lhs:
            lhs = LHS(Placeholder())
        if not rhs:
            rhs = RHS(Placeholder())

        if not isinstance(lhs,LHS):
            lhs = LHS(lhs)

        if not isinstance(rhs,RHS):
            rhs = RHS(rhs)

        self.rhs = rhs
        self.lhs = lhs

        self.terms = [self.rhs, self.lhs]

    @property
    def math(self):
        l1 =' '.join([self.classname, self.lhs.get_math(), self.rhs.get_math()])
        return ''.join(['(',l1,')'])

    def __repr__(self):
         return self.math

    def _pure_(self):
        return self.po(self.lhs._pure_(),self.rhs._pure_())

    @property
    def classname(self):
        return self.__class__.__name__

    def set_side(self, side):
        for term in self.temrms:
            term.side = side
            term.set_side(side)

    def json_flat(self,lst=None):
        if not lst:
            lst = []

        lst.append({"id": self.id,
                    "type": self.classname,
                    "toplevel": True,
                    "children": [term.id for term in self.terms]})

        for term in self.terms:
            term.json_flat(lst)

        return lst

    def get_html(self):
        self.rhs.id = self.idgen.next()
        self.lhs.id = self.idgen.next()

        self.rhs.group = self.id
        self.lhs.group = self.id

        self.lhs.javascript = None
        self.rhs.javascript = None

        self.rhs.rhs.id = self.idgen.next()
        self.lhs.lhs.id = self.idgen.next()

        self.rhs.rhs.associate_terms()
        self.lhs.lhs.associate_terms()

        if self.sortable:
            s1 = self.lhs.lhs.ui_sortable(self.rhs.rhs)
            s2 = self.rhs.rhs.ui_sortable(self.lhs.lhs)

            javascript = s1 + s2

            #If we have an Equation of the form A/B = C/D then we can
            #drag terms between the numerator and denominator
            if self.lhs.lhs.has_single_term() and self.rhs.rhs.has_single_term():
                #TODO: Change these to isinstance
                if type(self.lhs.lhs.terms[0]) is Fraction and type(self.rhs.rhs.terms[0]) is Fraction:

                   lfrac = self.lhs.lhs.terms[0]
                   rfrac = self.rhs.rhs.terms[0]

                   lden = lfrac.den
                   rden = rfrac.den

                   lnum = lfrac.num
                   rnum = rfrac.num

                   #lnumm, ldenm = lnum.wrap(Product) , lden.wrap(Product)
                   #rnumm, rdenm = rnum.wrap(Product) , rden.wrap(Product)

                   if type(lnum) is not Product:
                       lfrac.num = lfrac.num.wrap(Product)

                   if type(rnum) is not Product:
                       rfrac.num = rfrac.num.wrap(Product)

                   if type(lden) is not Product:
                       lfrac.den = lfrac.den.wrap(Product)

                   if type(rden) is not Product:
                       rfrac.den = rfrac.den.wrap(Product)

                   if type(lnum) is Product or type(lnum) is Variable:
                       javascript += lnum.ui_sortable(rfrac.den)

                   if type(rnum) is Product or type(rnum) is Variable:
                       javascript += rnum.ui_sortable(lfrac.den)

                   if type(lden) is Product or type(lden) is Variable:
                       javascript += lden.ui_sortable(rfrac.num)

                   if type(rden) is Product or type(rden) is Variable:
                       javascript += rden.ui_sortable(lfrac.num)


        c = template.Context({
            'id': self.id,
            'rhs_id': self.rhs.id,
            'lhs_id': self.lhs.id,
            'math': self.math,
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
        #self.lhs.idgen = self.idgen
        #self.rhs.idgen = self.idgen

        #self.lhs.ensure_id()
        #self.rhs.ensure_id()

    def down(self,other):
        if type(other) is Numeric:
            self.lhs = LHS(*[Fraction(term,other) for term in self.lhs.terms])
            self.rhs = RHS(*[Fraction(term,other) for term in self.rhs.terms])
            self.rhs.group = self.id
            self.lhs.group = self.id

        return self.get_html()

rhs_html = '''
<span id='{{id}}' math-type="RHS" math-meta-class="side" math="{{math}}" group="{{group}}" class="container">
    {% autoescape off %}
    {{rhs}}
    {% endautoescape %}
</span>

'''

class RHS(Term):
    html = template.Template(rhs_html)

    def __init__(self,*terms):
        self.rhs = Addition(*terms)
        self.terms = [self.rhs]
        self.args = [self.rhs]
        self.side = 1
        self.rhs.side = 1
        self.rhs.parent = self

    def _pure_(self):
        return self.rhs._pure_()

    def get_html(self):
        self.rhs.group = self.id
        self.rhs.associate_terms()

        c = template.Context({
            'id': self.id,
            'latex':self.latex,
            'math': self.get_math(),
            'type': self.classname,
            'group': self.group,
            'rhs': self.rhs.get_html()
            })

        return self.html.render(c)

lhs_html = '''
<span id='{{id}}' math-type="LHS" math-meta-class="side" math="{{math}}" group="{{group}}" class="container" >
    {% autoescape off %}
    {{lhs}}
    {% endautoescape %}
</span>
'''

class LHS(Term):
    html = template.Template(lhs_html)

    def __init__(self,*terms):
        self.lhs = Addition(*terms)
        self.terms = [self.lhs]
        self.args = [self.lhs]
        self.side = 0
        self.lhs.side = 0
        self.lhs.parent = self

    #TODO: we NEED hashes on these, but because the Addition
    #contiainer is not created with the parser it doesn't get a
    #hash so we need to figure out a way to do that.
    #@property
    #def hash(self):
    #    pass

    def _pure_(self):
        return self.lhs._pure_()

    def get_html(self):
        self.lhs.group = self.id
        self.lhs.associate_terms()

        c = template.Context({
            'id': self.id,
            'latex':self.latex,
            'math': self.get_math(),
            'type': self.classname,
            'group': self.group,
            'lhs': self.lhs.get_html()
            })

        return self.html.render(c)

definition_html = '''
    <tr id="{{id}}" class="equation" math="{{math}}"
    math-type="{{classname}}" toplevel="true" data-confluent="{{confluent}}" data-public="{{public}}">

    <td>
        <button class="ui-icon ui-icon-transferthick-e-w"
        onclick="apply_transform('ReverseDef',get_equation(this))">{{lhs_id}}</button>
        <button class="ui-icon ui-icon-arrow-4" onclick="select_term(get_equation(this))">{{id}}</button>
        <button class="confluence 
        {% if confluent %} 
        ui-icon ui-icon-bullet
        {% else %}
        ui-icon ui-icon-radio-off
        {% endif %}
        " onclick="toggle_confluence(get_equation(this))">{{id}}</button>
    </td>
    <td>{{lhs}}</td>
    <td><span class="equalsign">$${{symbol}}$$</span></td>
    <td>{{rhs}}</td>
    <td class="guard">{{guard}}</td>
    <td class="annotation"><div contenteditable=true>{{annotation}}</div></td>

    </tr>
'''

class Definition(Equation):
    symbol = ":="
    sortable = False
    html = template.Template(definition_html)
    confluent = True
    public = True
    pure = None

    def _pure_(self):
        if self.lhs.hash != self.rhs.hash:
            return pure.PureRule(self.lhs._pure_(),self.rhs._pure_())
        else:
            print "Definition is infinitely recursive."

    def get_html(self):

        self.rhs.id = self.idgen.next()
        self.lhs.id = self.idgen.next()

        self.rhs.group = self.id
        self.lhs.group = self.id

        self.lhs.javascript = None
        self.rhs.javascript = None

        self.rhs.rhs.id = self.idgen.next()
        self.lhs.lhs.id = self.idgen.next()

        self.rhs.rhs.associate_terms()
        self.lhs.lhs.associate_terms()

        c = template.Context({
            'id': self.id,
            'rhs_id': self.rhs.id,
            'lhs_id': self.lhs.id,
            'math': self.math,
            'lhs': self.lhs.get_html(),
            'rhs': self.rhs.get_html(),
            'annotation': self.annotation,
            'symbol': self.symbol,
            'confluent': int(self.confluent),
            'public': self.public,
            'classname': self.classname
            })

        return self.html.render(c)

#-------------------------------------------------------------
# Operations
#-------------------------------------------------------------

operation_html_postfix = '''
<span id="{{id}}" math-meta-class="term" class="term {{class}}{{sensitive}}" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">

    <span class="parenthesis">
    {{operand}}
    </span>

    <span class="operator" math-type="operator" math-meta-class="operator" group="{{id}}">
    $${{symbol}}$$
    </span>
</span>
'''

operation_html_prefix = '''
<span id="{{id}}" math-meta-class="term" class="container {{class}}{{sensitive}}" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">
    <span class="operator {{class}}" math-type="operator"
        math-meta-class="operator" group="{{id}}" title="{{type}}" >$${{symbol}}$$
    </span>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths left">
       &Ograve;
    </span>
    {% endif %}

    <span class="">
    {{operand}}
    </span>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths right">
       &Oacute;
    </span>
    {% endif %}

</span>
'''

operation_html_outfix = '''
    <span id="{{id}}" math-meta-class="term" class="container {{class}}{{sensitive}}" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">

    {{symbol1}}

    {% if parenthesis %}
    <span class="ui-state-disabled pnths left">
       &Ograve;
    </span>
    {% endif %}

    <span class="parenthesis">
    {{operand}}
    </span>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths right">
       &Oacute;
    </span>
    {% endif %}

    {{symbol2}}

    </span>
'''

#The unicode here comes from cmex10 font for parentheses

operation_html_infix = haml('''
#{{id}}.{{class}}.container math-meta-class="term"  math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}"
    {% if parenthesis %}
    .ui-state-disabled.pnths.left
       &Ograve;
    {% endif %}

    {% for o in operand %}
    {{ o }}
    {% if not forloop.last %}
    .ui-state-disabled.infix math-type="times" math-meta-class="sugar"
        $${{symbol}}$$
    {% endif %}
    {% endfor %}

    {% if parenthesis %}

    .ui-state-disabled.pnths.right
       &Oacute;

    {% endif %}

{{jscript}}
''')

operation_html_sup = '''
<span id="{{id}}" math-meta-class="term" class="container {{class}}{{sensitive}}" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">

    {% if parenthesis %}
    <span class="ui-state-disabled pnths left">
       &Ograve;
    </span>
    {% endif %}

    <span class="">
    {{operand}}
    </span>

    <sup>
    {{symbol1}}
    </sup>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths right">
       &Oacute;
    </span>
    {% endif %}

</span>
'''

operation_html_sub = '''
<span id="{{id}}" math-meta-class="term" class="container {{class}}{{sensitive}}" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">

    {% if parenthesis %}
    <span class="ui-state-disabled pnths left">
       &Ograve;
    </span>
    {% endif %}

    <span class="">
    {{operand}}
    </span>

    <sub>
    {{symbol1}}
    </sub>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths right">
       &Oacute;
    </span>
    {% endif %}

</span>
'''

operation_html_latex = '''
<span id="{{id}}" math-meta-class="term" class="container {{class}}{{sensitive}}" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">

    {% if parenthesis %}
    <span class="ui-state-disabled pnths left">
       &Ograve;
    </span>
    {% endif %}

    <span class="{{class}}">
    {{operand}}
    </span>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths right">
       &Oacute;
    </span>
    {% endif %}

</span>
'''

infix_symbol_template = haml('''
.ui-state-disabled.infix.term math-type="infix" math-meta-class="sugar"
    $${{%s}}$$
''')


def infix_symbol_html(symbol):
    return infix_symbol_template % symbol


class Operation(Term):
    '''An operator acting a term'''

    ui_style = 'prefix'

    symbol = None
    show_parenthesis = False
    recursive_propogation = False
    sortable = False

    #Arity of the operator
    arity = None

    is_linear = False
    is_bilinear = False
    is_commutative = False
    is_anticommutative = False

    pure = None

    def __init__(self,*operands):
        if len(operands) > 1:
            self.terms = list(operands)
            self.operand = self.terms
        else:
            self.operand = operands[0]
            self.terms = [operands[0]]

    def action(self,operand):
        return self.get_html()

    def get_html(self):
        self.associate_terms()

        # If a parent element has already initiated a sort (i.e
        # like Equation does) then don't overwrite that
        # javascript.
        if self.sortable and not self.has_sort:
            self.ui_sortable()

        #Infix Formatting
        if self.ui_style == 'infix':
            self.html = template.Template(operation_html_infix)
            objects = [o.get_html() for o in self.terms]

            c = template.Context({
                'id': self.id,
                'math': self.get_math(),
                'type': self.classname,
                'group': self.group,
                'operand': objects,
                'symbol': self.symbol,
                'parenthesis': self.show_parenthesis,
                'jscript': self.get_javascript(),
                'class': self.css_class
                })

            return self.html.render(c)

        #Outfix Formatting
        elif self.ui_style == 'outfix':
            self.html = template.Template(operation_html_outfix)

            c = template.Context({
                'id': self.id,
                'math': self.get_math(),
                'type': self.classname,
                'group': self.group,
                'operand': self.operand.get_html(),
                'symbol1': self.symbol1.get_html(),
                'symbol2': self.symbol2.get_html(),
                'parenthesis': self.show_parenthesis
                })

            return self.html.render(c)

        #Prefix Formatting
        elif self.ui_style == 'prefix':
            self.html = template.Template(operation_html_prefix)

            #if not self.css_class:
            #    self.css_class = 'baseline'

            c = template.Context({
                'id': self.id,
                'math': self.get_math(),
                'type': self.classname,
                'group': self.group,
                'operand': self.operand.get_html(),
                'symbol': self.symbol,
                'parenthesis': self.show_parenthesis,
                'class': self.css_class
                })

        #Postfix Formatting
        elif self.ui_style == 'postfix':
            self.html = template.Template(operation_html_postfix)

            c = template.Context({
                'id': self.id,
                'math': self.get_math(),
                'type': self.classname,
                'group': self.group,
                'operand': self.operand.get_html(),
                'symbol': self.symbol,
                'parenthesis': self.show_parenthesis,
                'class': self.css_class
                })

        #Superscript Formatting
        elif self.ui_style == 'sup':
            self.html = template.Template(operation_html_sup)

            if not self.css_class:
                self.css_class = 'middle'

            c = template.Context({
                'id': self.id,
                'math': self.get_math(),
                'type': self.classname,
                'group': self.group,
                'operand': self.operand.get_html(),
                'symbol1': self.symbol1.get_html(),
                'parenthesis': self.show_parenthesis,
                'class': self.css_class
                })

        #Subscript Formatting
        elif self.ui_style == 'sub':
            self.html = template.Template(operation_html_sub)

            if not self.css_class:
                self.css_class = 'middle'

            c = template.Context({
                'id': self.id,
                'math': self.get_math(),
                'type': self.classname,
                'group': self.group,
                'operand': self.operand.get_html(),
                'symbol1': self.symbol1.get_html(),
                'parenthesis': self.show_parenthesis,
                'class': self.css_class
                })
        #Subscript Formatting
        elif self.ui_style == 'latex':
            self.html = template.Template(operation_html_latex)

            if hasattr(self.operand,'symbol'):
                self.operand.latex = "%s{%s}" % (self.symbol1, self.operand.symbol)

            c = template.Context({
                'id': self.id,
                'math': self.get_math(),
                'type': self.classname,
                'group': self.group,
                'operand': self.operand.get_html(),
                'parenthesis': self.show_parenthesis,
                'class': self.css_class
                })
        else:
            print('Unknown operator class, should be (infix,postfix,prefix,outfix)')

        return self.html.render(c)

    def get_symbol(self):
        return self.symbol

    def receive(self,obj,receiver_context,sender_type,sender_context,new_position):
        return obj

    def has_single_term(self):
        if len(self.terms) == 1:
            return True

class RefOperator(Operation):
    def __init__(self, obj, *operands):
        if isinstance(obj, unicode) or isinstance(obj,str):
            obj = Function.objects.get(id=int(obj))

        if isinstance(obj, Numeric):
            obj = Function.objects.get(id=obj.number)

        if len(operands) > 1:
            self.terms = list(operands)
            self.operand = self.terms
        else:
            self.operand = operands[0]
            self.terms = [operands[0]]

        self.symbol = obj.symbol1
        self.ui_style = obj.notation
        self.index = obj.id

    @property
    def classname(self):
        return 'RefOperator__%d' % self.index

    def _pure_(self):
        args = [o._pure_() for o in self.terms]
        return pure.refop(pure.PureInt(int(self.index)))(*args)

class Addition(Operation):
    ui_style = 'infix'
    symbol = '+'
    show_parenthesis = False
    pure = 'add'

    def __init__(self,*terms):
        self.terms = list(terms)

        #If we have nested Additions collapse them Ex: 
        #(Addition (Addition x y ) ) = (Addition x y)
        if len(terms) == 1:
            if type(terms[0]) is Addition:
                self.terms = terms[0].terms

        self.operand = self.terms
        js.make_sortable(self)

    def __add__(self,other):
        if type(other) is Addition:
            self.terms.extend(other.terms)
            return self

    def _pure_(self):
        # There is some ambiguity here since we often use an
        # addition operator of arity=1 to make UI magic happen
        # clientside, but we just eliminiate it when converting
        # into a expression
       if len(self.terms) == 1:
           return self.terms[0]._pure_()
       else:
           pterms = map(lambda o: o._pure_() , self.terms)
           return self.po(*pterms)

    def receive(self,obj,receiver_context,sender_type,sender_context,new_position):
        #If an object is dragged between sides of the equation negate the object

        if sender_context == 'LHS' or sender_context == 'RHS':
            obj = obj.negate()
            return obj
        else:
            return obj

    def remove(self,obj,remove_context):
        '''If we drag everything form this side of the equation
        zero it out'''

        if type(self.terms[0]) is Empty:
            return Numeric(0)

class Product(Operation):
    ui_style = 'infix'
    symbol = '\\cdot'
    show_parenthesis = False
    pure = 'mul'

    def __init__(self,*terms):
        self.terms = list(terms)

        for term in self.terms:
            term.group = self.id
            if type(term) is Addition:
                term.show_parenthesis = True
        self.operand = self.terms
        make_sortable(self)
        #self.ui_sortable()

    def remove(self,obj,remove_context):
        if type(self.terms[0]) is Empty:
            return One()

    def _pure_(self):
       if len(self.terms) == 1:
           return self.terms[0]._pure_()
       else:
           pterms = map(lambda o: o._pure_() , self.terms)
           return self.po(*pterms)

power_html = '''
#{{id}} group="{{group}}" .term.{{class}}.{{sensitive}} math-type="{{type}}" math-meta-class="term" math="{{math}}"
    .base
        {{base}}
    sup.exponent
        {{exponent}}
'''

class Power(Operation):
    sensitive = True
    html = template.Template(power_html)
    pure = 'powr'

    def __init__(self,base,exponent):
        self.base = base
        self.exponent = exponent
        self.terms = [self.base, self.exponent]
        basetype = type(self.base)
        if basetype is Fraction or isinstance(self.base, Operation):
            self.base.show_parenthesis = True
        make_sortable(self)

    def _pure_(self):
        return self.po(self.base._pure_() , self.exponent._pure_())

    def get_html(self):
        self.exponent.css_class = 'exponent'
        self.exponent.group = self.id
        self.base.css_class = 'exponent'
        self.base.group = self.id

        c = template.Context({
            'id': self.id,
            'math': self.get_math(),
            'group': self.group,
            'base': self.base.get_html(),
            'type': self.classname,
            'exponent': self.exponent.get_html() })

        return self.html.render(c)

class Negate(Operation):
    ui_style = 'prefix'
    symbol = '-'
    show_parenthesis = False
    css_class = 'negate'

    # Capitalize since "neg" already exists in the default Pure
    # predule.
    pure = 'Neg'

    def __init__(self,operand):
        self.operand = operand
        self.operand.group = self.id
        self.terms = [self.operand]

        if type(self.operand) is Addition:
            self.show_parenthesis = True

    def _pure_(self):
       return pure.po(self.operand._pure_())

    @fallback(Term.combine_fallback)
    def combine(self,other,context):
        ''' -A+-B = -(A+B)'''

        if context == 'Addition':
            if isinstance(other,Negate):
                return Negate(Addition(self.operand, other.operand))

    def negate(self):
        return self.operand
