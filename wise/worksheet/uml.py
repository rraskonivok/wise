def generate(icls):

    strs = []
    def descend(cl):
        for cls in cl.__subclasses__():
            strs.append('[%s]^[%s|%s]' % (cl.__name__,cls.__name__, ';'.join(cls.__dict__.keys())))
            descend(cls)

    descend(icls)

    for st in strs:
        print st
