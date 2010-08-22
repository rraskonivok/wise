import parser

import mathobjects
# Foundational math objects
import base

from logger import debug, getlogger
from django import template

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import simplejson as json
from django.utils.html import strip_spaces_between_tags as strip_whitespace
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from wise.worksheet.utils import *
from wise.worksheet.models import Workspace, MathematicalEquation, Cell, Symbol, Function, Rule, RuleSet

CACHE_INTERVAL = 30*60 # 5 Minutes

#---------------------------
# Rules --------------------
#---------------------------

@errors
@login_required
def apply_rule(request):
    code = tuple(request.POST.getlist('selections[]'))
    set_id = int( request.POST.get('set_id') )
    rule_id = request.POST.get('rule_id')

    if rule_id != 'null':
        rule_id = int(rule_id)
    else:
        rule_id = None

    #debug(code)
    namespace_index = int( request.POST.get('namespace_index') )

    uid = uidgen(namespace_index)

    args = [parse(cde, uid) for cde in code]
    print 'sexp', args[0]
    transform = mathobjects.algebra.ReduceWithRules

    #Ugly hack to allow us to pass the uid generator and use it
    # in the middle of a transformation in case we need to
    # generate a whole new batch of uids (like when converting
    # pure <-> python ).
    for arg in args:
        arg.idgen = uid


    #Apply a specific rule
    if rule_id:
        rule = Rule.objects.get(id=rule_id)
        rule_strings = [rule.pure]

    #Apply all rules in the ruleset
    else:
        rs = RuleSet.objects.get(id=set_id)
        rules = Rule.objects.filter(set=rs,confluent=True).order_by('index')
        rule_strings = [rule.pure for rule in rules]

    new = transform(rule_strings,args[0])

    new.idgen = uid
    new.ensure_id()

    new_html = [html(new)]
    new_json = [json_flat(new)]

    return JsonResponse({'new_html': new_html,
                         'new_json': new_json,
                         'namespace_index': uid.next()[3:]})

ruleslist = '''
{% load custom_tags %}
<ul>
{% for rule in rules%}
    <li><a class='ruletoplevel' href="javascript:apply_rule({{rule.0.id}},null);">{{ rule.0.name }}</a>
        <a class='expand'>[+]</a>
        <ul style="display: none">
        {% for subrule in rule.1 %}
            <li><a
            href="javascript:apply_rule({{rule.0.id}},{{subrule.id}});">{{ subrule.annotation|brak2tex }}</a></li>
        {% endfor %}
        </ul>
    </li>
{% endfor %}
</ul>
'''

@errors
@login_required
def rules_request(request):
    ruleset = RuleSet.objects.filter(owner=request.user)
    subrules = []

    for rs in ruleset:
        rss = Rule.objects.filter(set=rs,public=True).order_by('index')
        subrules.append(rss)

    lst = template.Template(ruleslist)
    c = template.Context({'rules':zip(ruleset,subrules)})
    return HttpResponse(lst.render(c))

#---------------------------
# Symbols ------------------
#---------------------------

symbolslist = '''
<table style="width: 100%">
{% for symbol in symbols%}
    <tr>
    <td>{{ symbol.0 }}</td>
    <td>{{ symbol.1 }}</td>
    <tr>
{% endfor %}
</table>
'''

@errors
@login_required
def symbols_request(request):
    symbols = Symbol.objects.filter(owner=request.user)
    symbols_html = [mathobjects.RefSymbol(sym).get_html() for sym in symbols]
    descriptions = [sym.desc for sym in symbols]

    lst = template.Template(symbolslist)
    c = template.Context({'symbols':zip(symbols_html,descriptions)})
    return HttpResponse(lst.render(c))

#---------------------------
# Functions ----------------
#---------------------------

functionslist = '''
<table style="width: 100%">
{% for function in functions%}
    <tr>
    <td>{{ function.0 }}</td>
    <td>{{ function.1 }}</td>
    <tr>
{% endfor %}
</table>
'''

@errors
@login_required
def functions_request(request):
    ph = mathobjects.Placeholder()
    functions = Function.objects.filter(owner=request.user)
    functions_html = [mathobjects.RefOperator(fun,ph).get_html() for fun in functions]
    descriptions = [fun.desc for fun in functions]

    lst = template.Template(functionslist)
    c = template.Context({'functions':zip(functions_html,descriptions)})
    return HttpResponse(lst.render(c))

@errors
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
def pure_parse(request):
    namespace_index = request.POST.get('namespace_index')
    code = request.POST.get('code')

    if not namespace_index:
        namespace_index = 0
    else:
        namespace_index = int(namespace_index)

    cell_index = int( request.POST.get('cell_index') )

    uid = uidgen(namespace_index)
    new = mathobjects.pure_to_python(code,uid)

    newline_html = cellify(html(new),cell_index+1)

    return JsonResponse({'new_html': newline_html,
                         'new_json': json_flat(new),
                         'namespace_index': uid.next()[3:],
                         'cell_index': cell_index + 1})

@login_required
@errors
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
@cache_page(CACHE_INTERVAL)
def combine(request):
    first = unencode( request.POST.get('first') )
    second = unencode( request.POST.get('second') )
    context = unencode( request.POST.get('context') )
    namespace_index = int( request.POST.get('namespace_index') )

    uid = uidgen(namespace_index)

    first = mathobjects.ParseTree(first)
    second = mathobjects.ParseTree(second)

    first.gen_uids(uid)
    second.gen_uids(uid)

    first = first.eval_args()
    second = second.eval_args()

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
def apply_transform(request):
    code = tuple(request.POST.getlist('selections[]'))
    transform = unencode( request.POST.get('transform') )
    namespace_index = int( request.POST.get('namespace_index') )

    uid = uidgen(namespace_index)

    args = [parse(cde, uid) for cde in code]

    transform = mathobjects.algebra.__dict__[transform]

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
def save_workspace(request,eq_id):
    try:
        workspace = Workspace.objects.get(id=eq_id)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({'error':'Workspace is missing'}))

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

    return HttpResponse(json.dumps({'success': True}))

@login_required
@errors
def save_ruleset(request,rule_id):
    try:
        ruleset = RuleSet.objects.get(id=rule_id)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({'error':'Rule Set is missing'}))

    rules = Rule.objects.filter(set=rule_id)

    for rule in rules:
        rule.delete()

    #TODO this is crazy dangerous
    indexes = len(request.POST)
    uid = uidgen()

    for i in xrange(indexes):
        math, annotation, is_confluent, is_public = request.POST.getlist(''.join([str(i),'[]']))
        pure = parse(math,uid)._pure_()

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

    return HttpResponse(json.dumps({'success': True}))

@login_required
@errors
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

    namespace_index = int( request.POST.get('namespace_index') )

    uid = uidgen(namespace_index)

    inserted = mathobjects.ParseTree(obj)
    received = mathobjects.ParseTree(receiver)

    inserted.gen_uids(uid)
    received.gen_uids(uid)

    inserted = inserted.eval_args()
    received = received.eval_args()

    new = received.receive(inserted,receiver_context,sender_type,sender_context,new_position)
    new.idgen = uid
    new.ensure_id()

    return JsonResponse({'new_html': html(new),
                         'new_json': json_flat(new),
                         'namespace_index': uid.next()[3:]})

@login_required
@errors
@cache_page(CACHE_INTERVAL)
def remove(request):
    obj = unencode( request.POST.get(u'obj') )
    obj_type = unencode( request.POST.get('obj_type') )

    sender = unencode( request.POST.get('sender') )
    sender_type = unencode( request.POST.get('sender_type') )
    sender_context = unencode( request.POST.get('sender_context') )

    namespace_index = int( request.POST.get('namespace_index') )

    uid = uidgen(namespace_index)

    obj = mathobjects.ParseTree(obj)
    sender = mathobjects.ParseTree(sender)

    obj.gen_uids(uid)
    sender.gen_uids(uid)

    obj = obj.eval_args()
    sender = sender.eval_args()

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
        new = parse('(Definition (LHS (Placeholder )) (RHS (Placeholder )))',uid)
    elif newtype == u'eq':
        new = parse('(Equation (LHS (Placeholder )) (RHS (Placeholder )))',uid)
    else:
        error('invalid type of inline')
    newline_html = cellify(html(new),cell_index+1)

    return JsonResponse({'new_html': newline_html,
                         'new_json': json_flat(new),
                         'namespace_index': uid.next()[3:],
                         'cell_index': cell_index + 1})
