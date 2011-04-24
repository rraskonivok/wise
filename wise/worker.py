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

import django.utils.simplejson as json
from django.utils.simplejson import dumps, loads

from wise.worksheet.utils import uidgen, html, json_flat

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

def do_rule(rule, sexps, nsi):
    # Build the Pure expression from the given sexps
    args = map(translate.parse_sexp, sexps)
    pargs = map(translate.python_to_pure, args)

    # Build the rule and apply it to the Pure expression
    ref = rules[rule]()
    _pure_expr = ref.reduce_with(*pargs)

    # Convert to prefix form for conversion back to Python
    result = i2p(_pure_expr)

    # Create the uid generator and walk the new expression to
    # return the JSON
    uid = uidgen(nsi)
    expr_tree = translate.parse_pure_exp(result)
    expr_tree.uid_walk(uid, overwrite=True)

    _html = html(expr_tree)
    _json = json_flat(expr_tree)
    _nsi  =  uid.next()[3:]

    return json.dumps({
        'new_html'        : _html,
        'new_json'        : _json,
        'namespace_index' : _nsi
    })

def do_exec(s):
    pure_expr = interface().eval(code)
    return str(i2p(pure_expr))

actions = {
    'rule', do_rule,
    'exec', do_exec,
}


context = zmq.Context()
task_receive = context.socket(zmq.PULL)
task_receive.connect("tcp://127.0.0.1:5000")

result_push = context.socket(zmq.PUSH)
result_push.connect("tcp://127.0.0.1:5001")

def send_result(uid, result):
    result_push.send_pyobj({'uid': uid, 'result': result})

def main():

    print "Starting the kernel..."
    print ":: tcp://127.0.0.1:5000"

    while True:
        msg = task_receive.recv()
        jmsg = loads(msg)

        if msg:
            start_time = time.time()

            try:
                rule = jmsg['args']
                operands = jmsg['operands']
                uid = jmsg['uid']
                nsi = jmsg['nsi']

                result = do_rule(rule, operands, nsi)
                print 'result', result
                send_result(uid, result)
            except Exception as e:
                send_result(uid, 'error')
                print 'err'
                print e

            end_time = time.time()

            print '--'
            print 'job:', jmsg['uid']
            print 'time:', end_time - start_time
            #receive.send('done')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        result_push.close()
        task_receive.close()
