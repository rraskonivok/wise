#!/usr/bin/env python

# Set our process titlte
from setproctitle import setproctitle
setproctitle('wise-worker')

import pprint
import time
import zmq

# ----------
# Setup Path
# ----------

from django.core.management import setup_environ
import settings
setup_environ(settings)
settings.DEBUG = True

from wise import boot
from wise import *

import wise.translators.pytopure as translate
from wise.translators.pureobjects import i2p, p2i
from wise.translators.mathobjects import rules
from wise.translators.pure_wrap import PureInterface

from django.utils.simplejson import dumps, loads

# Adapated from IPython
class Message(object):

    def __init__(self, msg_dict):
        dct = self.__dict__
        for k, v in msg_dict.iteritems():
            if isinstance(v, dict):
                v = Message(v)
            dct[k] = v

        #self.uuid = uuid.uuid4()

    def __iter__(self):
        return iter(self.__dict__.iteritems())

    def __repr__(self):
        return repr(self.__dict__)

    def __str__(self):
        return pprint.pformat(self.__dict__)

    def __contains__(self, k):
        return k in self.__dict__

    def __getitem__(self, k):
        return self.__dict__[k]

    def to_json(self):
        return dumps(self.__dict__)

# --------------
# Load Interface
# --------------

boot.start_python_pure()
boot.start_cython()

def do_rule(rule, sexps):
    args = map(translate.parse_sexp, sexps)
    pargs = map(translate.python_to_pure, args)

    ref = rules[rule]()
    pure_expr = ref.reduce_with(*pargs)

    return str(i2p(pure_expr))

def do_exec(s):
    pure_expr = interface().eval(code)
    return str(i2p(pure_expr))

actions = {
    'rule', do_rule,
    'exec', do_exec,
}

def main():

    context = zmq.Context()
    receive = context.socket(zmq.PULL)
    receive.connect("tcp://127.0.0.1:5000")

    print "Starting the kernel..."
    print ":: tcp://127.0.0.1:5000"

    while True:
        msg = receive.recv()
        jmsg = loads(msg)

        if msg:
            print 'JOB: %s' % jmsg['uid']
            start_time = time.time()

            try:
                rule = jmsg['args']
                operands = jmsg['operands']
                result = do_rule(rule, operands)
                print result
            except Exception as e:
                print 'err'
                print e

            end_time = time.time()

            print end_time - start_time
            #receive.send('done')

if __name__ == '__main__':
    main()
    #spawn(main).join()
