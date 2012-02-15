
class UNSET(object):
    def __repr__(self):
        return "UNSET"

    def __nonzero__(self):
        return False

    def __eq__(self, rhs):
        return self.__class__ == rhs.__class__

UNSET = UNSET()


class AttrDict(MutableMapping):
    """
    Dictionary class that allows for accessing members as attributes or via
    regular dictionary lookup.

    """
    def __init__(self, *args, **kwargs):
        self.__dict__.update(*args, **kwargs)

    def __cmp__(self, rhs):
        return self.__dict__.__cmp__(rhs)

    def __contains__(self, item):
        return self.__dict__.__contains__(item)

    def __delitem__(self, item):
        return self.__dict__.__delitem__(item)

    def __eq__(self, rhs):
        return self.__dict__.__eq__(rhs)

    def __format__(self):
        return self.__dict__.__format__()

    def __ge__(self, rhs):
        return self.__dict__.__ge__(rhs)

    def __getitem__(self, item):
        return self.__dict__.__getitem__(item)

    def __gt__(self, rhs):
        return self.__dict__.__gt__(rhs)

    def __iter__(self):
        return self.__dict__.__iter__()

    def __le__(self, rhs):
        return self.__dict__.__le__(rhs)

    def __len__(self):
        return self.__dict__.__len__()

    def __lt__(self, rhs):
        return self.__dict__.__lt__(rhs)

    def __ne__(self, rhs):
        return self.__dict__.__ne__(rhs)

    def __repr__(self):
        return self.__dict__.__repr__()

    def __setitem__(self, item, val):
        return self.__dict__.__setitem__(item, val)

    def __str__(self):
        return self.__dict__.__str__()

    def clear(self):
        return self.__dict__.clear()

    def copy(self):
        return self.__class__(self.__dict__.copy())

    def fromkeys(self, keys, values=None):
        return self.__dict__.fromkeys(keys, values)

    def get(self, item, default=UNSET):
        if default != UNSET:
            return self.__dict__.get(item, default)
        return self.__dict__.get(item)

    def has_key(self, key):
        return self.__dict__.has_key(key)

    def items(self):
        return self.__dict__.items()

    def iteritems(self):
        return self.__dict__.iteritems()

    def iterkeys(self):
        return self.__dict__.iterkeys()

    def itervalues(self):
        return self.__dict__.itervalues()

    def keys(self):
        return self.__dict__.keys()

    def pop(self, key, default=UNSET):
        if default != UNSET:
            return self.__dict__.pop(key, default)
        return self.__dict__.pop(key)

    def popitem(self):
        return self.__dict__.popitem()

    def setdefault(self, default):
        return self.__dict__.setdefault(default)

    def update(self, *args, **kwargs):
        self.__dict__.update(*args, **kwargs)

    def values(self):
        return self.__dict__.values()

    def viewitems(self):
        return self.__dict__.viewitems()

    def viewkeys(self):
        return self.__dict__.viewkeys()

    def as_dict(self):
        return self.__dict__


