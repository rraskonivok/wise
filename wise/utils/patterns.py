import shelve

class Borg(object):
    """ Object with shared state across all instances """
    _shared_state = {}

    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj

class TranslationTable(object):
    """ Two way hash table with shared state across all instances """

    def populate(self, trans):
        self.loaded = True
        self.table.update(trans)

    def lookup(self, key):
        return self.table[key]

    def reverse_lookup(self, key):
        return self.table[:key]

    def __getitem__(self, key):
        return self.table[key]

class Aggregator(object):
    """
    Lookup table with disk persistance that falls back to an
    in singleton dictionary.
    """
    filename = None
    persistance = {}
    sha = None
    changed = False
    locked = False
    fallback = False

    def __init__(self, **args):
        self.filename = args['file']

        if self.filename:
            try:
                self.persistance = shelve.open(self.filename)
            except:
                print 'Could not load cache', self.filename
                self.fallback = True

        elif 'file' in args:

            try:
                self.persistance = shelve.open(args['file'])
            except:
                print 'Could not load cache', self.filename
                self.fallback = True

        else:
                self.fallback = True

    def all(self):
        return [i for i in self.persistance]

    def __len__(self):
        return len(self.persistance)

    def __contains__(self, key):
        return key in self.persistance

    def iteritems(self):
        return self.persistance.iteritems()

    def itervalues(self):
        return self.persistance.itervalues()

    def iterkeys(self):
        return self.persistance.iterkeys()

    def __getitem__(self, key):

        try:
            # These things don't like Unicode
            return self.persistance[str(key)]
        except AttributeError:
            raise Exception('Pickled object cannot be\
                    initialized from persistance since\
                    corresponding object does not exist.')
        except KeyError:
            raise

    def update(self, dct):
        self.persistance.update(dct)

    def as_dict(self):
        return dict(self.persistance)

    def __setitem__(self, key, value):
        if self.locked:
            raise Exception('Cannot write key since Aggregator is locked.')
            return

#        if self.persistance:
        self.persistance[key] = value
#        else:
#            raise OSError('No file persistance for Aggregator.')

    def sync(self):
        if self.fallback:
            return

        self.locked = True
        self.persistance.sync()
        self.locked = False
