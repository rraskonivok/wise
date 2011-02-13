import sys

# This is a lazy module which wraps its attributes to the
# interpreters `symbols` dictionary

# Will not invoke a Pure Instance:
# import wise.translators.pureobjects
#
# Will invoke a pure instance:
# from wise.translators.pureobjects import PureSymbol

# Credit goes to Alex Martelli
# http://stackoverflow.com/questions/1462986
class _Sneaky(object):
    """
    Avoid loading the interpreter until we need to reference a
    symbol.
    """

    def __init__(self):
        self.interface = None

    def __getattr__(self, name):
        from wise import settings
        from wise.translators.pure_wrap import init_pure

        if not self.interface:
            self.interface = init_pure()

            if settings.DEBUG:
                print 'Invoking interpreter because pureobjects.py requested object.'

        return self.interface[name]

sys.modules[__name__] = _Sneaky()
