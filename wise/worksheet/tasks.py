from celery.decorators import task
from celery.signals import worker_init, task_prerun
from wise.worksheet.utils import logger

_pure_initd = False

def init(**kwargs):
    global _pure_initd

    if _pure_initd:
        return

    print 'Spawned Worker'
    import wise.boot

    wise.boot.start_python_pure()
    wise.boot.start_cython()

    import wise.translators.pytopure as translate
    from wise.translators.pureobjects import i2p, p2i
    from wise.translators.mathobjects import rules
    from wise.translators.pure_wrap import PureInterface

    # Inject neccesary libarires into the workers global
    # namespace
    globals().update(dict(
        i2p = i2p,
        p2i = p2i,
        translate = translate,
        rules = rules,
        interface = PureInterface,
    ));

    _pure_initd = True

@task
def rule_reduce(rule, sexps):
    args = map(translate.parse_sexp, sexps)
    pargs = map(translate.python_to_pure, args)

    ref = rules[rule]()
    pure_expr = ref.reduce_with(*pargs)

    return str(i2p(pure_expr))

@task
def pure_exec(code):
    pure_expr = interface().eval(code)
    return str(i2p(pure_expr))

@task
def benchmark(x,y):
    return sum([a for a in range(1,random.randint(0,25))])

worker_init.connect(init)
task_prerun.connect(init)
