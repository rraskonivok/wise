# Aggregate all transforms from packages into one module...

# This way we can call wise.transforms.[DesiredTransform] in
# a very general fashion instead of dealing with individual 
# modules 

from types import FunctionType
from django.conf import settings
from django.utils import importlib

import wise.worksheet.exceptions as exception
from wise.library_utils import is_mapping
from wise.worksheet.utils import hashdict

ROOT_MODULE = 'wise.worksheet'
packages = {}
transforms = {}

# This is horribly inefficent but avoids using import * , and adds a level of security 
# since only Mapping types can be called by the ajax apply_transform request

for pack in settings.INSTALLED_MATH_PACKAGES:
    try:
        path = '.'.join([ROOT_MODULE,pack,'transforms'])
        packages[pack] = importlib.import_module(path)
        for name, symbol in packages[pack].__dict__.iteritems():
            # We short circuit in this order since is_mapping is simply a hash lookup while
            # isinstance is potentially costly
            if is_mapping(symbol) and isinstance(symbol,FunctionType):
                if settings.DEBUG:
                    print "Importing transform ... %s/%s" % (pack, name)

                transforms[name] = symbol
    except ImportError:
        raise exception.IncompletePackage(pack,'transforms.py')

def get_transform_by_path(pack, fun):
    return packages[pack].__dict__[fun]

def get_transform_by_str(fun):
    return transforms[fun]

# Hash the keys of the importing transforms, guaranteed to be unique to the specific
# combinations of imported libraries.
if settings.DEBUG:
    print 'Aggregated transforms have hash ...', hashdict(transforms.iterkeys())
