try:
    from wise.worksheet.pure_wrap import use, PureSymbol, env
except ImportError:
    raise Exception('Could not load Cython Pure module, perhaps it needs to be built?')

# !!!!!!!
# Yah, this is ugly, we'd like to move this into a pure solution
# in pure_wrap.py
env.eval('using worksheet::base::prelude')
stupid = env.eval('stupid')
