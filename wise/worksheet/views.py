'''
Wise
Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import traceback
import parser
import mathobjects
from decorator import decorator

from django import template

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import simplejson as json
from django.utils.html import strip_spaces_between_tags as strip_whitespace
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.cache import cache_page

from wise.worksheet.forms import LoginForm
from wise.worksheet.models import Workspace, MathematicalEquation, Cell, Symbol, Function

CACHE_INTERVAL = 30*60 # 5 Minutes

# Wraps errors out to server log and javascript popup
def errors(f):
    def wrapper(*args,**kwargs):
        try:
            return f(*args,**kwargs)
        except Exception,e:
            print e
            print traceback.print_exc()
            return HttpResponse(json.dumps({'error': str(e)}))
    return wrapper

#Strip unicode
def unencode(s):
    if type(s) is list:
        s = s[0]
    elif s is None:
        return None
    fileencoding = "iso-8859-1"
    txt = s.decode(fileencoding)
    return str(txt)

def _memoize(func, *args, **kw):
    if kw: # frozenset is used to ensure hashability
        key = args, frozenset(kw.iteritems())
    else:
        key = args
    cache = func.cache # attributed added by memoize
    if key in cache:
        return cache[key]
    else:
        cache[key] = result = func(*args, **kw)
        return result

# All these methods are null-safe, so if you pass anything that
# is null it just maps to None
def minimize_html(html):
    if not html:
        return None
    return strip_whitespace(html.rstrip('\n'))

def html(obj):
    if not obj:
        return None
    return minimize_html(obj.get_html())

def json_flat(obj):
    if not obj:
        return None
    return obj.json_flat()

def memoize(f):
    f.cache = {}
    return decorator(_memoize, f)

def cellify(s,index):
    return '<div class="cell" data-index="%s"><table class="lines" style="display: none">%s</table></div>' % (index, s)


def parse(code, uid):
    parsed = mathobjects.ParseTree(code)
    parsed.gen_uids(uid)
    evaled = parsed.eval_args()
    return evaled

def maps(func, obj):
    '''It's like map() but awesomer, namely in that you can pass
    a single argument to it and it doesn't crash and burn'''

    if hasattr(obj,'__iter__'):
        return map(func, obj)
    return [func(obj)]

def JSONResponse(obj):
    '''Convenience wrapper for JSON responses'''
    return HttpResponse(json.dumps(obj), mimetype="application/json")

def uidgen(i=0):
    while True:
        yield 'uid%i' % i
        i += 1

def account_login(request):
    form = AuthenticationForm()

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        redirect = request.GET['next']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(redirect)
            else:
                return HttpResponse('Account Disabled')
                # Return a 'disabled account' error message
        else:
            return render_to_response('login.html', {'form': form, 'errors': ['Invalid Login']})
            # Return an 'invalid login' error message.
    else:
        return render_to_response('login.html', {'form': form})


def account_logout(request):
    logout(request)
    # Redirect to a success page.
    return HttpResponse('Logged Out')

@errors
def test(request):
    add = mathobjects.pure.add
    rational = mathobjects.pure.rational
    one = mathobjects.pure.PureInt(1)
    two = mathobjects.pure.PureInt(2)
    sage_test = str(rational(one,two))
    pure_exp = mathobjects.parse_pure_exp(sage_test)
    return render_to_response('index.html',{'sage': pure_exp.get_html()})

@login_required
def home(request):
    workspaces = Workspace.objects.filter(owner=request.user)
    return render_to_response('home.html', {'workspaces': workspaces})

@errors
@login_required
def symbols_list(request):
    try:
        symbols = Symbol.objects.filter(owner=request.user)
    except ObjectDoesNotExist:
        pass

    return render_to_response('symbols_list.html', {'symbols': symbols})

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

@login_required
def sym(request, sym_id):

    try:
        symbol = Symbol.objects.get(id=sym_id)

        if ( symbol.owner.id != request.user.id ) and not symbol.public:
            return HttpResponse('You do not have permission to access this symbol.')

    except ObjectDoesNotExist:
        symbol = None
    return render_to_response('symbol_edit.html', {'symbol': symbol})

@login_required
def sym_update(request):
    sym_id = request.POST.get('sym_id')

    name = request.POST.get('name')
    tex = request.POST.get('tex')
    desc = request.POST.get('desc')
    public = request.POST.get('public') is not None

    sym = Symbol.objects.filter(id=sym_id)

    if sym:
        sym.update(name=name,tex=tex,public=public,desc=desc,owner=request.user)
    else:
        Symbol(name=name,tex=tex,public=public,desc=desc,owner=request.user).save()

    return HttpResponseRedirect('/sym')

def fun_list(request):
    functions = Function.objects.filter(owner=request.user)
    return render_to_response('fun_list.html', {'functions': functions})

@login_required
def fun(request, sym_id):
    try:
        function = Function.objects.get(id=sym_id)

        if ( function.owner.id != request.user.id ) and not function.public:
            return HttpResponse('You do not have permission to access this function.')

    except ObjectDoesNotExist:
        function = None
    return render_to_response('fun_edit.html', {'function': function})

@login_required
def fun_update(request, sym_id):
    new = request.GET.get('new')
    name = request.GET.get('name')
    tex = request.GET.get('tex')
    desc = request.GET.get('desc')
    public = request.GET.get('public') is not None

    sym = Symbol.objects.filter(id=sym_id)

    if sym:
        sym.update(name=name,tex=tex,public=public,desc=desc,owner=request.user)
    else:
        Symbol(name=name,tex=tex,public=public,desc=desc,owner=request.user).save()

    return HttpResponseRedirect('/sym')

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

@cache_page(CACHE_INTERVAL)
def palette(request):
    return generate_palette()

@errors
def sage_parse(request, eq_id):
    sage = unencode( request.POST.get('sage') )
    if not sage:
        sage = unencode( request.GET.get('sage') )

    code = sage.split('\n')

    parsd = run_code(code)

    if parsd:
        return JSONResponse({'newline': html(parsd)})
    else:
        return JSONResponse({'error': 'Could not parse Sage input.'})

@errors
def sage_inline(request, eq_id):
    code = unencode( request.POST.get('sage') )

    common = {'x': mathobjects.Variable('x')}

    if code in common:
        print 'common'
        return JSONResponse(html(common[code]))

    executed = run_code(code)

    if executed:
        return JSONResponse(html(executed))
    else:
        return JSONResponse({'error': 'Could not parse Sage input.'})

def run_code(code,ecmds=list()):
    try:
        evald = mathobjects.sage.sage_eval(code)
        parsd = mathobjects.parse_sage_exp(evald)
        return parsd
    except NameError, e:
        m = str(e).split()[1]
        code.insert(0,( 'var(%s)\n' % m ))
        return run_code(code)

@login_required
@errors
def ws(request, eq_id):
    ws = Workspace.objects.get(id=eq_id)

    if ( ws.owner.id != request.user.id ) and not ws.public:
        return HttpResponse('You do not have permission to access this worksheet.')

    try:
        cells = Cell.objects.filter(workspace=eq_id)
    except ObjectDoesNotExist:
        return HttpResponse('No cells found in worksheet')

    debug_parse_tree = request.GET.get('tree')
    uid = uidgen()

    json_cells = []
    html_cells = []

    for index,cell in enumerate(cells):
        json_cell = []
        html_eq = []

        try:
            eqs = MathematicalEquation.objects.filter(cell=cell)
        except ObjectDoesNotExist:
            return HttpResponse('Cell is empty.')

        for eq in eqs:
            eqtext = unencode(eq.code)
            tree = mathobjects.ParseTree(eqtext)
            tree.gen_uids(uid)

            #For debugging... 
            if debug_parse_tree:
                pretty_tree = mathobjects.pretty(tree)
                etree = tree.eval_args()
                print etree._sage_()

                tree = '<pre>%s</pre>' % pretty_tree
                outputs += tree

            else:
                etree = tree.eval_args()
                html_eq.append(html(etree))
                json_cell.append(etree.json_flat())

        #This is stupid unintuitive syntax
        html_cells.append(cellify(''.join(html_eq),index))
        json_cells.append(json_cell)

    if debug_parse_tree:
        return HttpResponse( outputs )
    else:
        return render_to_response('worksheet.html', {
            'title': ws.name,
            'equations': html_cells,
            'username': request.user.username,
            'namespace_index': uid.next()[3:],
            'cell_index': len(cells),
            'json_cells': json.dumps(json_cells),
            })

@errors
def json_tree(request, eq_id):
    eqs = MathematicalEquation.objects.filter(workspace=eq_id)
    uid = uidgen()
    json_list = []

    for eq in eqs:
        code = eq.code
        tree = mathobjects.ParseTree(code)
        tree.gen_uids(uid)

        json_list.append(tree.json_flat())

    return JSONResponse(json_list)

@login_required
@errors
@cache_page(CACHE_INTERVAL)
def lookup_transform(request, eq_id):
    typs = tuple(request.POST.getlist('selections[]'))
    #print [i for i in mathobjects.algebra.mappings]

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
        return JSONResponse({'empty': True})

    mappings_list = [(m.pretty , m.internal) for m in compatible_mappings]

    return JSONResponse(mappings_list)

@login_required
@errors
@cache_page(CACHE_INTERVAL)
def combine(request,eq_id):
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

    return JSONResponse({'new_html': new_html,
                         'new_json': new_json,
                         'namespace_index': uid.next()[3:]})

@errors
def unserialize(string):
    string = unencode(string)
    a = string.split('&')
    d = {}
    for i in a:
        b = i.split('=')
        d[unencode(b[0])] = unencode(b[1])
    return d

def new(request):
    pass

@login_required
@errors
def apply_transform(request,eq_id):
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

    return JSONResponse({'new_html': new_html,
                         'new_json': new_json,
                         'namespace_index': uid.next()[3:]})

@login_required
@errors
def save_workspace(request,eq_id):
    try:
        workspace = Workspace.objects.get(id=eq_id)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({'error':'Workspace is missing'}))

    eqs = MathematicalEquation.objects.filter(workspace=eq_id)

    #Delete old elements in the workspace
    data = {}
    for eq in eqs:
        eq.delete()

    #TODO this is crazy dangerous
    indexes = len(request.POST)

    for i in xrange(indexes):
        math = request.POST.get(str(i))
        MathematicalEquation(code=math, workspace=workspace).save()

    return HttpResponse(json.dumps({'success': True}))

@login_required
@errors
def del_workspace(request):
    #TODO this is crazy dangerous
    for id,s in request.POST.iteritems():
        MathematicalEquation.objects.filter(workspace=id).delete()
        Workspace.objects.get(id=id).delete()
    return HttpResponseRedirect('/home')

@login_required
@errors
def new_workspace(request):
    name = unencode( request.POST.get('name') )
    init = unencode( request.POST.get('init') )

    new_workspace = Workspace(name=name,owner=request.user,public=False)
    new_workspace.save()
    new_id = new_workspace.id

    if init == 'Equation':
        RHS = mathobjects.RHS(mathobjects.Placeholder())
        LHS = mathobjects.LHS(mathobjects.Placeholder())
        equation = mathobjects.Equation(LHS,RHS).get_math()
    else:
        equation = mathobjects.Placeholder().get_math()

    init_eq = MathematicalEquation(code=equation, workspace=new_workspace).save()
    return HttpResponseRedirect('/home')

@login_required
@errors
@cache_page(CACHE_INTERVAL)
def receive(request,eq_id):
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

    return JSONResponse({'new_html': html(new),
                         'new_json': json_flat(new),
                         'namespace_index': uid.next()[3:]})

@login_required
@errors
@cache_page(CACHE_INTERVAL)
def remove(request,eq_id):
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

    return JSONResponse({'new_html': html(new),
                         'new_json': json_flat(new),
                         'namespace_index': uid.next()[3:]})

@login_required
@errors
@cache_page(CACHE_INTERVAL)
def new_inline(request, eq_id):
    namespace_index = int( request.POST.get('namespace_index') )
    cell_index = int( request.POST.get('cell_index') )

    uid = uidgen(namespace_index)

    # TODO we should do this without parsing, this is really slow
    # and inefficent
    new = parse('(Definition (LHS (Placeholder )) (RHS (Placeholder )))',uid)
    newline_html = cellify(html(new),cell_index+1)

    return JSONResponse({'new_html': newline_html,
                         'new_json': json_flat(new),
                         'namespace_index': uid.next()[3:],
                         'cell_index': cell_index + 1})

palette_template = '''
{% for group in palette %}
    <h3><a href="#">{{ group.name }}</a></h3>
    <div>

        {% ifequal group.type 'tabular' %}
            <table class="palette">
                {% for name, html in group.objects %}
                    <tr>
                        <td>{{ name }}</td>
                        <td>{{ html }}</td>
                    </tr>
                {% endfor %}
            </table>
        {% endifequal %}

        {% ifequal group.type 'array' %}
            {% for html in group.objects %}
                {{ html }}
            {% endfor %}
        {% endifequal %}

        {% ifequal group.type 'widget' %}
        {% endifequal %}

    </div>
{% endfor %}
'''

@errors
def generate_palette():
    #TODO Be able to include snippts of html as widgets in the
    #palette

    def Placeholder():
        return mathobjects.Placeholder()

    constants = {'name': 'Constants', 'type': 'array', 'objects': [
                    mathobjects.E().get_html(),
                    mathobjects.Pi().get_html(),
                    mathobjects.Khinchin().get_html(),
                ]}

    import string
    lettervariables = [mathobjects.Variable(letter).get_html() for letter in string.lowercase]

    patternmatching = {'name': 'Pattern Matching', 'type': 'array', 'objects': [
#                    mathobjects.Variable('x').get_html(),
#                    mathobjects.Variable('y').get_html(),
#                    mathobjects.Variable('z').get_html(),
                    mathobjects.AbstractFunction('f').get_html(),
                    mathobjects.Variable('u').get_html(),
#                    mathobjects.IntVariable('xint').get_html(),
                ]}

    variables = {'name': 'Variables', 'type': 'array', 'objects': lettervariables }

    trig = {'name': 'Functions', 'type': 'tabular', 'objects': [
                    ('Sine', mathobjects.Sine(Placeholder()).get_html()),
                    ('Cosine', mathobjects.Cosine(Placeholder()).get_html()),
                    ('Tangent', mathobjects.Tangent(Placeholder()).get_html()),
                    ('Secant', mathobjects.Secant(Placeholder()).get_html()),
                    ('Cosecant', mathobjects.Cosecant(Placeholder()).get_html()),
                    ('Cotangent', mathobjects.Cotangent(Placeholder()).get_html()),
                    ('Logarithm', mathobjects.Log(Placeholder()).get_html()),
                ]}

    operations = {'name': 'Operations', 'type': 'tabular', 'objects': [
                    ('Addition', mathobjects.Addition(*[Placeholder(),Placeholder()]).get_html()),
                    ('Negation', mathobjects.Negate(Placeholder()).get_html()),
                    ('Product', mathobjects.Product(*[Placeholder(),Placeholder()]).get_html()),
                    ('Fraction', mathobjects.Fraction(Placeholder(),Placeholder()).get_html()),
                    ('Power', mathobjects.Power(Placeholder(),Placeholder()).get_html()),
                    ('Wedge', mathobjects.Wedge(Placeholder(),Placeholder()).get_html()),
                    ('Integral', mathobjects.Integral(Placeholder(),mathobjects.Differential(Placeholder())).get_html()),
                    ('Partial Derivative', mathobjects.Diff(Placeholder(),Placeholder()).get_html()),
                    ('Derivative', mathobjects.FDiff(Placeholder(),Placeholder()).get_html()),
                    ('Laplacian', mathobjects.Laplacian(Placeholder()).get_html()),
                ]}

    numbers = {'name': 'Numbers', 'type': 'array', 'objects': [
                    mathobjects.Numeric(x).get_html() for x in range(0,10)
                ]}

    physics = {'name': 'Physics', 'type': 'tabular', 'objects': [
                    ('Length', mathobjects.Length(Placeholder()).get_html()),
                ]}

    palette = [trig,variables,operations,numbers,physics,constants, patternmatching]

    interface_ui = template.Template(palette_template)
    c = template.Context({'palette':palette})

    return HttpResponse(interface_ui.render(c))
