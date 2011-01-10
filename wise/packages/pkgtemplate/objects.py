from wise.packages.loader import load_package_module
Term = load_package_module('base','term').Term

def initialize():
    super_classes = []
    nullary_types = {}

    return super_classes, nullary_types
