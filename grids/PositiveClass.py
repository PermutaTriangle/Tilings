class PositiveClass(object):
    def __init__(self, perm_class):
        if isinstance(perm_class, PositiveClass):
            raise TypeError("Perm set already positive")
        if len(perm_class.of_length(0)) == 0:
            raise TypeError("Perm set does not contain empty perm")
        self._perm_class = perm_class

    @property
    def basis(self):
        return self._perm_class.basis

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

    def __eq__(self, other):
        return isinstance(other, PositiveClass) \
           and self._perm_class == other._perm_class

    def __hash__(self):
        return hash(hash(self._perm_class) + 4)  # Totally arbitrary

    def __repr__(self):
        return "Av+" + repr(self._perm_class)[2:]
