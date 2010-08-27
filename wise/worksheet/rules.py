import translate
from pure_wrap import PureLevel, reduce_with_pure_rules
from worksheet.utils import hasharray

# A lookup table mapping previously run rules to their
# Cython equivelents to avoid the cost of translation
# for future use
rulecache = {}

def ReduceWithRules( rules, expr ):
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
