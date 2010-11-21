# General function to recursively consume the math hierarchy and
# output some form of structured data (UML , dotviz, ...)

# This generates data which can be consumed by http://www.yuml.me 
def generate(icls):

    strs = []
    def descend(cl):
        for cls in cl.__subclasses__():
            strs.append('[%s]^[%s|%s]' % (cl.__name__,cls.__name__, ';'.join(cls.__dict__.keys())))
            descend(cls)

    descend(icls)

    for st in strs:
        print st
