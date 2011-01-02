from celery.decorators import task

from wise.worksheet.utils import memoize, logger
import wise.translators.pytopure as translate
from wise.translators.pure_wrap import PureInterface
from wise.translators.mathobjects import rules

print 'Spawned Worker'

@task
def rule_reduce(rule, sexps):
    from wise.translators.pureobjects import i2p

    args = [translate.parse_sexp(sexp) for sexp in sexps]

    pargs = map(translate.python_to_pure, args)
    ref = rules[rule]()

    print rules[rule], ref

    if not ref:
        raise Exception('No Rule Found')

    pure_expr = ref.reduce_with(*pargs)

    print pure_expr

    return str(i2p(pure_expr))

@task
def pure_exec(code):
    from wise.translators.pureobjects import i2p

    interface = PureInterface()
    pure_expr = interface.eval(code)

    return str(i2p(pure_expr))

@task
def benchmark(x,y):
    return sum([a for a in range(1,random.randint(0,25))])
