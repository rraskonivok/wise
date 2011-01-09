# General function to recursively consume the math hierarchy and
# output some form of structured data (UML , dotviz, ...)

import settings
from wise.utils.module_loading import module_has_submodule
from wise.packages.loader import load_package_module

try:
    from pygraphviz import AGraph
    GRAPHVIZ = True
except:
    GRAPHVIZ = False

def all_subclasses(cls, accumulator=set(),
                        depth=1,
                        max_inheritance_depth=30):

    accumulator.update(cls.__subclasses__())

    if depth < max_inheritance_depth:
        for scls in cls.__subclasses__():
            all_subclasses(scls, accumulator, depth=depth+1)

    return accumulator

def pycls2graph(*tcls):
    if not GRAPHVIZ:
        raise Exception('pygraphviz is not installed')
        return

    G = AGraph()

    def descend(cls):
        G.add_node(cls.__name__)
        for scls in cls.__subclasses__():
            G.add_node(scls.__name__)
            G.add_edge(cls.__name__,scls.__name__)
            descend(scls)

    for cls in tcls:
        descend(cls)

    return G

def package_to_graph(package):
    tops, nullary = load_package_module(package,'objects').initialize()
    return pycls2graph(*tops)
