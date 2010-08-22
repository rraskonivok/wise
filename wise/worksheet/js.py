from django import template

javascript_html = '''
{% autoescape off %}
<script language="javascript" type="text/javascript" data-type="ajax">
{{javascript}}
</script>
{% endautoescape %} 
'''

javascript_template = template.Template(javascript_html)

#-------------------------------------------------------------
# JQuery Interfaces
#-------------------------------------------------------------

def jquery(obj):
    '''Returns a jquery "function" (i.e. $('#uid123') )  for a given object'''
    return '$("#%s")' % obj.id


class prototype_dict(dict):
    '''Python and Javascript dictionaries are similar except that
    python requires strings, this eliminates quotes in the
    __str__ representation

    Example:
    > a = prototype_dict()
    > a['foo'] = 'bar'
    > print a
    { foo : 'bar' }

    '''

    def __repr__(self):
        s = ''
        for key,value in super(prototype_dict,self).iteritems():
            s += ' %s: %s,' % (key,value)
        return '{%s}' % s

class make_sortable(object):
    '''Wrapper to produce the jquery command to make ui elements
    sortable/connected'''

    sortable_object = None
    connectWith = None
    cancel = '".ui-state-disabled"'
    helper = "'clone'"
    tolerance = '"pointer"'
    placeholder = '"helper"'
    onout = None
    onupdate = 'function(event,ui) { update($(this)); }'
    onreceive = 'function(event,ui) { receive(ui,$(this),group_id); }'
    onremove = 'function(event,ui) { remove(ui,$(this)); }'
    onsort = None
    forcePlaceholderSize = '"true"'
    forceHelperSize = '"true"'
    dropOnEmpty = '"true"'
    axis = '"false"'

    def __init__(self, sortable_object,
            ui_connected=None,
            onremove=None,
            onrecieve=None,
            onsort=None,
            onupdate=None):

        self.sortable_object = jquery(sortable_object)
        if ui_connected is None:
            self.connectWith = 'undefined'
            self.upupdate = 'undefined'
        else:
            self.connectWith = jquery(ui_connected)

    def get_html(self):
        options = prototype_dict({'placeholder': self.placeholder,
                                  'connectWith': self.connectWith,
                                  'forceHelperSize': self.forceHelperSize,
                                  'helper': self.helper,
                                  'tolerance': self.tolerance,
                                  'axis': self.axis,
                                  'update': self.onupdate,
                                  'receive': self.onreceive,
                                  'remove': self.onremove,
                                  'cancel': self.cancel,
                                  #Revert is cool but buggy
                                  #'revert': 'true',
                                  #'deactivate': self.onupdate,
                                  'forcePlaceholderSize': self.forcePlaceholderSize})

        # An inconceivable amount of time/pain went into finding
        # out that different browsers execute/run javascript
        # immediately as it is loaded in the dom thus selectors
        # that call objects that are farther down will be empty,
        # this is solved by running all scripts when the document
        # signals it is. 

        args = (self.sortable_object, self.connectWith,
                str(options))

        html = '$(document).ready(function(){make_sortable(%s,%s,%s);})'

        return html % args
