# General function to recursively consume the math hierarchy and
# output some form of structured data (UML , dotviz, ...)

# This generates data which can be consumed by http://www.yuml.me 

try:
    from pygraphviz import AGraph
    GRAPHVIZ = True
except:
    GRAPHVIZ = False

#def generate(icls):
#
#    strs = []
#    def descend(cl):
#        for cls in cl.__subclasses__():
#            strs.append('[%s]^[%s|%s]' % (cl.__name__,cls.__name__, ';'.join(cls.__dict__.keys())))
#            descend(cls)
#
#    descend(icls)
#
#    for st in strs:
#        print st

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
        for scls in cls.__subclasses__():
            G.add_node(scls.__name__)
            G.add_edge(cls.__name__,scls.__name__)
            descend(scls)

    for cls in tcls:
        descend(cls)

    return G
