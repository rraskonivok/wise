import traceback
from decorator import decorator

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.html import strip_spaces_between_tags as strip_whitespace
from django.utils import simplejson as json
from django.contrib.auth.decorators import login_required
from worksheet.shpaml import convert_text

# Wraps errors out to server log and javascript popup
def errors(f):
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
            response = {'error': {'type': 405,
                                  'message': 'Accepts only POST request'}}
        if isinstance(response, dict):
            resp = JsonResponse(response)
            if 'error' in response:
                resp.status_code = response['error'].get('type', 500)
            return resp
        return response
    wrapper.__name__ = func.__name__
    wrapper.__module__ = func.__module__
    wrapper.__doc__ = func.__doc__
    return wrapper

class JsonResponse(HttpResponse):
    ''' HttpResponse descendant, which return response with ``application/json`` mimetype.  '''
    def __init__(self, data):
        super(JsonResponse, self).__init__(content=json.dumps(data), mimetype='application/json')

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

#-------------------------------------------------------------
# HTML Generation
#-------------------------------------------------------------

def haml(code):
    return convert_text(code)

def minimize_html(html):
    if not html:
        return None
    return strip_whitespace(html.rstrip('\n'))

def html(obj):
    if not obj:
        return None
    return minimize_html(obj.get_html())

def uidgen(i=0):
    while True:
        yield 'uid%i' % i
        i += 1

def cellify(s,index):
    return '<div class="cell" data-index="%s"><table class="lines" style="display: none">%s</table></div>' % (index, s)

def spaceiter(list):
    '''iterate over a list returning a space separated string'''
    return ' '.join(list)
