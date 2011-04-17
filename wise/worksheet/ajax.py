# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import gevent
from gevent_zeromq import zmq

import uuid

from django.utils.simplejson import dumps, loads

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

import wise.translators.pytopure as translate
import wise.worksheet.exceptions as exception

from wise.translators.mathobjects import rulesets, transforms
from wise.worksheet import tasks
from wise.worksheet.utils import *

from wise.packages import loader

# Load up Cell & Equation types from the 'base' package
Cell = loader.load_package_module('base','cell').Cell
EquationPrototype = loader.load_package_module('base','toplevel').EquationPrototype

# ----------------------
# Message Protocol
# ----------------------

"""
apply_transformation:

{
    task            : 'transform',
    args            : ['package', 'transform_name'],
    operands        : []
    namespace_index : 0,
}

apply_rule:

{
    task            : 'rule',
    args            : ['package', 'rule_name'],
    operands        : []
    namespace_index : 0,
}

apply_eval:

{
    task            : 'eval',
    args            : ['code'],
    operands        : []
    namespace_index : 0,
}


"""

# Adapated from IPython
class Message(object):

    def __init__(self, msg_dict):
        dct = self.__dict__
        for k, v in msg_dict.iteritems():
            if isinstance(v, dict):
                v = Message(v)
            dct[k] = v

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

context = zmq.Context()
publisher = context.socket(zmq.PUSH)
publisher.bind("tcp://127.0.0.1:5000")

def message_listener(socketio, uid):
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("tcp://127.0.0.1:5001")

    # setsockopt doesn't like unicode
    subscriber.setsockopt(zmq.SUBSCRIBE, str(uid))
    completed = False

    while not completed:
        print 'LISTENING FOR', uid
        msg = subscriber.recv()
        if msg:
            socketio.send({'message': msg.split(":")[1]})
            completed = True

def _co_rule(socket, pmsg, uid):
    pmsg['uid'] = str(uid)
    socket.send(dumps(pmsg))
    #msg = sender.recv()

    #socketio.send(sender.recv_pyobj())

# ----------------------
# Websocket Handler
# ----------------------

def socketio(request):
    socketio = request.environ['socketio']

    # Is everything shiny?
    #if settings.DEBUG and 'socket.io' in request.environ['PATH_INFO']:
        #return HttpResponse("Everything's shiny, Cap'n. Not to fret.")

    while True:
        messages = socketio.recv()

        for msg in messages:
            pmsg = loads(msg)

            try:
                task = pmsg['task']
            except KeyError:
                print 'Not well formed'
                return HttpResponse()

            if task == 'rule':
                uid = uuid.uuid4()
                gevent.spawn(message_listener, socketio, uid)
                gevent.spawn(_co_rule, publisher, pmsg, uid).join()

    return HttpResponse()


def heartbeat(request):
    # Server is up and life is good
    response = HttpResponse(status=200)
    response['Cache-Control'] = 'no-cache'
    return response

@login_required
@ajax_request
def apply_rule(request):
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

    # The sexps of elements from worksheet, i.e. the
    # preimage/operands of the rule
    sexps = tuple(request.POST.getlist('operands[]'))

    # The uniqe client id ( cid ) used to refer to objets in the
    # workspace.
    namespace_index = int( request.POST.get('namespace_index') )

    if not namespace_index:
        raise Exception('No namespace index given in request.')

    if '' in sexps:
        raise Exception('Empty sexp was passed.')

    # Spawn a new generator uid generator to walk the parse tree
    uid = uidgen(namespace_index)
    rule = request.POST.get('rule')

    #gevent.Greenlet(_co_rule, rule, sexps).start()

    return JsonResponse({})
    #result = tasks.rule_reduce.delay(rule, sexps)
    #expr_tree = translate.parse_pure_exp(result.wait())
    #expr_tree.uid_walk(uid, overwrite=True)

    #return JsonResponse({'new_html': [html(expr_tree)],
                         #'new_json': [json_flat(expr_tree)],
                         #'namespace_index': uid.next()[3:]})

@login_required
def rules_request(request):
    return render_haml_to_response('ruleslist.tpl',
            {'rulesets':rulesets.as_dict()})

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

@login_required
@ajax_request
def use_infix(request):
    code = request.POST.get('code')

    # Block the execution of any code which could alter the
    # interpreter, this is marginally improves security
    if any([s in code for s in blacklist]):
        # Raise a warning since this could be a hacking attempt
        # TODO: at some point tie this into django-axes and cut
        # the user off if they try too much of this stuff
        logging.warning('Attempt to use Pure keyword: ' + code)
        return JsonResponse({'error': 'Invalid keyword'})

    namespace_index = int( request.POST.get('namespace_index') )
    uid = uidgen(namespace_index)
    quotify = False

    result = tasks.pure_exec.delay(code)
    if result.failed():
        # If failed then result is the PureEvalError instance
        return JsonResponse({'error': unicode(result.result.value)})

    try:
        expr_tree = translate.parse_pure_exp(result.wait())
    except exception.NoWrapper as e:
        unknown = e.value
        return JsonResponse({'error': 'Unknown symbol: %s' % unknown})

    expr_tree.uid_walk(uid, overwrite=True)

    return JsonResponse({'new_html': [html(expr_tree)],
                         'new_json': [json_flat(expr_tree)],
                         'namespace_index': uid.next()[3:]})


@login_required
@ajax_request
def apply_transform(request):
    code = tuple(request.POST.getlist('selections[]'))
    transform = unencode( request.POST.get('transform') )
    namespace_index = int( request.POST.get('namespace_index') )
    uid = uidgen(namespace_index)

    args = [translate.parse_sexp(cde) for cde in code]

    try:
        pack, fun = transform.split('/')
        transform = transforms[fun]
    except KeyError:
        raise exception.NoSuchTransform(transform)

    image = transform(*args)

    if len(image) == 0:
        raise Exception('Resulting image of transformation cannot\
                be empty.')

    actions = ['pass','delete','flash']

    new_html = []
    new_json = []

    for el in image:
        # Handle action strings
        if isinstance(el,str):
            if el in actions:
                new_html.append(el)
                new_json.append(el)
            else:
                # If something stranged is passed
                raise Exception('Unknown action returned by\
                        transform (%s, %s)' % (el, fun))

        # Handle mathematical terms
        else:
            el.uid_walk(uid)
            new_html.append(html(el))
            new_json.append(json_flat(el))

    return JsonResponse({'new_html': new_html,
                         'new_json': new_json,
                         'namespace_index': uid.next()[3:]})


@login_required
@ajax_request
def new_line(request):
    namespace_index = request.POST.get('namespace_index')

    if not namespace_index:
        namespace_index = 0
    else:
        namespace_index = int(namespace_index)

    cell_index = int( request.POST.get('cell_index') )
    newtype = request.POST.get('type')

    uid = uidgen(namespace_index)

    # TODO we should do this without parsing, this is really slow
    # and inefficent
    if newtype == u'def':
        new = translate.parse_sexp('(Definition (Placeholder) (Placeholder))')
    elif newtype == u'func':
        new = translate.parse_sexp('(Function (Placeholder) (Placeholder) (Placeholder))',uid)
    elif newtype == u'eq':
        new = EquationPrototype()
    elif newtype == u'assum':
        new = AssumptionPrototype()
    else:
        new = translate.parse_sexp(newtype)

    new.uid_walk(uid)

    return JsonResponse({'new_html': html(new),
                         'new_json': json_flat(new),
                         'namespace_index': uid.next()[3:],
                         'cell_index': cell_index + 1})

def new_cell(request):
    namespace_index = request.POST.get('namespace_index')
    cell_index = request.POST.get('cell_index')

    # Map into indices if given, otherwise assume 0
    if not namespace_index:
        namespace_index = 0
    else:
        namespace_index = int(namespace_index)

    if not cell_index:
        cell_index = 0
    else:
        cell_index = int(cell_index)

    # Create new empty cell
    new_cell = Cell([],[])
    new_cell.index = cell_index + 1;

    return JsonResponse({'new_html': html(new_cell),
                         'new_json': json_flat(new_cell),
                         'namespace_index': namespace_index,
                         'cell_index': cell_index + 1})

#vim: ai ts=4 sts=4 et sw=4
