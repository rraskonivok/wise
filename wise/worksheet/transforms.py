from types import FunctionType
from django.conf import settings
from django.utils import importlib

import wise.worksheet.exceptions as exception
from wise.utils.library_utils import is_mapping

packages = {}
transforms = {}

# This is horribly inefficent but avoids using import * , and adds a level of security 
# since only Mapping types can be called by the ajax apply_transform request

for pack in settings.INSTALLED_MATH_PACKAGES:
#    try:
        path = '.'.join([settings.ROOT_MODULE,pack,'transforms'])
        packages[pack] = importlib.import_module(path)
        for name, symbol in packages[pack].__dict__.iteritems():
            # We short circuit in this order since is_mapping is simply a hash lookup while
            # isinstance is potentially costly
            if is_mapping(symbol) and isinstance(symbol,FunctionType):
                if settings.DEBUG:
                    pass
                    #print "Importing transform ... %s/%s" % (pack, name)

                transforms[name] = symbol
#    except ImportError:
#        raise exception.IncompletePackage(pack,'transforms.py')

def get_transform_by_path(pack, fun):
    return packages[pack].__dict__[fun]

def get_transform_by_str(fun):
    return transforms[fun]
