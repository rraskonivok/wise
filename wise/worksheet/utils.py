# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os.path
import traceback
from decorator import decorator
from logger import debug, getlogger
from operator import xor
from binascii import crc32

from django import template
from django.template import loader
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.html import strip_spaces_between_tags as strip_whitespace
from django.utils import simplejson as json
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

import worksheet.shpaml

def errors(f):
    '''Wraps errors out to server log and javascript popup'''
    def wrapper(*args,**kwargs):
        try:
            return f(*args,**kwargs)
        except Exception,e:
            print e
            print traceback.print_exc()

            if settings.DEBUG:
                return HttpResponse(json.dumps({'error': str(e)}))
            else:
                return HttpResponse(json.dumps({'error': 'A server-side error occured'}))
    return wrapper

def fallback(fallback):
    '''Try to run f, if f returns None or False then run fallback'''
    def options(f):
        def wrapper(self,*args,**kwargs):
            if f(self,*args,**kwargs) is None:
                return fallback(self,*args,**kwargs)
            else:
                return f(self,*args,**kwargs)
        return wrapper
    return options

# From django-sugar project
def ajax_request(func):
    '''
    Checks request.method is POST. Return error in JSON in other case.

    If view returned dict, returns JsonResponse with this dict as content.
    '''
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            response = func(request, *args, **kwargs)
        else:
            response = {'error': 'Accepts only POST request'}
        if isinstance(response, dict):
            return JsonResponse(response)
        return response
    wrapper.__name__ = func.__name__
    wrapper.__module__ = func.__module__
    wrapper.__doc__ = func.__doc__
    return wrapper

class JsonResponse(HttpResponse):
    ''' HttpResponse descendant, which return response with ``application/json`` mimetype.  '''
    def __init__(self, data):
        super(JsonResponse, self).__init__(content=json.dumps(data), mimetype='application/json')


@errors
def render_haml_to_response(tname, context):
    tps, tpo = loader.find_template_source(tname)
    tpl = template.Template(haml(tps))
    return HttpResponse(tpl.render(template.Context(context)))

def unencode(s):
    '''Convert unicode to iso-8859-1'''
    if type(s) is list:
        s = s[0]
    elif s is None:
        return None
    fileencoding = "iso-8859-1"
    txt = s.decode(fileencoding)
    return str(txt)


def json_flat(obj):
    if not obj:
        return None
    return obj.json_flat()

def maps(func, obj):
    '''It's like map() but awesomer, namely in that you can pass
    a single argument to it and it doesn't crash and burn'''

    if hasattr(obj,'__iter__'):
        return map(func, obj)
    return [func(obj)]

def parse(code, uid):
    parsed = mathobjects.ParseTree(code)
    parsed.gen_uids(uid)
    evaled = parsed.eval_args()
    return evaled

def is_number(s):
    try:
        float(s)
    except ValueError:
        return False
    return True

#-------------------------------------------------------------
# Client ID Generator
#-------------------------------------------------------------

def uidgen(i=0):
    '''Auto incrementing generator which returns a string
    cid1, cid2. Used by Backbone.js to keep track of elements on
    the clientside worksheet.'''

    while True:
        yield 'cid%i' % i
        i += 1

#-------------------------------------------------------------
# HTML Generation
#-------------------------------------------------------------

def cat(*strs):
    '''Quick string concatentation'''
    return ''.join(strs)

def haml(code):
    '''Render Haml to an HTML string'''
    return shpaml.convert_text(code)

def minimize_html(html):
    '''Remove whitespace between html tags and remove all
    newlines'''
    if not html:
        return None
    return strip_whitespace(html.rstrip('\n'))

def html(obj):
    '''Prefix form of obj.get_html(), returns a string.'''
    if not obj:
        return None
    return minimize_html(obj.get_html())


def cellify(s,index):
    return '<div class="cell" data-index="%s"><table class="lines" style="display: none">%s</table></div>' % (index, s)

def spaceiter(list):
    '''iterate over a list returning a space separated string'''
    return ' '.join(list)

def purify(obj):
    '''Prefix form of obj.get_html(), returns a Pure object.'''
    if hasattr(obj,'__iter__'):
        return map(purify,obj)
    else:
        return obj._pure_()

def load_haml_template(fname):
    '''Returns a haml template specified by filename from the
    locations specified in TEMPLATE_DIRS '''
    if settings.IGNORE_PATHS:
        return False
    else:
        tps, tpo = loader.find_template_source(fname)
        return template.Template(haml(tps))

#-------------------------------------------------------------
# Hashing
#-------------------------------------------------------------

def hasharray(lst):
    '''Return a hash of a list, not guaranteed to be collision
    free, but good enough for most purposes'''
    return hash(reduce(xor, lst))

def hashdict(lst):
    '''Return a hash of a dict, not guaranteed to be collision
    free, but good enough for most purposes'''
    return hash(reduce(xor, lst))

class crcdigest(object):
    '''Wrapper to make crcdigest behave like hashlib functions'''
    def __init__(self):
        #crc32(0) = 0
        self.hash = 0

    def update(self,text):
        self.hash = crc32(text,self.hash)

    def hexdigest(self):
        return hex(self.hash)

def is_number(s):
    ''' Return true if the given string argument can be cast into
    a numeric type'''
    try:
        float(s)
    except ValueError:
        return False
    return True
