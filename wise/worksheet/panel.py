from django.conf import settings
from django.utils import importlib
import wise.worksheet.exceptions as exception

from wise.worksheet.utils import haml
from types import ClassType, InstanceType
from inspect import getargspec
from django.template import Template, Context

ROOT_MODULE = 'wise.worksheet'
packages = {}
panels = {}

class Panel:
    def get_html(self):
        interface_ui = self.template
        objects = [obj.get_html() for obj in self.objects]
        c = Context({'name':self.name, 'objects': objects})
        return interface_ui.render(c)

tablular_template = haml('''
<table class="palette">
    {% for name, html in objects %}
        <tr>
            <td>{{ name }}</td>
            <td>{{ html }}</td>
        </tr>
    {% endfor %}
</table>
''')

array_template = haml('''
{% for html in objects %}
    {{ html }}
{% endfor %}
''')

class TabularPanel(Panel):
    template = Template(tablular_template)

    def __init__(self, name, objects):
        self.name = name
        self.objects = objects


class ArrayPanel(Panel):
    template = Template(array_template)

    def __init__(self, name, objects):
        self.name = name
        self.objects = objects

def is_panel(obj):
    return isinstance(obj,Panel)

for pack in settings.INSTALLED_MATH_PACKAGES:
    try:
        path = '.'.join([ROOT_MODULE,pack,'panel'])
        packages[pack] = importlib.import_module(path)
        for name, symbol in packages[pack].__dict__.iteritems():
            if is_panel(symbol):
                if settings.DEBUG:
                    print "Importing panel ... %s/%s" % (pack, name)

                panels[name] = symbol
    except ImportError:
        raise exception.IncompletePackage(pack,'panel.py')

print panels
