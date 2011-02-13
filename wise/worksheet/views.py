# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import panel
import wise.boot
import wise.meta_inspector

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson as json
from django.views.generic import ListView, DetailView
from django.views.generic.edit import (UpdateView, DeleteView,
CreateView)
from wise.translators.pytopure import parse_sexp
from wise.worksheet.forms import WorksheetForm
from wise.worksheet import models
from wise.worksheet.utils import *
from wise.packages import loader

from operator import itemgetter

# Initialize the Python-Pure translation bridge
if settings.WORKER_TYPE == 'sync':
    wise.boot.start_cython()

wise.boot.start_python_pure()
panel.build_panels()

basecell = loader.load_package_module('base','cell')

#---------------------------
# Home Page
#---------------------------

class HomeView(ListView):
    model = models.Workspace
    template_name = "home.html"
    context_object_name = 'workspaces'

    def get_queryset(self):
        return models.Workspace.objects.filter(owner=self.request.user)

#---------------------------
# Worksheet CRUD
#---------------------------

class WorksheetDetail(DetailView):
    queryset = models.Workspace.objects.all()
    template_name = "worksheet_edit.html"

class WorksheetDelete(DeleteView):
    queryset = models.Workspace.objects.all()
    template_name = "worksheet_delete.html"
    success_url = '/home'

class WorksheetEdit(UpdateView):
    model = models.Workspace
    queryset = models.Workspace.objects.all()

    form = WorksheetForm
    template_name = "worksheet_edit.html"
    success_url = '/home'

    def redirect_to(self, obj):
        return reverse('worksheet_detail', args=[obj.id])

class WorksheetCreate(CreateView):
    model = models.Workspace
    form = WorksheetForm
    template_name = "worksheet_edit.html"
    success_url = '/home'

    def redirect_to(self, obj):
        return reverse('authors_list')

def new_worksheet_prototype(attrs):
    nworksheet = models.Workspace(**attrs).save()
    models.Cell(workspace=ws, index=0).save()
    return nworksheet

#---------------------------
# Ecosystem
#---------------------------

@login_required
def ecosystem(request):
    # Wrap up the packages into 'pack' objects so aren't passing
    # pointers to our disk persistence to the template
    context = RequestContext(request)
    context['workspaces'] = models.Workspace.objects.filter(owner=request.user)

    packages = []

    for name, pack in wise.meta_inspector.PACKAGES.iteritems():
        pack.symbols = []
        packages.append(pack)

        if pack.provided_symbols:
            for symbol in pack.provided_symbols:
                pack.symbols.append(symbol)

    return render_to_response('ecosystem.html',
                              {'packages': packages},
                              context_instance=RequestContext(request))

#---------------------------
# Worksheet
#---------------------------

@login_required
def ws_read(request, ws_id):
    ws = get_object_or_404(models.Workspace, pk=ws_id)

    if ( ws.owner.id != request.user.id ) and not ws.public:
        return HttpResponseForbidden()

    cells = models.Cell.objects.filter(workspace=ws_id)

    if not cells:
        cells = []

    # HTML elements to inject into the #workspace div
    html_cells = []

    uid = uidgen()
    # Populate the Cell
    for index,cell in enumerate(cells):
        # Load toplevel expressions
        eqs = models.Expression.objects.filter(cell=cell).order_by('index')
        top_exprs = []

        #asms = Assumption.objects.filter(cell=cell).order_by('index')
        #top_asms = []

        for eq in eqs:
            # Build up the object from the sexp in the database
            etree = parse_sexp(eq.sexp)
            etree.annotation = eq.annotation
            etree.uid_walk(uid)
            top_exprs.append(etree)

        # Initialize the new Cell instance
        ncell = basecell.Cell(top_exprs, [],
           index = index,
           cid = 'cell'+str(index),
           id = cell.id
        )

        html_cells.append(html(ncell))

    response = render_to_response('worksheet_read.html', {
        'title': ws.name,
        'author': ws.owner,
        'cells': html_cells,
        },
        context_instance = RequestContext(request),
    )

    return response

#TODO: change the name of this to something more illuminating
# i.e. WorksheetView
@login_required
def ws(request, ws_id):
    ws = get_object_or_404(models.Workspace, pk=ws_id)

    if ( ws.owner.id != request.user.id ):
        return HttpResponseForbidden()

    # Start a uid generator at cid0
    uid = uidgen()
    cells = models.Cell.objects.filter(workspace=ws_id)

    # If the worksheet is empty give it an empty cell
    if not cells:
        ncell = models.Cell(workspace=ws, index=0)
        ncell.save()

        cells = []
        cells.append(ncell)

    # HTML elements to inject into the #workspace div
    html_cells = []

    # inline javascript global variable `JSON_TREE`
    json_cells = []

    # Populate the Cell
    for index,cell in enumerate(cells):
        # Load toplevel expressions
        eqs = models.Expression.objects.filter(cell=cell).order_by('index')
        top_exprs = []

        #asms = Assumption.objects.filter(cell=cell).order_by('index')
        #top_asms = []

        for eq in eqs:
            # Build up the object from the sexp in the database
            etree = parse_sexp(eq.sexp)
            etree.uid_walk(uid)

            etree.sid = eq.id
            etree.annotation = eq.annotation
            top_exprs.append(etree)

        #for asm in asms:
        #    # Build up the object from the sexp in the database
        #    etree = parse_sexp(asm.sexp)
        #    etree.uid_walk(uid)

        #    etree.sid = asm.id
        #    etree.annotation = asm.annotation
        #    top_asms.append(etree)

        # Initialize the new Cell instance
        ncell = basecell.Cell(top_exprs, [],
           index = index,
           cid = 'cell'+str(index),
           id = cell.id
        )

        html_cells.append(html(ncell))
        json_cells.append(json_flat(ncell))

    response = render_to_response('worksheet.html', {
        'title': ws.name,
        'ws_id': ws.id,
        'cells': html_cells,
        'namespace_index': uid.next()[3:],
        'cell_index': len(cells),
        'json_cells': json.dumps(json_cells),
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
# Palettes
#---------------------------

@login_required
def palette(request):
    response = generate_palette()
    response.content = minimize_html(response.content)
    response.xhtml = True
    return response

def generate_palette():
    # Sort panels alphabetically
    panels = sorted(panel.panels.iteritems(), key=itemgetter(0))

    render_panels = []

    for name, pnl in panels:
        pnl.html = pnl.get_html()
        render_panels.append(pnl)

    return render_haml_to_response('palette_template.tpl',
        {
            'panels': render_panels
        }
    )

#---------------------------
# Development Tools
#---------------------------

def objectgraph(request, package='base'):
    from worksheet.viz import package_to_graph

    try:
        graph = package_to_graph(package)
    except ImportError:
        return HttpResponse('Invalid class.')

    graph.layout(prog='fdp')
    png=graph.draw(format='png')
    return HttpResponse(png, mimetype='image/png')

@login_required
def translate(request):
    return render_to_response('translate.html')

@login_required
def dict(request, data='pure'):
    """
    Dump the translation dictionary to a JSON object, for
    debugging purposes
    """

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
