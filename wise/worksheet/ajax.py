# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import translate

import mathobjects
import transforms
import rules
import pure_wrap

from django import template

from django.conf import settings
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, Http404

from wise.worksheet.utils import *
from wise.worksheet.models import Workspace, MathematicalEquation, Cell, Symbol, Function, Rule, RuleSet
import wise.worksheet.exceptions as exception

CACHE_INTERVAL = 30*60 # 5 Minutes

#---------------------------
# Rules --------------------
#---------------------------

#@login_required
#@errors
#@ajax_request
#@cache_page(CACHE_INTERVAL)
#def apply_rule(request):
#    code = tuple(request.POST.getlist('selections[]'))
#    set_id = int( request.POST.get('set_id') )
#    rule_id = request.POST.get('rule_id')
#
#    if rule_id != 'null':
#        rule_id = int(rule_id)
#    else:
#        rule_id = None
#
#    #debug(code)
#    namespace_index = int( request.POST.get('namespace_index') )
#
#    uid = uidgen(namespace_index)
#
#    args = [translate.parse_sexp(cde, uid) for cde in code]
#
#    #Ugly hack to allow us to pass the uid generator and use it
#    # in the middle of a transformation in case we need to
#    # generate a whole new batch of uids (like when converting
#    # pure <-> python ).
#    for arg in args:
#        arg.idgen = uid
#
#    # Load a specific rule
#    if rule_id:
#        rule = Rule.objects.get(id=rule_id)
#        rule_strings = [rule.pure]
#
#    # Load all rules in the ruleset
#    else:
#        rs = RuleSet.objects.get(id=set_id)
#        rules_q = Rule.objects.filter(set=rs,confluent=True).order_by('index')
#        rule_strings = [rule.pure for rule in rules_q]
#
#    # If the Rule is flagged as an external reference go fetch it
#    if rule.external == True:
#        try:
#            pack, symbol = rule.pure.split('/')
#        except ValueError:
#            raise Exception("Reference to external pure symbol is not well-formed: %s" % rule.pure)
#
#        ref = pure_wrap.objects[symbol]
#        new = rules.ApplyExternalRule(ref,args[0])
#
#    # ... otherwise build it up from the given sexp string.
#    else:
#        new = rules.ReduceWithRules(rule_strings,args[0])
#
#    new.idgen = uid
#    new.ensure_id()
#
#    new_html = [html(new)]
#    new_json = [json_flat(new)]
#
#    return JsonResponse({'new_html': new_html,
#                         'new_json': new_json,
#                         'namespace_index': uid.next()[3:]})

@login_required
@errors
@ajax_request
#@cache_page(CACHE_INTERVAL)
def apply_rule(request):
    code = tuple(request.POST.getlist('selections[]'))

    rule = request.POST.get('rule')

    namespace_index = int( request.POST.get('namespace_index') )

    if not namespace_index:
        raise Exception('No namespace index given in request')
    uid = uidgen(namespace_index)
    args = [translate.parse_sexp(cde, uid) for cde in code]


    #Ugly hack to allow us to pass the uid generator and use it
    # in the middle of a transformation in case we need to
    # generate a whole new batch of uids (like when converting
    # pure <-> python ).
    for arg in args:
        arg.idgen = uid

    # Change this to rules[rule]
    ref = pure_wrap.objects[rule]
    new = rules.ApplyExternalRule(ref,*args)

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

    #if settings.DEBUG:
    #    ruleslist = [(rule.ref, rule) for rule in rules.rulesets.itervalues()]
    #else:
    #    ruleslist = [(name, rule) for (name,rule) in rules.rulesets.iteritems()]

    return render_haml_to_response('ruleslist.tpl',{'rulesets':rules.rulesets})

#---------------------------
# Symbols ------------------
#---------------------------

@login_required
@errors
#@cache_page(CACHE_INTERVAL)
def symbols_request(request):
    symbols = Symbol.objects.filter(owner=request.user)
    symbols_html = [mathobjects.RefSymbol(sym).get_html() for sym in symbols]
    descriptions = [sym.desc for sym in symbols]

    return render_haml_to_response('symbolslist.tpl',{'symbols':zip(symbols_html,descriptions)})

#---------------------------
# Functions ----------------
#---------------------------

@login_required
@errors
#@cache_page(CACHE_INTERVAL)
def functions_request(request):
    ph = mathobjects.Placeholder()
    functions = Function.objects.filter(owner=request.user)
    functions_html = [mathobjects.RefOperator(fun,ph).get_html() for fun in functions]
    descriptions = [fun.desc for fun in functions]

    return render_haml_to_response('functionslist.tpl',{'functions':zip(functions_html,descriptions)})

@login_required
@errors
@ajax_request
@cache_page(CACHE_INTERVAL)
def preview_function(request):
    symbol1 = request.POST.get('symbol1')
    notation = request.POST.get('notation')
    pnths = request.POST.get('pnths')
    notation = request.POST.get('notation').lower()
    arity = request.POST.get('arity')

    if not arity:
        arity = 1
    else:
        arity = int(arity)

    ph = mathobjects.Placeholder()

    if notation == 'infix':
        prvw = mathobjects.Operation(ph,ph)
    else:
        prvw = mathobjects.Operation(*([ph]*arity))

    prvw.symbol = symbol1
    prvw.notation = notation
    prvw.show_parenthesis = pnths is not None
    prvw.ui_style = notation

    return HttpResponse(html(prvw))

@login_required
@errors
@ajax_request
@cache_page(CACHE_INTERVAL)
def pure_parse(request):
    namespace_index = request.POST.get('namespace_index')
    code = request.POST.get('code')

    if not namespace_index:
        namespace_index = 0
    else:
        namespace_index = int(namespace_index)

    cell_index = int( request.POST.get('cell_index') )

    uid = uidgen(namespace_index)
    new = translate.pure_to_python(code,uid)

    newline_html = cellify(html(new),cell_index+1)

    return JsonResponse({'new_html': newline_html,
                         'new_json': json_flat(new),
                         'namespace_index': uid.next()[3:],
                         'cell_index': cell_index + 1})

@login_required
@errors
@ajax_request
@cache_page(CACHE_INTERVAL)
def lookup_transform(request):
    typs = tuple(request.POST.getlist('selections[]'))

    def str_to_mathtype(typ):
        return mathobjects.__dict__[typ]

    domain = tuple( map(str_to_mathtype, typs) )

    def compatible_pred(obj_types, fun_signature):
        if len(obj_types) != len(fun_signature): return False
        return all(issubclass(ot, ft) for ot, ft in zip(obj_types, fun_signature))

    @memoize
    def get_comptables(obj_types, fun_signatures):
        return [t for t in fun_signatures if compatible_pred(obj_types, t.domain)]

    compatible_mappings = get_comptables( domain, mathobjects.algebra.mappings)

    if not compatible_mappings:
        return JsonResponse({'empty': True})

    mappings_list = [(m.pretty , m.internal) for m in compatible_mappings]

    return JsonResponse(mappings_list)

@login_required
@errors
@ajax_request
@cache_page(CACHE_INTERVAL)
def combine(request):
    first = unencode( request.POST.get('first') )
    second = unencode( request.POST.get('second') )
    context = unencode( request.POST.get('context') )
    namespace_index = int( request.POST.get('namespace_index') )

    uid = uidgen(namespace_index)

    first = translate.parse_sexp(first,uid)
    second = translate.parse_sexp(second,uid)

    # The combination of the two elements (if a rule exists),
    # otherwise default to just the whatever the container the
    # two objects coexist in requires.
    new_html, objs = first.combine(second,context)
    new_json = map(json_flat, objs)

    return JsonResponse({'new_html': new_html,
                         'new_json': new_json,
                         'namespace_index': uid.next()[3:]})

@login_required
@errors
@ajax_request
@cache_page(CACHE_INTERVAL)
def apply_transform(request):
    code = tuple(request.POST.getlist('selections[]'))
    transform = unencode( request.POST.get('transform') )
    namespace_index = int( request.POST.get('namespace_index') )

    uid = uidgen(namespace_index)

    args = [translate.parse_sexp(cde, uid) for cde in code]

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

    new = transform(*args)

    #Yah, this is ugly
    if hasattr(new,'__iter__'):
        for nval in new:
            if not isinstance(nval,str):
                nval.idgen = uid
                nval.ensure_id()
    else:
        new.idgen = uid
        new.ensure_id()

    #Yah, remove this soon. UGLY
    def mappy_html(obj):
        if isinstance(obj,str):
            return obj
        else:
            return html(obj)

    def mappy_json(obj):
        if isinstance(obj,str):
            return obj
        else:
            return json_flat(obj)

    new_html = maps(mappy_html, new)
    new_json = maps(mappy_json, new)

    return JsonResponse({'new_html': new_html,
                         'new_json': new_json,
                         'namespace_index': uid.next()[3:]})

@login_required
@errors
@ajax_request
@cache_page(CACHE_INTERVAL)
def save_workspace(request,eq_id):
    try:
        workspace = Workspace.objects.get(id=eq_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error':'Workspace is missing'})

    cells = Cell.objects.filter(workspace=eq_id)

    for cell in cells:
        cell.delete()

    #TODO this is crazy dangerous
    indexes = len(request.POST)

    for i in xrange(indexes):
        newcell = Cell(workspace=workspace,index=0)
        newcell.save()
        #Querydicts are not standard dicts... keep repeating this
        math, annotation = request.POST.getlist(''.join([str(i),'[]']))

        #TODO: Do some fancy string parsing to transform [[ x^2 ]] -> $$ x^2 $$
        MathematicalEquation(code=math,
                annotation=annotation,
                cell=newcell,
                index=i).save()

    return JsonResponse({'success': True})

@login_required
@errors
@ajax_request
@cache_page(CACHE_INTERVAL)
def save_ruleset(request,rule_id):
    try:
        ruleset = RuleSet.objects.get(id=rule_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error':'Rule Set is missing'})

    rules = Rule.objects.filter(set=rule_id)

    for rule in rules:
        rule.delete()

    #TODO this is crazy dangerous
    indexes = len(request.POST)
    uid = uidgen()

    for i in xrange(indexes):
        math, annotation, is_confluent, is_public = request.POST.getlist(''.join([str(i),'[]']))
        pure = translate.parse_sexp(math,uid)._pure_()

        is_confluent = (is_confluent == '1')
        is_public = (is_public == '1')

        print is_confluent, is_public

        newrule = Rule(sexp=math,
                pure=pure,
                annotation=annotation,
                set=ruleset,
                public=True,
                confluent=is_confluent,
                index=i).save()

    return JsonResponse({'success': True})

@login_required
@errors
@ajax_request
@cache_page(CACHE_INTERVAL)
def receive(request):
    obj = unencode( request.POST.get(u'obj') )
    obj_type = unencode( request.POST.get('obj_type') )

    receiver = unencode( request.POST.get('receiver') )
    receiver_type = unencode( request.POST.get('receiver_type') )
    receiver_context = unencode( request.POST.get('receiver_context') )

    sender = unencode( request.POST.get('sender') )
    sender_type = unencode( request.POST.get('sender_type') )
    sender_context = unencode( request.POST.get('sender_context') )

    new_position = unencode( request.POST.get('new_position') )

    namespace_index = request.POST.get('namespace_index')

    if not namespace_index:
        raise exception.PostDataCorrupt('namespace_index')

    uid = uidgen(int(namespace_index))

    inserted = translate.parse_sexp(obj, uid )
    received = translate.parse_sexp(receiver, uid )

    new = received.receive(inserted,receiver_context,sender_type,sender_context,new_position)
    new.idgen = uid
    new.ensure_id()

    return JsonResponse({'new_html': html(new),
                         'new_json': json_flat(new),
                         'namespace_index': uid.next()[3:]})

@login_required
@errors
@ajax_request
@cache_page(CACHE_INTERVAL)
def remove(request):
    obj = unencode( request.POST.get(u'obj') )
    obj_type = unencode( request.POST.get('obj_type') )

    sender = unencode( request.POST.get('sender') )
    sender_type = unencode( request.POST.get('sender_type') )
    sender_context = unencode( request.POST.get('sender_context') )

    namespace_index = int( request.POST.get('namespace_index') )

    uid = uidgen(namespace_index)

    obj = translate.parse_sexp(obj,uid)
    sender = translate.parse_sexp(sender,uid)

    new = sender.remove(obj,sender_context)
    if new:
        new.idgen = uid
        new.ensure_id()

    return JsonResponse({'new_html': html(new),
                         'new_json': json_flat(new),
                         'namespace_index': uid.next()[3:]})

@login_required
@errors
@ajax_request
@cache_page(CACHE_INTERVAL)
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
        new = translate.parse_sexp('(Definition (LHS (Placeholder )) (RHS (Placeholder )))',uid)
    elif newtype == u'eq':
        new = translate.parse_sexp('(Equation (LHS (Placeholder )) (RHS (Placeholder )))',uid)
    else:
        error('invalid type of inline')
    newline_html = cellify(html(new),cell_index+1)

    return JsonResponse({'new_html': newline_html,
                         'new_json': json_flat(new),
                         'namespace_index': uid.next()[3:],
                         'cell_index': cell_index + 1})
