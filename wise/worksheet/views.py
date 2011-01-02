# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import simplejson as json
from django.views.decorators.cache import cache_page
from django.http import (HttpResponse, HttpResponseRedirect,
HttpResponseForbidden)

from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView

import wise.base
import wise.boot

from wise.worksheet.utils import *
from wise.worksheet.forms import WorksheetForm
from wise.worksheet.models import (Workspace, Expression, Cell,
Assumption)
import wise.worksheet.panel

from wise.meta_inspector import PACKAGES
from wise.translators.pytopure import parse_sexp

# Initialize the Python-Pure translation bridge
wise.boot.start_python_pure()

#---------------------------
# Home Page
#---------------------------

class HomeView(ListView):
    model = Workspace
    template_name = "home.html"
    context_object_name = 'workspaces'

    def get_queryset(self):
        return Workspace.objects.filter(owner=self.request.user)

#---------------------------
# Worksheet CRUD
#---------------------------

class WorksheetDetail(DetailView):
    queryset = Workspace.objects.all()
    template_name = "worksheet_edit.html"

class WorksheetDelete(DeleteView):
    queryset = Workspace.objects.all()
    template_name = "worksheet_delete.html"
    success_url = '/home'

class WorksheetEdit(UpdateView):
    model = Workspace
    queryset = Workspace.objects.all()

    form = WorksheetForm
    template_name = "worksheet_edit.html"
    success_url = '/home'

    def redirect_to(self, obj):
        return reverse('worksheet_detail', args=[obj.id])

def new_worksheet_prototype(attrs):
    nworksheet = Workspace(**attrs).save()
    Cell(workspace=ws, index=0).save()
    return nworksheet

#---------------------------
# Ecosystem
#---------------------------

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

#---------------------------
# Worksheet
#---------------------------

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
    for index,cell in enumerate(cells):
        html_eq = []

        # Process Cell Contents
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
        cell = wise.base.cell.Cell(top_nodes, top_asms)
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
    panels = wise.worksheet.panel.panels

    for pnl in panels.itervalues():
        pnl.html = pnl.get_html()
        render_panels.append(pnl)

    return render_haml_to_response('palette_template.tpl',{'panels': render_panels})

#---------------------------
# Development Tools
#---------------------------

@login_required
def translate(request):
    return render_to_response('translate.html')

@login_required
def dict(request, data='pure'):
    ''' Dump the translation dictionary to a JSON object, for
    debugging purposes '''

    from pprint import pformat

    if not settings.DEBUG:
        return HttpResponseForbidden()

    if data == 'python':
        from wise.translators.mathobjects import get_python_lookup
        pretty = pformat(get_python_lookup().table._fwd)
    elif data == 'pure':
        from wise.translators.mathobjects import get_pure_lookup
        pretty = pformat(get_pure_lookup().table._fwd)
    elif data == 'rules':
        from wise.translators.mathobjects import rules
        pretty = pformat(rules)
    elif data == 'rulesets':
        from wise.translators.mathobjects import rulesets
        pretty = pformat(rulesets.as_dict())
    elif data == 'cython':
        from wise.translators.mathobjects import cy_objects
        pretty = pformat(cy_objects)
    else:
        pretty = "unknown output " + data

    return HttpResponse(pretty, mimetype="text/plain")

#vim: ai ts=4 sts=4 et sw=4
