import translate

import pure_wrap
from pure_wrap import PureLevel, PureSymbol, reduce_with_pure_rules

from worksheet.utils import hasharray
import wise.worksheet.exceptions as exception

from django.utils import importlib
from django.conf import settings

# A lookup table mapping previously run rules to their
# Cython equivelents to avoid the cost of translation
# for future use
rulecache = {}

def ReduceWithRules( rules, expr ):
    '''Reduce the given expression with a list of PureRules
    specified as an array of strings which are translated into
    Pure code.'''

    hsh = hasharray(rules)

    if hsh in rulecache:
        plevel = rulecache[hsh]
    else:
        print 'Building up new rule'
        plevel = PureLevel(rules)
        rulecache[hsh] = plevel
        print 'Rule cache size:', len(rulecache)

    pexpr = translate.python_to_pure(expr)
    pure_expr = reduce_with_pure_rules(plevel, pexpr)

    #debug(str(pexpr) + ' ----> ' + str(pure_expr))
    return translate.pure_to_python(pure_expr,expr.idgen)

def ApplyExternalRule( ref, *expr ):
    '''Reduce the given expression with an external Pure symbol
    which corresponds to a set of rules defined in an external
    prelude'''

    # Working under the assumptiong that the external rule is
    # of the form 
    #
    # symbol X = reduce X
    # with
    #     rewrite rules
    # end;

    pexpr = map(translate.python_to_pure,expr)
    pure_expr = ref(*pexpr)
    pyexpr = translate.pure_to_python(pure_expr,expr[0].idgen)


    if settings.DEBUG:
        print 'Applying Rule:', ref, '\n--'
        print 'Input Sexp:', expr
        print 'Input Pure:', pexpr
        print 'Reduced Sexp:', pyexpr
        print 'Reduced Pure:', pure_expr

    return pyexpr

class PublicRule:
    po = None
    ref = None

    def __init__(self, pure_symbol_name):
        self.ref = pure_symbol_name
        #self.po = pure_wrap.objects[pure_symbol_name]
        self.po = PureSymbol(pure_symbol_name)
        pure_wrap.objects[pure_symbol_name] = self.po


    def get_html(self):
        interface_ui = self.template
        objects = [obj.get_html() for obj in self.objects]
        c = Context({'name':self.name, 'objects': objects})
        return interface_ui.render(c)

def is_rule(obj):
    return isinstance(obj,PublicRule)

packages = {}
rulesets = {}
ROOT_MODULE = 'wise'

for pack in settings.INSTALLED_MATH_PACKAGES:
    try:
        path = '.'.join([ROOT_MODULE,pack,'rules'])
        packages[pack] = importlib.import_module(path)
        for name, symbol in packages[pack].__dict__.iteritems():

            # Merge dictionary into main
            if name == 'panel':
                rulesets.update(symbol)

            #if is_rule(symbol):
            #    if settings.DEBUG:
            #        print "Importing ruleset ... %s/%s" % (pack, name)

            #    rulesets[name] = symbol
    except ImportError:
        raise exception.IncompletePackage(pack,'rules.py')

print 'RuleSets',rulesets
