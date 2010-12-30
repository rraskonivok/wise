import shelve

class Aggregator(object):
    filename = None
    persistance = None
    sha = None
    changed = False
    locked = False

    def __init__(self, **args):
        if self.filename:
            self.persistance = shelve.open(self.filename)
        elif 'file' in args:
            self.persistance = shelve.open(args['file'])
        else:
            raise OSError('No file persistance for Aggregator.')

    def all(self):
        return [i for i in self.persistance]

    def __len__(self):
        return len(self.persistance)

    def __contains__(self, key):
        return key in self.persistance

    def iteritems(self):
        return self.persistance.iteritems()

    def __getitem__(self, key):

        #if self.persistance:
            try:
                # These things don't like Unicode
                return self.persistance[str(key)]
            except AttributeError:
                raise Exception('Pickled object cannot be initialized from persistance since corresponding object does not exist.')
        #else:
        #    raise OSError('No file persistance for Aggregator.')

    def __setitem__(self, key, value):
        if self.locked:
            raise Exception('Cannot write key since Aggregator is locked.')
            return

#        if self.persistance:
        self.persistance[key] = value
#        else:
#            raise OSError('No file persistance for Aggregator.')

    def sync(self):
        self.locked = True
        self.persistance.sync()
        self.locked = False
