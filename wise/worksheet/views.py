# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import traceback
from transforms import get_transform_by_path

import wise.translators.mathobjects as mathobjects
import wise.translators.pure_wrap as pure_wrap
from wise.translators.pytopure import parse_sexp

import panel

from logger import debug, getlogger

from django.template import Template, Context
from django.conf import settings
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.utils import simplejson as json
from django.utils.html import strip_spaces_between_tags as strip_whitespace
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.cache import cache_page
from django.contrib.auth.models import User

from wise.worksheet.utils import *
from wise.worksheet.forms import LoginForm
from wise.worksheet.models import Workspace, Expression, Cell, \
Assumption
from wise.base.cell import Cell as PyCell

CACHE_INTERVAL = 30*60 # 5 Minutes

def account_login(request):
    form = AuthenticationForm()

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if 'next' in request.GET:
            redirect = request.GET['next']
        else:
            redirect = '/'

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
    return HttpResponseRedirect('/accounts/login')

@login_required
def home(request):
    workspaces = Workspace.objects.filter(owner=request.user)
    return render_to_response('home.html', {'workspaces': workspaces})

@login_required
def ecosystem(request):
    workspaces = Workspace.objects.filter(owner=request.user)
    return render_to_response('ecosystem.html')

@login_required
def users(request):
    return render_to_response('users.html',{'users':User.objects.all()})

# Debugging Stuff

@login_required
def log(request):
    log = open('session.log').read()
    log_html = log.replace("\n","<br />\n")

    return render_to_response('log.html', {'log': log_html})

@login_required
@errors
def dict(request):
    ''' Dump the translation dictionary to a JSON object, for
    debugging purposes '''
    return HttpResponse(str(pure_wrap.objects))
    #return JsonResponse(pure_wrap.objects)

# End Debugging Stuff

@login_required
def translate(request):
    return render_to_response('translate.html')

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

    uid = uidgen()

    json_cells = []
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
            etree = parse_sexp(eq.sexp, uid)
            etree.sid = eq.id
            etree.annotation = eq.annotation
            top_nodes.append(etree)

        for asm in asms:
            # Build up the object from the sexp in the database
            etree = parse_sexp(asm.sexp, uid)
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
        json_cells.append(cell)

    return render_to_response('worksheet.html', {
        'title': ws.name,
        'ws_id': ws.id,
        'cells': [html(cell) for cell in py_cells],
        'username': request.user.username,
        'namespace_index': uid.next()[3:],
        'cell_index': len(cells),
        'json_cells': json.dumps([json_flat(cell) for cell in py_cells]),
        })

#---------------------------
# Palette ------------------
#---------------------------

#@cache_page(CACHE_INTERVAL)
def palette(request):
    return generate_palette()

@errors
def generate_palette():
    render_panels = []

    for pnl in panel.panels.itervalues():
        pnl.html = pnl.get_html()
        render_panels.append(pnl)

    return render_haml_to_response('palette_template.tpl',{'panels': render_panels})

#vim: ai ts=4 sts=4 et sw=4
