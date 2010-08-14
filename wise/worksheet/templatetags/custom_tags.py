from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def brak2tex(value):
    value = value.replace('[[','\$')
    value = value.replace(']]','\$')
    return value
