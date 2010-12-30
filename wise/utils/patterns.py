import shelve
from wise.utils.bidict import bidict

class Borg(object):
    """ Object with shared state across all instances """
    _shared_state = {}

    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj

class TranslationTable(object):
    """ Two way hash table with shared state across all instances """

    __shared_state = dict(
        table = bidict(),

        loaded = False,
        locked = False,
    )

    def __init__(self):
        self.__dict__ = self.__shared_state

    def populate(self, trans):
        self.table.update(trans)

class Aggregator(object):
    """ Lookup table with disk persistance """
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
