# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from wise.translators.pytopure import parse_sexp

from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponse, HttpResponseRedirect, \
HttpResponseForbidden

from django.shortcuts import redirect
from django.shortcuts import render_to_response, get_object_or_404

from django.template import RequestContext

from django.core.urlresolvers import reverse
from django.utils import simplejson as json

from django.contrib.auth.decorators import login_required

from django.views.decorators.cache import cache_page

import panel

from wise.worksheet.utils import *
from wise.worksheet.forms import WorksheetForm
from wise.worksheet.models import Workspace, Expression, Cell, \
Assumption

from wise.base.cell import Cell as PyCell

from wise.meta_inspector import PACKAGES

CACHE_INTERVAL = 30*60 # 5 Minutes

from wise.boot import start_python_pure

# Initialize the Python <-> Pure translation bridge
start_python_pure()

#---------------------------
# Worksheet CRUD
#---------------------------

def new_worksheet_prototype(attrs):
    ws = Workspace(**attrs)
    ws.save()

    Cell(workspace=ws, index=0).save()

    return ws


def worksheet_delete(request, ws_id):
    ws = get_object_or_404(Workspace,pk=ws_id)

    if ( ws.owner.id != request.user.id ):
        return HttpResponseForbidden('You do not have permission to access \
                this worksheet.')

    ws.delete()
    return HttpResponseRedirect('/')

@login_required
def worksheet_edit(request, ws_id = None,
        form_class=WorksheetForm,
        template_name='worksheet_edit.html',
        extra_context=None,
        ):

    if request.POST:
        form = form_class(request.POST or None)

        if form.is_valid():
            worksheet = form.save(commit=False)
            worksheet.owner = request.user
            worksheet.save()
            return HttpResponseRedirect('/')

    elif ws_id:
        ws = get_object_or_404(Workspace,pk=ws_id)
        form = form_class(instance=ws)

        context = {'form': form}

        if extra_context is not None:
            context.update(extra_context)

        return render_to_response(template_name, context,
            context_instance=RequestContext(request))

    #errors = []
    #id = None

    ## -- Update --
    #if ws_id:
    #    action = 'Update'

    #    ws = get_object_or_404(Workspace,pk=ws_id)

    #    if ( ws.owner.id != request.user.id ):
    #        return HttpResponse('You do not have permission to access this\
    #                worksheet.')

    #    # -- Receiveing post data from form --
    #    if request.method == 'POST':
    #        form = WorksheetForm(request.POST)

    #        if not request.POST.get('name', ''):
    #            errors.append('Worksheet name is invalid')

    #        ws.name = request.POST.get('name')
    #        ws.public = not request.POST.get('public')

    #        ws.save();

    #        if not errors and form.is_valid():
    #            return HttpResponseRedirect('/')

    #    # -- Render form --
    #    else:
    #        id = ws.id

    #        form = WorksheetForm({
    #            'name': ws.name,
    #            'public': ws.public,
    #        })

    ## -- Create --
    #else:
    #    action = 'Create'

    #    # -- Receiveing post data from form --
    #    if request.method == 'POST':
    #        form = WorksheetForm(request.POST)

    #        if not request.POST.get('name', ''):
    #            errors.append('Worksheet name is invalid')

    #        if not errors and form.is_valid():

    #            ws = new_worksheet_prototype({
    #                'name'   : request.POST.get('name'),
    #                'public' : not request.POST.get('public'),
    #            })

    #            return HttpResponseRedirect('/ws/%i' % ws.id)

    #    # -- Render form --
    #    else:
    #        form = WorksheetForm()

    #return render_to_response('worksheet_edit.html',
    #                          {
    #                            'form': form,
    #                            'errors': errors,
    #                            'action': action,
    #                            'id': id,
    #                          },
    #                          context_instance=RequestContext(request))

def account_logout(request):
    logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect('/accounts/login')

@login_required
def home(request):
    workspaces = Workspace.objects.filter(owner=request.user)

    return render_to_response('home.html',
                              {'workspaces': workspaces},
                              context_instance=RequestContext(request))

from django.views.generic import ListView
from django.views.generic.edit import UpdateView
from django.views.generic import DetailView

class HomeView(ListView):
    model = Workspace
    template_name = "home.html"
    context_object_name = 'workspaces'

    def get_queryset(self):
        return Workspace.objects.filter(owner=self.request.user)

class WorksheetDetail(DetailView):
    queryset = Workspace.objects.all()
    template_name = "worksheet_edit.html"

class WorksheetEdit(UpdateView):
    model = Workspace
    queryset = Workspace.objects.all()

    form = WorksheetForm
    template_name = "worksheet_edit.html"
    success_url = '/home'

    def redirect_to(self, obj):
        return reverse('worksheet_detail', args=[obj.id])

@login_required
def ecosystem(request):

    context = RequestContext(request)
    context['workspaces'] = Workspace.objects.filter(owner=request.user)

    packages = []

    for name, pack in PACKAGES.iteritems():
        pack.symbols = []
        packages.append(pack)

        for symbol in pack.provided_symbols.itervalues():
            symbol_desc = {}
            symbol_desc['description'] = symbol.__doc__
            symbol_desc['name'] = symbol.__name__
            pack.symbols.append(symbol_desc)

    return render_to_response('ecosystem.html',
                              {'packages': packages},
                              context_instance=RequestContext(request))

@login_required
def translate(request):
    return render_to_response('translate.html')

@login_required
def ws(request, ws_id):

    ws = get_object_or_404(Workspace, pk=ws_id)

    if ( ws.owner.id != request.user.id ) and not ws.public:
        return HttpResponse('You do not have permission to access this worksheet.')

    cells = Cell.objects.filter(workspace=ws_id)

    uid = uidgen()

    html_cells = []
    py_cells = []

    # Process Cells
    # -------------
    for index,cell in enumerate(cells):
        html_eq = []

        # Process Cell Contents
        # ---------------------
        eqs = Expression.objects.filter(cell=cell).order_by('index')
        asms = Assumption.objects.filter(cell=cell).order_by('index')
        top_nodes = []
        top_asms = []

        for eq in eqs:
            # Build up the object from the sexp in the database
            etree = parse_sexp(eq.sexp)
            etree.uid_walk(uid)

            etree.sid = eq.id
            etree.annotation = eq.annotation
            top_nodes.append(etree)

        for asm in asms:
            # Build up the object from the sexp in the database
            etree = parse_sexp(asm.sexp)
            etree.uid_walk(uid)

            etree.sid = asm.id
            etree.annotation = asm.annotation
            top_asms.append(etree)

        # Build the cell and link it to the top nodes of the
        # expressions inside it.
        db_id = cell.id

        #TODO: overloads cell from in loop ^^^
        cell = PyCell(top_nodes, top_asms)
        cell.index = index;
        cell.cid = 'cell' + str(index)

        # Initialize the Cell
        cell.id = db_id
        py_cells.append(cell)

        json_cells = [json_flat(cell) for cell in py_cells]

    response = render_to_response('worksheet.html', {

        'title': ws.name,
        'ws_id': ws.id,

        'cells': [html(cell) for cell in py_cells],

        'namespace_index': uid.next()[3:],
        'cell_index': len(cells),

        'json_cells': json.dumps(json_cells,ensure_ascii=False),

        'xhtml': True,
        },
        context_instance = RequestContext(request),
    )

    # XHTMLMiddleware will look for this attribute and set
    # Content-Type to application/xhtml+xml which is needed by
    # some browsers (i.e. Firefox 3.5) to render MathML
    response.xhtml = True

    return response

#---------------------------
# Palette
#---------------------------

@login_required
def palette(request):
    response = generate_palette()
    response.content = minimize_html(response.content)
    response.xhtml = True
    return response

def generate_palette():
    render_panels = []

    for pnl in panel.panels.itervalues():
        pnl.html = pnl.get_html()
        render_panels.append(pnl)

    return render_haml_to_response('palette_template.tpl',{'panels': render_panels})

# Debugging Stuff

@login_required
def log(request):
    log = open('session.log').read()
    log_html = log.replace("\n","<br />\n")

    return render_to_response('log.html', {'log': log_html})

@login_required
def dict(request, data='pure'):
    ''' Dump the translation dictionary to a JSON object, for
    debugging purposes '''

    from pprint import pformat

    #if not settings.DEBUG:
    #    pretty = 'Only enabled in DEBUG'

    if data == 'python':
        from wise.translators.mathobjects import get_python_lookup
        pretty = pformat(get_python_lookup().table._fwd)
    elif data == 'pure':
        from wise.translators.mathobjects import get_pure_lookup
        pretty = pformat(get_pure_lookup().table._fwd)
    else:
        pretty = "unknown output " + data

    return HttpResponse(pretty, mimetype="text/plain")

# End Debugging Stuff

#vim: ai ts=4 sts=4 et sw=4

