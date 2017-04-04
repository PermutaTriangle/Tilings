class PositiveClass(object):
    __INSTANCE_CACHE = {}

    def __new__(cls, perm_class):
        basis = perm_class.basis
        instance = PositiveClass.__INSTANCE_CACHE.get(basis)
        if instance is None:
            instance = super(PositiveClass, cls).__new__(cls)
            PositiveClass.__INSTANCE_CACHE[basis] = instance
        return instance

    def __init__(self, perm_class):
        if isinstance(perm_class, PositiveClass):
            raise TypeError("Perm set already positive")
        if len(perm_class.of_length(0)) == 0:
            raise TypeError("Perm set does not contain empty perm")
        self._perm_class = perm_class

    @property
    def basis(self):
        return self._perm_class.basis

    @property
    def perm_class(self):
        return self._perm_class

    def of_length(self, length):
        if length == 0:
            return set()
        else:
            return self._perm_class.of_length(length)

    def __contains__(self, item):
        if len(item) == 0:
            return False
        else:
            return item in self._perm_class

    def __repr__(self):
        return "Av+" + repr(self._perm_class)[2:]
