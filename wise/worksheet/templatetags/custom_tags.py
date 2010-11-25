from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def brak2tex(value):
    value = value.replace('[[','\$')
    value = value.replace(']]','\$')
    return value

# template.render({'showme': False })
# {% conditional_display showme %} -> style="display: none"

@register.tag(name="conditional_display")
def do_display(parser, token):
    tag_name, cond_variable = token.split_contents()
    return DisplayNode(cond_variable)

class DisplayNode(template.Node):
    def __init__(self, cond_variable):
        self.condition = template.Variable(cond_variable)
    def render(self, context):
        # Resolve the argument out to Truthiness value
        if self.condition.resolve(context):
            return ''
        else:
            return 'style="display: none"'
