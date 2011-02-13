import os

from inspect import getargspec
from types import TypeType

from django.conf import settings
from django.template import Context

from wise.worksheet.utils import load_haml_template
from wise.worksheet.utils import trim_docstring
from wise.utils.patterns import Aggregator
from wise.utils.module_loading import module_has_submodule
from wise.packages import loader

Placeholder = loader.load_package_module('base','objects').Placeholder
panels = Aggregator(file='cache/panels_cache')

def _map_panel_types(obj):
    # If we have a Class read the argument signature of the
    # __init__ function and fill in all required arguments with
    # Placeholders.
    # Example:
    #   Addition -> Addition(Placeholder(),Placeholder())
    if isinstance(obj, TypeType):
        # Get the number of arguments the __init__ function for
        # the mathobject takes and substitute placeholder in for
        # each argument
        args, varargs, keywords, defaults = getargspec(obj.__init__)

        # decrement the len(args) since we ignore the self
        # argument
        arglength = (len(args) - 1) or 1;
        try:
            placeholder_tuples = (Placeholder(),)*(arglength)
            return obj(*placeholder_tuples)
        except TypeError:
            print 'Type Error',args, arglength

    # If an instance is passed do nothing and just pass it
    # along.
    # Example:
    #   Variable('x')
    else:
        return obj

class Panel:
    package = None

    def get_html(self):
        interface_ui = self.template
        objects = [obj.get_html() for obj in self.objects]
        c = Context({'name':self.name, 'objects': objects})
        return interface_ui.render(c)

class MathMLPanel(Panel):
    template = load_haml_template('mathml_buttons.tpl')

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
                button['tooltip'] = trim_docstring(obj.__doc__)
                buttons.append( button )
        else:
            for xml, obj in self.objects:
                # Search in $PACKAGE/buttons/$XML for the MathML
                # to render on the button
                button = {}
                panel = os.path.join(settings.PACKAGE_DIR, self.package, xml)
                button['mathml'] = open(panel).read()
                button['tooltip'] = trim_docstring(obj.__doc__)
                button['math'] = _map_panel_types(obj)
                buttons.append( button )

        interface_ui = self.template
        c = Context({'name':self.name, 'buttons': buttons})
        return interface_ui.render(c)

def is_panel(obj):
    return isinstance(obj,Panel)

def build_panels(force=False):
    if panels and not settings.NOCACHE:
        print 'Using cached panels file.'
        return

    for pack_name in settings.INSTALLED_MATH_PACKAGES:
        print 'Importing panels from ... ' + pack_name
        pack_module = loader.load_package(pack_name)

        # Load PACKAGE/panel.py
        if module_has_submodule(pack_module, 'panel'):
            pack_panels = loader.load_package_module(pack_name,'panel')

            panels.make_writable()
            for panel_name, symbol in pack_panels.__dict__.iteritems():
                if is_panel(symbol):
                    symbol.package = pack_name
                    panels[panel_name] = symbol

            panels.sync()
