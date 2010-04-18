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

from django import template
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import simplejson as json
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth.forms import AuthenticationForm

from django.utils.translation import ugettext_lazy as _, ugettext

from wise.worksheet.forms import LoginForm
from wise.worksheet.models import Equation, Workspace, MathematicalTransform, MathematicalIdentity

import parser
import mathobjects
#http://friggeri.net/blog/2008/12/21/jquery-gestures

#Wraps errors out to server log and javascript popup
def errors(f):
    def wrapper(*args,**kwargs):
        try:
            return f(*args,**kwargs)
        except Exception,e:
            print e
            print traceback.print_exc()
            return HttpResponse(json.dumps({'error': str(e)}))
    return wrapper


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


#Memoize single argument function
def memoize(f):
    def wrapper(*args):
        if args[0] in memo:
            return memo[args[0]]
        else:
            result = f(*args)
            memo[args] = result
            return result
    return wrapper


def test(request):
    '''
    workspaces = Workspace.objects.all()
    return render_to_response('home.html', {'workspaces': workspaces})
    '''
    try:
        x = mathobjects.sage.var('x')
        exp = x**2
        RHS = mathobjects.parse_sage_exp(mathobjects.sage.diff(exp))
        LHS = mathobjects.Diff(mathobjects.parse_sage_exp(exp))
        sage_test = mathobjects.Equation(mathobjects.LHS(LHS),mathobjects.RHS(RHS)).get_html()
    except Exception,e:
        sage_test = e

    return render_to_response('index.html',{'sage': sage_test})


@login_required
def home(request):
    workspaces = Workspace.objects.all()
    return render_to_response('home.html', {'workspaces': workspaces})

def palette(request):
    return generate_palette()

@errors
def sage_parse(request, eq_id):
    sage = unencode( request.POST.get('sage') )
    if not sage:
        sage = unencode( request.GET.get('sage') )

    sage = sage.split('\n')
    print sage

    evald = mathobjects.sage.sage_eval(sage)
    parsd = mathobjects.parse_sage_exp(evald)

    if parsd:
        js = json.dumps({'newline': parsd.get_html()})
    else:
        js = json.dumps({'error': 'Could not parse'})
    return HttpResponse(js)

@login_required
@errors
def ws(request, eq_id):
    ws = Workspace.objects.get(id=eq_id)
    eqs = Equation.objects.filter(workspace=eq_id)
    debug_parse_tree = unencode( request.GET.get('tree') )
    outputs = []

    for eq in eqs:
        eqtext = unencode(eq.name)
        tree = mathobjects.ParseTree(eqtext)

        #For debugging... maybe we want to add a tag to show this
        if debug_parse_tree:
            pretty_tree = mathobjects.pretty(tree)
            etree = tree.eval_args()
            print etree._sage_()

            tree = '<pre>%s</pre>' % pretty_tree
            outputs += tree
        else:
            etree = tree.eval_args()
            outputs.append(etree.get_html())

    if not eqs:
        raise Http404

    if debug_parse_tree:
        return HttpResponse(outputs)

    return render_to_response('worksheet.html', {'title': ws.name, 'equations':outputs})

transform_interface = '''
{% for option in options %}
    <button title="{{option.internal}}" onclick="javascript:apply_transform('{{option.internal}}')">{{option.prettytext}}</button>
{% endfor %}
'''

@login_required
@errors
def lookup_transform(request, eq_id):
    first_type = unencode( request.POST.get('first') )
    second_type = unencode( request.POST.get('second') )
    context = unencode( request.POST.get('context') )

    if not (first_type and second_type and context):
        return HttpResponse(json.dumps({'error': 'Insufficent lookup information'}))

    #Fix this with:
    #    if first_type in dir('mathobjects') 

    #TODO: This is ugly and dangerous
    if first_type != 'null':
        first_basetype = eval('mathobjects.' + first_type).base_type

    if second_type != 'null':
        second_basetype = eval('mathobjects.' + second_type).base_type


    #Create sets of the database queries
    lookup1 = set(MathematicalTransform.objects.filter(first=first_type,second=second_type,context=context))
    lookup2 = set(MathematicalTransform.objects.filter(first=first_basetype,second=second_basetype,context=context)) 
    lookup3 = set(MathematicalTransform.objects.filter(first=first_type,second=second_basetype,context=context))
    lookup4 = set(MathematicalTransform.objects.filter(first=first_basetype,second=second_type,context=context))

    #Take the union of the sets so as to avoid identical operations
    options = lookup1 | lookup2 | lookup3 | lookup4

    interface_ui = template.Template(transform_interface)

    c = template.Context({'options':options})
    return HttpResponse(interface_ui.render(c))

identity_interface = '''
{% for option in options %}
    <button onclick="javascript:apply_identity('{{option.internal}}')">{{option.prettytext}}</button>
{% endfor %}

{% for option in options2 %}
    <button onclick="javascript:apply_identity('{{option.internal}}')">{{option.prettytext}}</button>
{% endfor %}
'''

def lookup_identity(request, eq_id):
    first_type = unencode( request.POST.get('first') )
    options = MathematicalIdentity.objects.filter(first=first_type)

    #Fix this with:
    #    if first_type in dir('mathobjects') 

    #TODO: This is ugly and dangerous
    first_basetype = eval('mathobjects.' + first_type).base_type
    options2 = MathematicalIdentity.objects.filter(first=first_basetype)

    interface_ui = template.Template(identity_interface)
    c = template.Context({'options':options,'options2':options2})
    return HttpResponse(interface_ui.render(c))

term_html=template.Template('''<li id="{{term.id}}">
<span class="noselect">${{term.latex}}$</span>
</li>''')

@errors
def term(request,eq_id):
    id = request.POST.get('id')
    if id == 'plus':
        new = pf.spawn()
        return HttpResponse(new.get_html())
    elif id == 'times':
        new = mf.spawn()
        return HttpResponse(new.get_html())

#Try to combine existing terms based on rules
@errors
def combine(request,eq_id):
    first = unencode( request.POST.get('first') )
    second = unencode( request.POST.get('second') )
    context = unencode( request.POST.get('context') )

    first = mathobjects.ParseTree(first).eval_args()
    second = mathobjects.ParseTree(second).eval_args()

    combination = first.combine(second,context)

    #print mathobjects.pretty(first)
    #print mathobjects.pretty(second)

    return HttpResponse(combination)

@errors
def action(request,eq_id):
    type = unencode( request.POST.get('type') )
    math = unencode( request.POST.get('math') )
    obj = mathobjects.ParseTree(math).eval_args()

    result = obj.action()

    return HttpResponse(result)

@errors
def propogate(request,eq_id):
    type = unencode( request.POST.get('type') )
    math = unencode( request.POST.get('math') )
    obj = mathobjects.ParseTree(math).eval_args()

    result = obj.propogate()

    return HttpResponse(result)

@errors
def down(request,eq_id):
    '''This is normal used for subexpression-level factoring'''
    container = unencode( request.POST.get('container') )
    dragged = unencode( request.POST.get('dragged') )
    container_obj = mathobjects.ParseTree(container).eval_args()
    dragged_obj = mathobjects.ParseTree(dragged).eval_args()

    result = container_obj.down(dragged_obj)

    return HttpResponse(result)

@errors
def topdown(request,eq_id):
    '''This is normal used for equation-level division'''
    equation = unencode( request.POST.get('equation') )
    dragged = unencode( request.POST.get('dragged') )
    equation_obj = mathobjects.ParseTree(equation).eval_args()
    dragged_obj = mathobjects.ParseTree(dragged).eval_args()

    result = equation_obj.down(dragged_obj)

    return HttpResponse(result)

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

@errors
def apply_transform(request,eq_id):
    first = unencode( request.POST.get('first') )
    second = unencode( request.POST.get('second') )
    transform = unencode( request.POST.get('transform') )
    nested = unencode( request.POST.get('nested') )

    first = mathobjects.ParseTree(first).eval_args()
    second = mathobjects.ParseTree(second).eval_args()

    json = eval('mathobjects.'+transform)(first,second)

    return HttpResponse(json)

@errors
def apply_identity(request,eq_id):
    first = unencode( request.POST.get('first') )
    identity = unencode( request.POST.get('identity') )
    first = mathobjects.ParseTree(first).eval_args()

    json = eval('mathobjects.'+identity)(first)

    return HttpResponse(json)

@errors
def save_workspace(request,eq_id):
    try:
        workspace = Workspace.objects.get(id=eq_id)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({'error':'Workspace is missing'}))

    eqs = Equation.objects.filter(workspace=eq_id)

    #Delete old elements in the workspace
    data = {}
    for eq in eqs:
        eq.delete()

    #TODO this is crazy dangerous
    indexes = len(request.POST)

    for i in xrange(indexes):
        math = request.POST.get(str(i))
        Equation(name=math, workspace=workspace).save()

    return HttpResponse('cat')

@errors
def del_workspace(request):
    #TODO this is crazy dangerous
    for id,s in request.POST.iteritems():
        Equation.objects.filter(workspace=id).delete()
        Workspace.objects.get(id=id).delete()

@errors
def new_workspace(request):
    name = unencode( request.POST.get('name') )
    init = unencode( request.POST.get('init') )

    new_workspace = Workspace(name=name)
    new_workspace.save()
    new_id = new_workspace.id

    if init == 'Equation':
        RHS = mathobjects.RHS(mathobjects.Placeholder())
        LHS = mathobjects.LHS(mathobjects.Placeholder())
        equation = mathobjects.Equation(LHS,RHS).get_math()
    else:
        equation = mathobjects.Placeholder().get_math()

    init_eq = Equation(name=equation,workspace=new_workspace).save()
    return HttpResponse('Success')

'''
@errors
def applyfunc(request,eq_id):
    id = unencode( request.POST.getlist('id') )
    math = unencode( request.POST.getlist('math') )
    type = unencode( request.POST.getlist('type') )
    func = unencode( request.POST.getlist('func') )
    if not id or not func:
        return HttpResponse('Fail')

    if func=='negate':
        m = type_cast(math)
        m.negate()
        m.id = id
        return HttpResponse( m.get_html() )

    return HttpResponse('Fail')
'''

@errors
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

    inserted = mathobjects.ParseTree(obj).eval_args()

    received = mathobjects.ParseTree(receiver).eval_args()
    response = received.receive(inserted,receiver_context,sender_type,sender_context,new_position)

    if response is None:
        response = 'Could not find rewrite rule'

    return HttpResponse(response)

@errors
def remove(request,eq_id):
    obj = unencode( request.POST.get(u'obj') )
    obj_type = unencode( request.POST.get('obj_type') )

    sender = unencode( request.POST.get('sender') )
    sender_type = unencode( request.POST.get('sender_type') )
    sender_context = unencode( request.POST.get('sender_context') )

    obj = mathobjects.ParseTree(obj).eval_args()
    sender = mathobjects.ParseTree(sender).eval_args()
    response = sender.remove(obj,sender_context)

    if response is None:
        response = 'Could not find rewrite rule'

    return HttpResponse(response)

def continuous_rainbow(length):
    def cycle(iterable):
        while True:
            for item in iterable:
                yield item

    pastel_rainbow = ["#FFE3E3","#FFFEDB","#DBFFE1","#DBF1FF","#E6C5E2"]
    c=cycle(pastel_rainbow)

    return [c.next() for i in range(10)]

def unencode(s):
    if type(s) is list:
        s = s[0]
    elif s is None:
        return None
    fileencoding = "iso-8859-1"
    txt = s.decode(fileencoding)
    return str(txt)

def new_inline(request, eq_id):
    lhs = mathobjects.Placeholder()
    rhs = mathobjects.Placeholder()

    eq = mathobjects.Equation(mathobjects.LHS(lhs),mathobjects.RHS(rhs))
    return HttpResponse(json.dumps({'newline': eq.get_html()}))

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

    variables = {'name': 'Variables', 'type': 'array', 'objects': [
                    mathobjects.Variable('x').get_html(),
                    mathobjects.Variable('y').get_html(),
                    mathobjects.Variable('z').get_html(),
                ]}

    trig = {'name': 'Functions', 'type': 'tabular', 'objects': [
                    ('Sine', mathobjects.Sine(Placeholder()).get_html()),
                    ('Cosine', mathobjects.Cosine(Placeholder()).get_html()),
                    ('Tangent', mathobjects.Tangent(Placeholder()).get_html()),
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
                    ('Derivative', mathobjects.Diff(Placeholder(),mathobjects.Variable('x')).get_html()),
                ]}

    numbers = {'name': 'Numbers', 'type': 'array', 'objects': [
                    mathobjects.Numeric(x).get_html() for x in range(0,10)
                ]}

    physics = {'name': 'Physics', 'type': 'tabular', 'objects': [
                    ('Length', mathobjects.Length(Placeholder()).get_html()),
                ]}

    palette = [trig,variables,operations,numbers,physics,constants]

    interface_ui = template.Template(palette_template)
    c = template.Context({'palette':palette})

    return HttpResponse(interface_ui.render(c))
