try:
    from wise.worksheet.pure_wrap import use, PureSymbol
except ImportError:
    raise Exception('Could not load Cython Pure module, perhaps it needs to be built?')

use('calculus','calculus')
