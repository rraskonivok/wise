from django.conf import settings
from django.utils import importlib

import wise.worksheet.exceptions as exception
from wise.worksheet.utils import haml
from wise.base.objects import Term, Placeholder

from types import ClassType, InstanceType, TypeType
from inspect import getargspec
from django.template import Template, Context

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
            ph = Placeholder
            placeholder_tuple = (ph(),)*(len(args) - 1)
            return obj(*placeholder_tuple)
        except TypeError:
            print 'Type Error',args
    elif isinstance(obj, Term):
        return obj
    else:
        print 'Invalid object in panel', isinstance(obj, ClassType), isinstance(obj,InstanceType), isinstance(obj, TypeType) ,type(obj)

class Panel:
    package = None

    def get_html(self):
        interface_ui = self.template
        objects = [obj.get_html() for obj in self.objects]
        c = Context({'name':self.name, 'objects': objects})
        return interface_ui.render(c)

tablular_template = haml('''
<table>
    {% for object in objects %}
        <tr>
            <td>{{ object.0 }}</td>
            <td>{{ object.1 }}</td>
        </tr>
    {% endfor %}
</table>
''')

array_template = haml('''
{% for html in objects %}
    {{ html }}
{% endfor %}
''')

button_template = haml('''
{% for obj in objects %}
    span.uniform_button
        span onclick="subs('{{ obj.math }}');"
            <img src="/img/buttons/{{ obj.label }}"/>
{% endfor %}
''')

mathml_template = haml('''
{% for obj in buttons %}
    span.uniform_button
        span onclick="subs('{{ obj.math }}');"
            {{ obj.mathml|safe }}
{% endfor %}
''')

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


#tex_template = haml('''
#{% for obj in objects %}
#    span.uniform_button
#        span onclick="subs('{{ obj.math }}');"
#            $${{ obj.label }}$$
#{% endfor %}
#''')

class TabularPanel(Panel):
    template = Template(tablular_template)

    def __init__(self, name, objects):
        self.name = name
        self.objects = [(label, _map_panel_types(obj)) for label,obj in objects]

    def get_html(self):
        interface_ui = self.template
        objects = [(label, obj.get_html()) for label,obj in self.objects]
        c = Context({'name':self.name, 'objects': objects})
        return interface_ui.render(c)


class ArrayPanel(Panel):
    template = Template(array_template)

    def __init__(self, name, objects):
        self.name = name
        self.objects = map(_map_panel_types, objects)

class ButtonPanel(Panel):
    template = Template(button_template)

    def __init__(self, name, objects):
        self.name = name
        self.objects = [(label, _map_panel_types(obj)) for label,obj in objects]

    def get_html(self):
        interface_ui = self.template
        objects = []
        for label, obj in self.objects:
            obj.label = label
            objects.append(obj)

        c = Context({'name':self.name, 'objects': objects})
        return interface_ui.render(c)

class MathMLPanel(Panel):
    template = Template(mathml_template)

    def __init__(self, name, objects):
        self.name = name
        self.objects = objects


    def get_html(self):
        buttons = []

        for xml, obj in self.objects:
            button = {}
            button['mathml'] = open(self.package + '/' + xml).read()
            button['math'] = _map_panel_types(obj)
            buttons.append( button )

        interface_ui = self.template

        c = Context({'name':self.name, 'buttons': buttons})
        return interface_ui.render(c)

#class TexButton(Panel):
#    template = Template(tex_template)
#
#    def __init__(self, name, objects):
#        self.name = name
#        self.objects = [(label, _map_panel_types(obj)) for label,obj in objects]
#
#    def get_html(self):
#        interface_ui = self.template
#        objects = []
#        for label, obj in self.objects:
#            obj.label = label
#            objects.append(obj)
#
#        c = Context({'name':self.name, 'objects': objects})
#        return interface_ui.render(c)


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
