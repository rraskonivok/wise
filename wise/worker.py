# -*- coding: utf-8 -*-
#!/usr/bin/env python

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

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
import wise.worksheet.exceptions as exception

import django.utils.simplejson as json
from django.utils.simplejson import dumps, loads

from wise.worksheet.utils import uidgen, html, json_flat

# -----------------------
#  ZMQ Connections
# -----------------------

context = zmq.Context()
task_receive = context.socket(zmq.PULL)
task_receive.connect("tcp://127.0.0.1:5000")

result_push = context.socket(zmq.PUSH)
result_push.connect("tcp://127.0.0.1:5001")

# --------------
# Load Interface
# --------------

boot.start_python_pure()
boot.start_cython()

blacklist = [
    '='         , # "prevents" users from making stateful changes
    'argc'      ,
    'argv'      ,
    'break'     ,
    'bt'        ,
    'cd'        ,
    'clear'     ,
    'const'     ,
    'def'       ,
    'del'       ,
    'dump'      ,
    'eval'      ,
    'evalcmd'   ,
    'extern'    ,
    'help'      ,
    'infix'     ,
    'infixl'    ,
    'infixr'    ,
    'let'       ,
    'ls'        ,
    'mem'       ,
    'namespace' ,
    'nonfix'    ,
    'outfix'    ,
    'override'  ,
    'postfix'   ,
    'prefix'    ,
    'pwd'       ,
    'quit'      ,
    'run'       ,
    'save'      ,
    'sysinfo'   ,
    'type'      ,
    'underride' ,
    'using'
]

def do_rule(rule, sexps, nsi):
    """
    Applies a Pure rule to tuple of elements. The codomain tuple
    is always mapped to the same size of the domain tuple.

    For example a rule to commute addition maps 1-tuples to
    1-tuples.

    `(Addition x y) →  (Addition y x)`

    A rule to add an element to both sides of an equation maps
    2-tuples to 2-tuples but one element of the image is null.

    `( (Equation lhs rhs) , x ) →  ( (Equation lhs+x rhs+x) , pass )`

    In this case the 'pass' element tells the worksheet to do
    not expect a new element in the image of the rule and leave
    that element inplace.
    """

    # Build the Pure expression from the given sexps
    args  = map(translate.parse_sexp, sexps)
    pargs = map(translate.python_to_pure, args)

    # Build the rule and apply it to the Pure expression
    ref        = rules[rule]()
    _pure_expr = ref.reduce_with(*pargs)

    # Convert to prefix form for conversion back to Python
    result = i2p(_pure_expr)

    # Create the uid generator and walk the new expression to
    # return the JSON
    uid       = uidgen(int(nsi))
    expr_tree = translate.parse_pure_exp(result)

    # Walk the tree with the UID generator
    expr_tree.uid_walk(uid, overwrite=True)

    _html = html(expr_tree)
    _json = json_flat(expr_tree)
    _nsi  =  uid.next()[3:]

    return json.dumps({
        'new_html'        : [_html],
        'new_json'        : [_json],
        'namespace_index' : _nsi
    })


def do_eval(code, sexps, nsi):
    # Block the execution of any code which could alter the
    # interpreter, this is marginally improves security
    if any([s in code for s in blacklist]):
        # Raise a warning since this could be a hacking attempt
        # TODO: at some point tie this into django-axes and cut
        # the user off if they try too much of this stuff
        logging.warning('Attempt to use Pure keyword: ' + code)
        return json.dumps({'error': 'Invalid keyword'})

    try:
        pure_expr = PureInterface().eval(code)
        result = i2p(pure_expr)
    except Exception as e:
        error = str(e.value)
        return json.dumps({'error':error})


    # Create the uid generator and walk the new expression to
    # return the JSON
    uid       = uidgen(int(nsi))

    try:
        expr_tree = translate.parse_pure_exp(result)
    except exception.NoWrapper as e:
        unknown = e.value
        return json.dumps({'error': 'Unknown symbol: %s' % unknown})

    expr_tree.uid_walk(uid, overwrite=True)

    _html = html(expr_tree)
    _json = json_flat(expr_tree)
    _nsi  =  uid.next()[3:]

    return json.dumps({
        'new_html'        : [_html],
        'new_json'        : [_json],
        'namespace_index' : _nsi
    })

tasks = {
    'rule': do_rule,
    'eval': do_eval,
}

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

            rule     = jmsg['args']
            operands = jmsg['operands']
            uid      = jmsg['uid']
            nsi      = jmsg['nsi']
            task_f   = tasks[jmsg['task']]

            result = task_f(rule, operands, nsi)

            print 'result', result
            send_result(uid, result)

            end_time = time.time()

            print '--'
            print 'job:', jmsg['uid']
            print 'time:', end_time - start_time

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        result_push.close()
        task_receive.close()
