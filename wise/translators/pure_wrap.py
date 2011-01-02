from django.conf import settings

import wise.worksheet.exceptions as exception
from wise.utils.patterns import Borg
from wise.translators import pureobjects

class PureInterface(Borg):

    __shared_state = dict(
        _loaded = False,
        _interp = None,
        symbols = {},
        libs = (),
    )

    def __init__(self, interp=None):
        self.__dict__ = self.__shared_state

        if not self._interp:
            from pure.pure import PureEnv
            self._interp = PureEnv()
            self._loaded = True
        elif interp:
            self._interp = interp
            self._loaded = True

    def eval(self, s):
        return self._interp.eval(s)

    def active(self):
        return self._loaded

    def libraries(self):
        if self.active():
            return self.libs
        else:
            raise Exception('No active interface.')

    def use(self, package, library):
        if self.active():
            if (package,library) not in self.libs:
                # Paths are relative to the /wise/ directory
                print 'Importing library ' + '/'.join([package, library])
                result = self.eval('using ' + '::'.join([package, library]))
                self.libs += ((package,library),)

                if not result:
                    raise Exception('Could not import (%s,%s)' %
                            (package, library))
                else:
                    return True
        else:
            raise Exception('No active interface.')

    # Really no reason to call this, and quite a few reasons
    # *not* to since directly interacting with the interpreter
    # can cause segfaults.
    def get_interp(self):
        if self.active():
            return self._interp
        return self._interp or Exception('No active interface')

    # Modeled after rpy2's interface
    def __getitem__(self, key):
        if self.active():
            try:
                return self.symbols[key]
            except KeyError:
                raise Exception('No Pure symbol: %s' % key)
        else:
            raise Exception('No active interface')

    def jit_compile(self):
        if self.active():
            self._interp.compile_interp()
        else:
            raise Exception('No active interface')

def init_pure(prelude=True, force=False):
    interface = PureInterface()

    if not interface.symbols:
        # __all__ is specified in pure/pure.pyx
        exec('from wise.pure.pure import *') in interface.symbols
#        exec('from wise.pure.pure import *') in globals()

    if prelude:
        interface.use('pure','prelude')
        exec('from wise.pure.prelude import p2i, i2p, nargs') in interface.symbols
#        exec('from wise.pure.pure import *') in globals()

    return interface

# This is a statefull change in the interpreter, if this is
# called at the root definition level it applies globally
#class ProtoRule:
#    _proto = None
#    lhs = None
#    rhs = None
#
#    def __init__(self, lhs, rhs, guards=None):
#        self.lhs = lhs
#        self.rhs = rhs
#
#    def __call__(self):
#        self._proto = proto_op(p2i(self.lhs), p2i(self.rhsj)
#        #print 'Init rule:', self._proto
#        # instance ( lhs --> rhs )1/
#        instance(self._proto)
#
#    def __repr__(self):
#        return str(self._proto)

class PublicRule:
    po = None
    ref = None
    arity = -1
    pure = None

    def __init__(self):
        self.ref = self.pure
        #self.po = PureClosure(self.pure)
        #pure_wrap.objects[self.pure] = self.po
        #self.po.arity = pure_wrap.nargs(self.po)

    @property
    def description(self):
        return self.__doc__

    def reduce_with(self, *expr):
        po = pureobjects.PureClosure(self.pure)
        return po(*expr)

#        pure_expr = po(*pexpr)
#        pyexpr = pure_to_python(pure_expr,expr[0].idgen)
#
#        print 'Reduced Sexp:', pyexpr
#        print 'Reduced Pure:', pure_expr

    #@classmethodn
    #def register(self):
    #    if self.pure:

    #        if hasattr(self,'__doc__') and self.__doc__:
    #            self.desc = trim_docstring(self.__doc__)
    #        else:
    #            self.desc = 'No description available'

    #        self.po = PureClosure(self.pure)
    #        pure_wrap.objects[self.pure] = self.po
