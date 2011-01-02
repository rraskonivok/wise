from celery.decorators import task
from wise.worksheet.utils import memoize, logger

print 'Spawned Worker'

@task
def rule_reduce(rule, sexps):
    from wise.boot import start_python_pure, start_cython
    import wise.translators.pytopure as translate

    start_python_pure()
    start_cython()

    from wise.translators.mathobjects import rules
    from wise.translators.pureobjects import i2p

    args = [translate.parse_sexp(sexp) for sexp in sexps]
    pargs = map(translate.python_to_pure, args)
    ref = rules[rule]()

    if not ref:
        raise Exception('No Rule Found')

    pure_expr = ref.reduce_with(*pargs)
    return str(i2p(pure_expr))

@task
def pure_exec(code):
    from wise.boot import start_python_pure, start_cython
    start_python_pure()
    start_cython()

    from wise.translators.pure_wrap import PureInterface
    from wise.translators.pureobjects import i2p

    interface = PureInterface()
    pure_expr = interface.eval(code)

    return str(i2p(pure_expr))

@task
def benchmark(x,y):
    return sum([a for a in range(1,random.randint(0,25))])

#x = rule_reduce('algebra_normal',['(Variable x)'])
#y = rule_reduce('algebra_normal',['(Addition (Variable x) (Variable x))'])
#z = rule_reduce('algebra_normal',['(Integral (Variable x) (Variable x))'])
#
#print x == 'x' or x
#print y == 'mul 2 x' or y
#print z == 'powr x 2' or z
