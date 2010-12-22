# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import wise.translators.pytopure as translate
#import wise.translators.mathobjects

import wise.translators.pure_wrap as pure_wrap

from django import template
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, \
Http404

# uidgen is imported from utils
from wise.worksheet.utils import *
from wise.worksheet.models import Workspace, Expression, Cell
import wise.worksheet.exceptions as exception

import wise.worksheet.rules as rules
import wise.worksheet.transforms as transforms

from wise.base.cell import Cell as PyCell
from wise.base.objects import EquationPrototype, AssumptionPrototype

CACHE_INTERVAL = 30*60 # 5 Minutes

def heartbeat(request):
    # Server is up and life is good
    response = HttpResponse(status=200)
    response['Cache-Control'] = 'no-cache'
    return response

@memoize
def rule_reduce(rule, sexps):
    # >>>>>>>>>>>>>>>>>>>>>>>>>>
    # Reduce the passed arguments by applying them to the given
    # rule

    args = [translate.parse_sexp(sexp) for sexp in sexps]
    pargs = map(translate.python_to_pure, args)

    try:
        ref = pure_wrap.rules[rule]()
    except KeyError:
        raise Exception('Could not find executable form of rule: %s' % rule)

    pure_expr = ref.reduce_with(*pargs)
    new_expr_tree = translate.pure_to_python(pure_expr)
    return new_expr_tree

    # <<<<<<<<<<<<<<<<<<<<<<<<<<

@login_required
@errors
@ajax_request
def apply_rule(request):
    """
    Applies a Pure rule to tuple of elements. The codomain tuple
    is always mapped to the same size of the domain tuple.

    For example a rule to commute addition maps 1-tuples to
    1-tuples.

       (Addition x y) → (Addition y x)
            1         →        1

    A rule to add an element to both sides of an equation maps
    2-tuples to 2-tuples but one element of the image is null.

       ( (Equation lhs rhs) , x ) →  ( (Equation lhs+x rhs+x) , pass )
                 2                →                 2

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

    # Spawn a new generator to give out new uids to newly created
    # objects
    uid = uidgen(namespace_index)
    rule = request.POST.get('rule')

    new_expr_tree = rule_reduce(rule, sexps)

    # Overwrite all uids, in case we're working with a cached
    # objects which has some leftover uids
    new_expr_tree.uid_walk(uid, overwrite=True)

    return JsonResponse({'new_html': [html(new_expr_tree)],
                         'new_json': [json_flat(new_expr_tree)],
                         'namespace_index': uid.next()[3:]})

@login_required
@errors
@ajax_request
#@cache_page(CACHE_INTERVAL)
def apply_def(request):
    sexps = tuple(request.POST.getlist('selections[]'))

    # Handle client-side ID
    namespace_index = int( request.POST.get('namespace_index') )

    if not namespace_index:
        raise Exception('No namespace index given in request.')

    uid = uidgen(namespace_index)

    # Build up the pure representation of the definition from
    # the sexp

    def_sexp = request.POST.get('def')

    if not def_sexp:
        raise Exception('No definiton specified.')

    def_py = translate.parse_sexp(def_sexp,uid)
    def_pure = purify(def_py)

    # ---

    args = [translate.parse_sexp(sexp, uid) for sexp in sexps]

    for arg in args:
        arg.idgen = uid

    # Init a new lexical closure
    # >>>>>>>>>>>>>>>>>>>>>>>>>>
    pure_wrap.new_level()

    # Init the local definition
    def_pure()

    # Evaluate the selection in the context of the definition
    pure_expr = pure_wrap.p2i(purify(args[0]))
    print 'Acting on', pure_expr

    pure_wrap.restore_level()
    # <<<<<<<<<<<<<<<<<<<<<<<<<<
    # Close the closure and return to the main level

    new = translate.pure_to_python(pure_wrap.i2p(pure_expr),args[0].idgen)

    new.idgen = uid
    new.ensure_id()

    new_html = [html(new)]
    new_json = [json_flat(new)]

    return JsonResponse({'new_html': new_html,
                         'new_json': new_json,
                         'namespace_index': uid.next()[3:]})


@login_required
@errors
#@cache_page(CACHE_INTERVAL)
def rules_request(request):
    return render_haml_to_response('ruleslist.tpl',
            {'rulesets':rules.rulesets})

#@login_required
#@errors
#@ajax_request
#@cache_page(CACHE_INTERVAL)
#def lookup_transform(request):
#    typs = tuple(request.POST.getlist('selections[]'))
#
#    def str_to_mathtype(typ):
#        return mathobjects.__dict__[typ]
#
#    domain = tuple( map(str_to_mathtype, typs) )
#
#    def compatible_pred(obj_types, fun_signature):
#        if len(obj_types) != len(fun_signature): return False
#        return all(issubclass(ot, ft) for ot, ft in zip(obj_types, fun_signature))
#
#    def get_comptables(obj_types, fun_signatures):
#        return [t for t in fun_signatures if compatible_pred(obj_types, t.domain)]
#
#    compatible_mappings = get_comptables( domain, mathobjects.algebra.mappings)
#
#    if not compatible_mappings:
#        return JsonResponse({'empty': True})
#
#    mappings_list = [(m.pretty , m.internal) for m in compatible_mappings]
#
#    return JsonResponse(mappings_list)


@login_required
@errors
@ajax_request
def use_infix(request):
    # TODO: We should preparse this and define a lookup table 
    # for a bunch of common macros instead of just passing
    # this off to Pure eval, otherwise we get kind of unwiedly
    # constructions of things ex: Tuple x y z could be better
    # written as (x,y,z) and there really isn't any reason the
    # user would need to init a Pure tuple from the cmdline

    code = request.POST.get('code')
    transform = unencode( request.POST.get('transform') )
    namespace_index = int( request.POST.get('namespace_index') )
    uid = uidgen(namespace_index)

    # TODO: This is dangerous
    pure_expr = pure_wrap.i2p(pure_wrap.env.eval(code))
    new_expr_tree = translate.pure_to_python(pure_expr)
    new_expr_tree.uid_walk(uid)

    return JsonResponse({'new_html': [html(new_expr_tree)],
                         'new_json': [json_flat(new_expr_tree)],
                         'namespace_index': uid.next()[3:]})


@login_required
@errors
@ajax_request
def apply_transform(request):
    code = tuple(request.POST.getlist('selections[]'))
    transform = unencode( request.POST.get('transform') )
    namespace_index = int( request.POST.get('namespace_index') )

    uid = uidgen(namespace_index)

    args = [translate.parse_sexp(cde) for cde in code]

    try:
        pack, fun = transform.split('/')
        transform = transforms.get_transform_by_path(pack, fun)
    except KeyError:
        raise exception.NoSuchTransform(transform)

    #Ugly hack to allow us to pass the uid generator and use it
    # in the middle of a transformation in case we need to
    # generate a whole new batch of uids (like when converting
    # pure <-> python ).
    for arg in args:
        arg.idgen = uid

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
@errors
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
        new.uid_walk(uid)
    elif newtype == u'func':
        new = translate.parse_sexp('(Function (Placeholder) (Placeholder) (Placeholder))',uid)
    elif newtype == u'eq':
        new = EquationPrototype()
        new.uid_walk(uid)
    elif newtype == u'assum':
        new = AssumptionPrototype()
        new.uid_walk(uid)
    else:
        new = translate.parse_sexp(newtype)
        new.uid_walk(uid)

    return JsonResponse({'new_html': html(new),
                         'new_json': json_flat(new),
                         'namespace_index': uid.next()[3:],
                         'cell_index': cell_index + 1})

@errors
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

    # Create a new uid generator
    uid = uidgen(namespace_index)

    # Create any empty equation in the new cell
    # new_eq = EquationPrototype()
    # new_eq.uid_walk(uid)

    new_cell = PyCell([],[])
    new_cell.index = cell_index + 1;

    return JsonResponse({'new_html': html(new_cell),
                         'new_json': json_flat(new_cell),
                         'namespace_index': uid.next()[3:],
                         'cell_index': cell_index + 1})

#vim: ai ts=4 sts=4 et sw=4
