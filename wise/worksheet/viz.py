# -*- coding: utf-8 -*-

# Wise
# Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import settings
from wise.packages.loader import load_package_module

try:
    from pygraphviz import AGraph
    GRAPHVIZ = True
except ImportError:
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
