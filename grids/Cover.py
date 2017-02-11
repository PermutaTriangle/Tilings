# TODO: Docstring
# TODO: Make python2.7 compatible once permuta is

import warnings

from builtins import list
from operator import itemgetter
from permuta import Perm
from permuta import PermSet
from permuta.misc import ordered_set_partitions, flatten
from permuta.descriptors import Descriptor
from Tiling import PermSetTiled

class Cover(list):
    """Cover class.

    Tilings are stored in an array in size order.
    """

    input_set = PermSet()
    def __init__(self, input_set, tilings=[]):
        """Accepts a list of Tilings"""
        list.__init__(self, tilings) 
        self.input_set = input_set
        self.sort(key = lambda tiling: ((tiling._max_i+1)*(tiling._max_j+1), tiling._max_i, tiling.rank()))


    def __repr__(self):
        format_string = "<A cover of {} tilings>"
        return format_string.format(len(self))

    def __str__(self):
        pass

    def of_length(self, num):
        # Create examples
        ret = []
        for T in self:
            #print(T)
            for perm in PermSetTiled(T).of_length(num):
                ret.append(perm)
        return ret

if __name__ == "__main__":
    from Cover import Cover
    from Tiling import Tiling, Block
    b = Tiling({(0,0): Block.point, (1,1): Block.point})
    c = Tiling({(0,1): Block.point, (1,0): Block.point})
    d = Tiling({(0,0): Block.point, (1,1): Block.decreasing, (2,2): Block.increasing})
    from permuta import PermSet, Perm
    g = Cover(PermSet.avoiding([Perm.one([1,4,3,2])]), [d, c])

    print(g.__repr__())
    print(g.of_length(2))
