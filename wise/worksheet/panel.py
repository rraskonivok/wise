from inspect import getargspec
from types import TypeType

from django.conf import settings
from django.template import Template, Context
from django.utils import importlib
from wise.base.objects import Placeholder
import wise.worksheet.exceptions as exception

ROOT_MODULE = 'wise'
packages = {}
panels = {}

def _map_panel_types(obj):
    if isinstance(obj, TypeType):
        # Get the number of arguments the __init__ function for
        # the mathobject takes and substitute placeholder in for
        # each argument
        args, varargs, keywords, defaults = getargspec(obj.__init__)
        try:
            # decrement the len(args) since we ignore the self
            # argument
            ph = Placeholder
            placeholder_tuples = (ph(),)*(len(args) - 1)
            return obj(*placeholder_tuples)
        except TypeError:
            print 'Type Error',args
    else:
        # If an instance is passed do nothing and just pass it
        # along
        return obj

class Panel:
    package = None

    def get_html(self):
        interface_ui = self.template
        objects = [obj.get_html() for obj in self.objects]
        c = Context({'name':self.name, 'objects': objects})
        return interface_ui.render(c)

mathml_template = '''
<table>
<tr>
{% for button in buttons %}
  <td>
  <span class="uniform_button" onclick="subs('{{ button.math }}');">
  {{ button.mathml|safe }}
  </span>
  </td>
  {% if forloop.counter|divisibleby:"5" %}
    </tr><tr>
  {% endif %}
{% endfor %}
</tr>
</table>
'''

class MathMLPanel(Panel):
    template = Template(mathml_template)

    def __init__(self, name, objects, use_template=False):
        self.name = name
        self.objects = objects
        self.use_template = use_template

    def get_html(self):
        buttons = []

        if self.use_template:
            # Use a string template passed directly
            for xml, obj in self.objects:
                button = {}
                button['mathml'] = xml
                button['math'] = _map_panel_types(obj)
                buttons.append( button )
        else:
            for xml, obj in self.objects:
                button = {}
                button['mathml'] = open(self.package + '/' + xml).read()
                button['math'] = _map_panel_types(obj)
                buttons.append( button )

        interface_ui = self.template

        c = Context({'name':self.name, 'buttons': buttons})
        return interface_ui.render(c)

def is_panel(obj):
    return isinstance(obj,Panel)

for pack in settings.INSTALLED_MATH_PACKAGES:
    try:
        path = '.'.join([ROOT_MODULE,pack,'panel'])
        packages[pack] = importlib.import_module(path)
        for name, symbol in packages[pack].__dict__.iteritems():
            if is_panel(symbol):
                symbol.package = pack
                if settings.DEBUG:
                    pass
                    #print "Importing panel ... %s/%s" % (pack, name)

                panels[name] = symbol
    except ImportError:
        raise exception.IncompletePackage(pack,'panel.py')
