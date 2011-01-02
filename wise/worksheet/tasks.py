from celery.decorators import task
from celery.signals import worker_init
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
        interface = PureInterface,
    ));

@task
def rule_reduce(rule, sexps):
    if not 'translate' in globals():
        init()

    args = map(translate.parse_sexp, sexps)
    pargs = map(translate.python_to_pure, args)

    ref = rules[rule]()
    pure_expr = ref.reduce_with(*pargs)

    return str(i2p(pure_expr))

@task
def pure_exec(code):
    if not 'interface' in globals():
        init()

    pure_expr = interface().eval(code)
    return str(i2p(pure_expr))

@task
def benchmark(x,y):
    return sum([a for a in range(1,random.randint(0,25))])

worker_init.connect(init)
