class PositiveClass(object):
    def __init__(self, perm_class):
        if isinstance(perm_class, PositiveClass):
            raise TypeError("Perm set already positive")
        if len(perm_class.of_length(0)) == 0:
            raise TypeError("Perm set does not contain empty perm")
        self._perm_class = perm_class

    def of_length(self, length):
        if length == 0:
            return set()
        else:
            return self._perm_class.of_length(length)

    def __repr__(self):
        return "Av+" + repr(self._perm_class)[2:]
