from celery.decorators import task
from celery.signals import worker_ready
from wise.worksheet.utils import logger


def init(**kwargs):
    if 'PureInterface' in globals():
        print 'Exists'
        return

    print 'Spawned Worker'
    import wise.boot

    wise.boot.start_python_pure()
    wise.boot.start_cython()

    import wise.translators.pytopure as translate
    from wise.translators.pureobjects import i2p
    from wise.translators.mathobjects import rules
    from wise.translators.pure_wrap import PureInterface

    globals().update(dict(
        i2p = i2p,
        translate = translate,
        rules = rules,
        PureInterface = PureInterface,
    ));

@task
def rule_reduce(rule, sexps):

    args = [translate.parse_sexp(sexp) for sexp in sexps]

    pargs = map(translate.python_to_pure, args)
    ref = rules[rule]()

    if not ref:
        raise Exception('No Rule Found')

    pure_expr = ref.reduce_with(*pargs)

    return str(i2p(pure_expr))

@task
def pure_exec(code):
    init()

    interface = PureInterface()
    pure_expr = interface.eval(code)
    return str(i2p(pure_expr))

@task
def benchmark(x,y):
    return sum([a for a in range(1,random.randint(0,25))])

worker_ready.connect(init)
