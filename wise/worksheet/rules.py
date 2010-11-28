import wise.translators.pytopure as translate
import wise.translators.pure_wrap as pure_wrap
from wise.translators.pure_wrap import PureLevel, PureSymbol, reduce_with_pure_rules, PureClosure

from worksheet.utils import hasharray
import wise.worksheet.exceptions as exception

from django.utils import importlib
from django.conf import settings

from wise.base.rules import PublicRule

packages = {}
rulesets = {}
ROOT_MODULE = 'wise'

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

    # Working under the assumption that the external rule is
    # of the form 
    #
    # symbol X = reduce X
    # with
    #     rewrite rules
    # end;

    pexpr = map(translate.python_to_pure, expr)

    if settings.DEBUG:
        print 'Applying Rule:', ref, '\n--'
        print 'Input Sexp:', expr
        print 'Input Pure:', pexpr

    pure_expr = ref(*pexpr)
    pyexpr = translate.pure_to_python(pure_expr,expr[0].idgen)

    if settings.DEBUG:
        print 'Reduced Sexp:', pyexpr
        print 'Reduced Pure:', pure_expr

    return pyexpr

def is_rule(obj):
    return isinstance(obj,PublicRule)

# And so begin 4 nested for-loops, yah....
for pack in settings.INSTALLED_MATH_PACKAGES:
    try:
        path = '.'.join([ROOT_MODULE,pack,'rules'])
        packages[pack] = importlib.import_module(path)
        for name, symbol in packages[pack].__dict__.iteritems():

            # Merge dictionary into main
            if name == 'panel':
                rulesets.update(symbol)

            # Register the rule in the translation dictionary
            if hasattr(symbol,'register'):
                symbol.register()

    except ImportError:
        raise exception.IncompletePackage(pack,'rules.py')
