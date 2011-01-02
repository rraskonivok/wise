from celery.decorators import task
from wise.worksheet.utils import memoize, logger

print 'Spawned Worker'

import random

@task
def rule_reduce(rule, sexps):
    from wise.boot import start_python_pure, start_cython
    import wise.translators.pytopure as translate

    start_python_pure()
    start_cython()

    from wise.translators.pure_wrap import rules
    from wise.translators.pureobjects import i2p

    args = [translate.parse_sexp(sexp) for sexp in sexps]
    pargs = map(translate.python_to_pure, args)
    ref = rules[rule]()

    #expr_tree = translate.pure_to_python(pure_expr)
    #return expr_tree

    pure_expr = ref.reduce_with(*pargs)
    return str(i2p(pure_expr))

@task
def add(x,y):
    return sum([a for a in range(1,random.randint(0,25))])

#x = rule_reduce('algebra_normal',['(Variable x)'])
#y = rule_reduce('algebra_normal',['(Addition (Variable x) (Variable x))'])
#z = rule_reduce('algebra_normal',['(Integral (Variable x) (Variable x))'])
#
#print x == 'x' or x
#print y == 'mul 2 x' or y
#print z == 'powr x 2' or z
