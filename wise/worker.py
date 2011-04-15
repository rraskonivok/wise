#!/usr/bin/env python

# Set our process titlte
from setproctitle import setproctitle
setproctitle('wise-worker')

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

actions = {'rule', do_rule,
           'exec', do_exec,
          }

def main():

    context = zmq.Context()
    receive = context.socket(zmq.REP)
    receive.connect("tcp://127.0.0.1:5000")

    print "Starting the kernel..."
    print ":: tcp://127.0.0.1:5000"

    while True:
        msg = receive.recv_pyobj()

        if msg:
            print 'got job'
            start_time = time.time()

            try:
                rule = msg['args']
                operands = msg['operands']
                do_rule(rule, operands)
            except:
                print 'err'

            end_time = time.time()

            print end_time - start_time
            receive.send_pyobj(end_time - start_time)

if __name__ == '__main__':
    main()
    #spawn(main).join()
