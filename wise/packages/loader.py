import settings
from django.utils import importlib

def modulepath(*args):
    return '.'.join(args)

def load_package(package, directory=settings.PACK_MODULE):
    return importlib.import_module(modulepath(directory, package))

def load_package_module(package, module, directory=settings.PACK_MODULE):
    path = modulepath(directory,package, module)
    return importlib.import_module(path)
