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

from wise.utils import shpaml

#-------------------------------------------------------------
# Decorators
#-------------------------------------------------------------

def errors(f):
    '''Decorator to wrap errors out to server log and javascript popup'''
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
            raise e
    return wrapper

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

def memoize(f):
    f.cache = {}
    return decorator(_memoize, f)

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

#-------------------------------------------------------------
# HTTP/JSON Responses
#-------------------------------------------------------------

class JsonResponse(HttpResponse):
    ''' HttpResponse descendant, which return response with ``application/json`` mimetype.  '''
    def __init__(self, data):
        super(JsonResponse, self).__init__(content=json.dumps(data), mimetype='application/json')

@errors
def render_haml_to_response(tname, context):
    tps, tpo = loader.find_template_source(tname)
    tpl = template.Template(haml(tps))
    return HttpResponse(tpl.render(template.Context(context)))

def json_flat(obj):
    '''Prefix convenience wrapper for arg.json_flat()'''
    if not obj:
        return None
    return obj.json_flat()

def unencode(s):
    '''Convert unicode to iso-8859-1'''
    if type(s) is list:
        s = s[0]
    elif s is None:
        return None
    fileencoding = "iso-8859-1"
    txt = s.decode(fileencoding)
    return str(txt)


def maps(func, obj):
    ''' Idempotent form of map, which behaves like you would
    expect in most functional languages:

    maps f nil = nil
    maps f x = [f x]
    maps f [x,y,...] = [f x, f y, ...]

    maps(f,None) = None
    maps(f,x) = [f(x)]
    maps(f,[x,y,z]) = [f(x),f(y),f(z)]

    '''

    if obj is None:
        return None
    elif hasattr(obj,'__iter__'):
        return map(func, obj)
    else:
        return [func(obj)]

def parse(code, uid):
    parsed = mathobjects.ParseTree(code)
    parsed.gen_uids(uid)
    evaled = parsed.eval_args()
    return evaled


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
# Sexp Generation
#-------------------------------------------------------------

def sexp(*strs):
    '''Build a sexp string from string aruments ( str1 str2 str2 ... ) '''
    return cats(*(['(']+list(strs)+[')']))

def msexp(head,args):
    '''Build a sexp from Python objects'''
    return sexp(head.classname, *map(math,args))

#-------------------------------------------------------------
# HTML Generation
#-------------------------------------------------------------

def math(obj):
    '''Prefix convenience wrapper for arg.get_math()'''
    return obj.get_math()

def cat(*strs):
    '''Fast string concatentation'''
    return ''.join(strs)

def cats(*strs):
    '''Fast string concatentation with space as delimeter'''
    return ' '.join(strs)

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

def purify(obj):
    '''Prefix form of obj.get_html(), returns a Pure object.'''
    if hasattr(obj,'__iter__'):
        return map(purify,obj)
    else:
        return obj._pure_()

@memoize
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

#-------------------------------------------------------------
# Type Checking
#-------------------------------------------------------------

def is_number(s):
    ''' Return true if the given string argument can be cast into
    a numeric type'''
    try:
        float(s)
    except ValueError:
        return False
    return True
