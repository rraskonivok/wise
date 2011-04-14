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

from pprint import pformat

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseForbidden,
    HttpResponseRedirect)
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson as json
from django.views.generic import ListView, DetailView
from django.views.generic.edit import (UpdateView, DeleteView,
    CreateView)
from wise.translators.pytopure import parse_sexp
from wise.worksheet import models
from wise.worksheet.forms import WorksheetForm
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

    template_name = "worksheet_edit.html"
    success_url = '/home'

    def redirect_to(self, obj):
        return reverse('worksheet_detail', args=[obj.id])

class WorksheetCreate(CreateView):
    form_class = WorksheetForm
    model = models.Workspace
    template_name = "worksheet_edit.html"
    success_url = '/home'

    # We get to overload this method because the generic
    # CreateView needs to know about the owner field which we can
    # only get from the request object, see WorksheetForm for
    # more details
    def form_valid(self, form):
        self.object = form.save(owner=self.request.user)
        return HttpResponseRedirect(self.get_success_url())

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

class TextAtom(object):
    id = 0

    def __init__(self, text):
        self.text = text

    def get_html(self):

        template = """
<div id="cid%s-text">
<div class="textatom">%s</div>
</div>
        """

        return template % (self.id, self.text)

    def json_flat(self):
        resource_uri = ''

        return [{
            "id": self.id,
            "type": 'text',
            "toplevel": True,
            "args": self.text,
            "children": []
        }]

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
            if 'Text:' in eq.sexp:
                top_exprs.append(TextAtom(eq.sexp))
            else:
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

def ws_export(request, ws_id, format="wise"):
    CELL_INDICATOR = "-- CELL: %d --"
    ws = get_object_or_404(models.Workspace, pk=ws_id)

    if ( ws.owner.id != request.user.id ):
        return HttpResponseForbidden()

    cells = models.Cell.objects.filter(workspace=ws_id)

    output = ''

    newline = "\n"
    tripquote = lambda s: '"""%s"""' % s

    for cell in cells:
        eqs = models.Expression.objects.filter(cell=cell).order_by('index')
        output += CELL_INDICATOR % cell.index + newline

        for eq in eqs:
            if "Text:" in eq.sexp:
                output += tripquote(eq.sexp) + newline
            else:
                output += eq.sexp + newline


    if format == "wise":
        response = HttpResponse(output, mimetype="text/plain")
        response['Content-Disposition'] = 'attachment; filename=%s.wise' % ws.name
        return response

    elif format == "txt":
        response = HttpResponse(output, mimetype="text/plain")
        return response

    else:
        HttpResponse("Unknown export format")

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
            if 'Text:' in eq.sexp:
                top_exprs.append(TextAtom(eq.sexp))
            else:
                # Build up the object from the sexp in the database
                etree = parse_sexp(eq.sexp)
                etree.uid_walk(uid)

                etree.sid = eq.id
                etree.annotation = eq.annotation
                top_exprs.append(etree)

        # Initialize the new Cell instance
        ncell = basecell.Cell(top_exprs, [],
           index = index,
           id = cell.id,
           sid = cell.id
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

@login_required
def translate(request):
    return render_to_response('translate.html')


def objectgraph(request, package='base'):
    from worksheet.viz import package_to_graph

    try:
        graph = package_to_graph(package)
    except ImportError:
        return HttpResponse('Invalid class.')

    graph.layout(prog='fdp')
    png=graph.draw(format='png')
    return HttpResponse(png, mimetype='image/png')

@memoize
def _fetch_data(data):

    if data == 'python':
        pretty = pformat(get_python_lookup().table._fwd)
    elif data == 'pure':
        from wise.translators.mathobjects import get_pure_lookup
        pretty = pformat(get_pure_lookup().table._fwd)
    elif data == 'purelist':
        from wise.translators.mathobjects import get_pure_lookup
        pretty = json.dumps(get_pure_lookup().table.keys())
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

    return pretty

@login_required
def internal_dict(request, data='pure'):
    """
    Dump the translation dictionary to a JSON object, for
    debugging purposes
    """

    if not settings.DEBUG:
        return HttpResponseForbidden()

    pretty = _fetch_data(data)

    return HttpResponse(pretty, mimetype="text/plain")

#vim: ai ts=4 sts=4 et sw=4
