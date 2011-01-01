

from celery.decorators import task
from wise.worksheet.utils import memoize, logger

print 'Spawned Worker'

import random

@task
def rule_reduce(rule, sexps):
    import wise.translators.pure_wrap as pure_wrap
    from wise.boot import start_python_pure, start_cython
    import wise.translators.pytopure as translate
    from wise.translators.pytopure import parse_pure_exp
    from wise.translators.pure_wrap import i2p

    start_python_pure()
    start_cython()

    args = [translate.parse_sexp(sexp) for sexp in sexps]
    pargs = map(translate.python_to_pure, args)
    ref = pure_wrap.rules[rule]()

    #expr_tree = translate.pure_to_python(pure_expr)
    #return expr_tree

    pure_expr = ref.reduce_with(*pargs)
    return str(i2p(pure_expr))

@task
def add(x,y):
    return sum([a for a in range(1,random.randint(0,25))])
