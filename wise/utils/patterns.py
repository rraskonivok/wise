import os
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

# This is threadsafe iff it is in read-only mode.
class Aggregator(object):
    """
    Lookup table with disk persistance that falls back to an
    in memory dictionary.
    """

    filename = None
    sha = None
    changed = False
    locked = False

    fallback = False
    fallback_dict = dict()

    def __init__(self,file=None, flag=None):
        try:
            self.filename = file

            # If the cache doesn't exist then create it
            if not os.path.exists(file):
                flag = 'c'

            self.persistance = shelve.open(self.filename, flag or 'r')
        except:
            print 'Could not load cache', self.filename
            self.persistance = self.fallback_dict
            self.fallback = True

    def __len__(self):
        return len(self.persistance)

    def __contains__(self, key):
        return key in self.persistance

    #def __del__(self):
    #    if self.persistance:
    #        self.persistance.close()
    #        del self.persistance

    def all(self):
        return [i for i in self.persistance]

    def iteritems(self):
        return self.persistance.iteritems()

    def itervalues(self):
        return self.persistance.itervalues()

    def iterkeys(self):
        return self.persistance.iterkeys()

    def make_writable(self):
        if self.fallback:
            return

        self.persistance.close()
        self.persistance = shelve.open(self.filename,'w')

    def make_readonly(self):
        self.persistance.close()
        self.persistance = shelve.open(self.filename,'r')

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

        self.persistance[key] = value

    def sync(self):
        if self.fallback:
            return

        self.locked = True
        self.persistance.sync()
        self.locked = False
