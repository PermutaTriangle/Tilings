from collections import Counter, defaultdict
from heapq import heapify, heappop, heappush
from itertools import chain, product
from typing import TYPE_CHECKING, Dict, Iterator, List, Set, Tuple

from permuta import Perm
from tilings import GriddedPerm, Obstruction

if TYPE_CHECKING:
    from tilings import Tiling

Cell = Tuple[int, int]

VERBOSE = False

# better_bounds is a dict. the entry k:v means that if a cell contains the
#   full requirments in k, and no others touch it, then the upper bound for
#   the number of points that will need to be placed in that cell is the sum
#   of the lenths of the perms in k, minus v
# for example, a cell containing 01 and 10 has an upper bound of 3, not 4
better_bounds = {frozenset({Perm((0, 1)), Perm((1, 0))}): 1, frozenset({Perm((1, 0)), Perm((0, 1, 2))}): 1, frozenset({Perm((0, 1)), Perm((2, 1, 0))}): 1, frozenset({Perm((0, 1)), Perm((3, 2, 1, 0))}): 1, frozenset({Perm((1, 0)), Perm((0, 1, 2, 3))}): 1, frozenset({Perm((1, 0)), Perm((0, 1, 2, 3, 4))}): 1, frozenset({Perm((0, 1)), Perm((4, 3, 2, 1, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((2, 1, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((1, 2, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((2, 1, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((2, 0, 1))}): 1, frozenset({Perm((0, 2, 1)), Perm((2, 0, 1))}): 1, frozenset({Perm((0, 1, 2)), Perm((2, 0, 1))}): 1, frozenset({Perm((1, 0, 2)), Perm((1, 2, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((2, 1, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((1, 2, 0))}): 1, frozenset({Perm((0, 1, 3, 2)), Perm((2, 3, 1, 0))}): 1, frozenset({Perm((0, 1, 3, 2)), Perm((3, 1, 2, 0))}): 1, frozenset({Perm((0, 2, 1, 3)), Perm((2, 3, 1, 0))}): 1, frozenset({Perm((0, 2, 1, 3)), Perm((3, 2, 0, 1))}): 1, frozenset({Perm((1, 0, 2, 3)), Perm((3, 2, 1, 0))}): 1, frozenset({Perm((0, 1, 3, 2)), Perm((3, 2, 0, 1))}): 1, frozenset({Perm((0, 1, 2, 3)), Perm((2, 3, 1, 0))}): 1, frozenset({Perm((1, 0, 3, 2)), Perm((2, 3, 0, 1))}): 2, frozenset({Perm((1, 0, 2, 3)), Perm((3, 2, 0, 1))}): 1, frozenset({Perm((1, 0, 2, 3)), Perm((2, 3, 1, 0))}): 1, frozenset({Perm((0, 1, 3, 2)), Perm((3, 2, 1, 0))}): 1, frozenset({Perm((0, 1, 2, 3)), Perm((3, 2, 0, 1))}): 1, frozenset({Perm((1, 0, 2, 3)), Perm((3, 1, 2, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((1, 2, 0)), Perm((2, 1, 0))}): 3, frozenset({Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((1, 2, 0))}): 3, frozenset({Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((2, 1, 0))}): 3, frozenset({Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 1, 0))}): 3, frozenset({Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 0, 1))}): 3, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((2, 1, 0))}): 3, frozenset({Perm((0, 1, 2)), Perm((2, 0, 1)), Perm((2, 1, 0))}): 3, frozenset({Perm((0, 1, 2)), Perm((1, 0, 2)), Perm((2, 1, 0))}): 3, frozenset({Perm((0, 1, 2)), Perm((1, 0, 2)), Perm((1, 2, 0))}): 3, frozenset({Perm((0, 2, 1)), Perm((1, 2, 0)), Perm((2, 1, 0))}): 3, frozenset({Perm((0, 2, 1)), Perm((2, 0, 1)), Perm((2, 1, 0))}): 3, frozenset({Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((2, 0, 1))}): 3, frozenset({Perm((1, 0, 2)), Perm((2, 0, 1)), Perm((2, 1, 0))}): 3, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((2, 0, 1))}): 3, frozenset({Perm((0, 1, 2)), Perm((1, 2, 0)), Perm((2, 0, 1))}): 3, frozenset({Perm((0, 1, 2)), Perm((1, 0, 2)), Perm((2, 0, 1))}): 3, frozenset({Perm((0, 2, 1)), Perm((1, 2, 0)), Perm((2, 0, 1))}): 3, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 2, 0))}): 3, frozenset({Perm((1, 2, 0)), Perm((1, 0, 3, 2))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 1, 3, 2))}): 1, frozenset({Perm((1, 0, 2)), Perm((3, 2, 1, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((2, 3, 1, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((2, 3, 1, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((3, 2, 0, 1))}): 1, frozenset({Perm((0, 1, 2)), Perm((3, 2, 0, 1))}): 1, frozenset({Perm((0, 2, 1)), Perm((3, 2, 1, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((3, 2, 1, 0))}): 1, frozenset({Perm((2, 0, 1)), Perm((1, 0, 2, 3))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 1, 3, 2))}): 1, frozenset({Perm((0, 1, 2)), Perm((2, 3, 1, 0))}): 1, frozenset({Perm((1, 2, 0)), Perm((1, 0, 2, 3))}): 1, frozenset({Perm((0, 2, 1)), Perm((3, 2, 0, 1))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 1, 2, 3))}): 1, frozenset({Perm((0, 1, 2)), Perm((3, 1, 2, 0))}): 1, frozenset({Perm((2, 1, 0)), Perm((1, 0, 2, 3))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 2, 1, 3))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 1, 2, 3))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 2, 1, 3))}): 1, frozenset({Perm((0, 2, 1)), Perm((3, 1, 2, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((2, 3, 0, 1))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 1, 3, 2))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 2, 1, 3))}): 1, frozenset({Perm((2, 0, 1)), Perm((1, 0, 3, 2))}): 1, frozenset({Perm((1, 0, 2)), Perm((2, 3, 0, 1))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 1, 2, 3))}): 1, frozenset({Perm((1, 0, 2)), Perm((3, 1, 2, 0))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 1, 2, 4, 3))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 1, 2, 4, 3))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 2, 1, 4, 3))}): 1, frozenset({Perm((0, 1, 2)), Perm((4, 2, 3, 1, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((4, 3, 2, 0, 1))}): 1, frozenset({Perm((1, 0, 2)), Perm((4, 3, 1, 2, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((3, 4, 2, 1, 0))}): 1, frozenset({Perm((2, 0, 1)), Perm((1, 0, 2, 3, 4))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 2, 3, 1, 4))}): 1, frozenset({Perm((0, 2, 1)), Perm((4, 3, 2, 0, 1))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 1, 3, 2, 4))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 1, 3, 2, 4))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 3, 2, 1, 4))}): 1, frozenset({Perm((1, 0, 2)), Perm((4, 2, 3, 1, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((4, 1, 2, 3, 0))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 1, 2, 3, 4))}): 1, frozenset({Perm((2, 1, 0)), Perm((1, 0, 2, 4, 3))}): 1, frozenset({Perm((0, 1, 2)), Perm((4, 3, 2, 1, 0))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 1, 2, 4, 3))}): 1, frozenset({Perm((0, 2, 1)), Perm((4, 2, 1, 3, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((3, 4, 2, 0, 1))}): 1, frozenset({Perm((1, 0, 2)), Perm((4, 1, 3, 2, 0))}): 1, frozenset({Perm((2, 0, 1)), Perm((1, 0, 2, 4, 3))}): 1, frozenset({Perm((1, 0, 2)), Perm((4, 2, 3, 0, 1))}): 1, frozenset({Perm((0, 1, 2)), Perm((4, 3, 1, 2, 0))}): 1, frozenset({Perm((1, 2, 0)), Perm((1, 0, 2, 4, 3))}): 1, frozenset({Perm((1, 0, 2)), Perm((3, 4, 2, 1, 0))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 3, 2, 1, 4))}): 1, frozenset({Perm((0, 2, 1)), Perm((4, 2, 3, 0, 1))}): 1, frozenset({Perm((2, 0, 1)), Perm((1, 0, 3, 2, 4))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 3, 1, 2, 4))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 2, 1, 3, 4))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 1, 2, 3, 4))}): 1, frozenset({Perm((0, 1, 2)), Perm((4, 1, 3, 2, 0))}): 1, frozenset({Perm((1, 2, 0)), Perm((1, 0, 3, 2, 4))}): 1, frozenset({Perm((2, 1, 0)), Perm((1, 0, 2, 3, 4))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 3, 1, 2, 4))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 1, 2, 3, 4))}): 1, frozenset({Perm((0, 1, 2)), Perm((3, 4, 2, 1, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((4, 3, 2, 0, 1))}): 1, frozenset({Perm((0, 2, 1)), Perm((3, 4, 1, 2, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((4, 3, 2, 1, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((4, 3, 2, 1, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((3, 4, 1, 2, 0))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 1, 3, 2, 4))}): 1, frozenset({Perm((0, 2, 1)), Perm((4, 3, 1, 2, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((3, 4, 2, 0, 1))}): 1, frozenset({Perm((0, 2, 1)), Perm((4, 2, 3, 1, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((4, 1, 2, 3, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((4, 2, 1, 3, 0))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 2, 1, 3, 4))}): 1, frozenset({Perm((1, 0, 2)), Perm((3, 4, 2, 0, 1))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 2, 1, 4, 3))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 2, 1, 3, 4))}): 1, frozenset({Perm((1, 2, 0)), Perm((1, 0, 2, 3, 4))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 2, 3, 1, 4))}): 1, frozenset({Perm((2, 3, 1, 0)), Perm((1, 0, 2, 4, 3))}): 1, frozenset({Perm((2, 3, 1, 0)), Perm((0, 2, 3, 1, 4))}): 1, frozenset({Perm((3, 1, 2, 0)), Perm((1, 0, 2, 4, 3))}): 1, frozenset({Perm((3, 2, 0, 1)), Perm((1, 0, 2, 3, 4))}): 1, frozenset({Perm((2, 3, 1, 0)), Perm((0, 3, 2, 1, 4))}): 1, frozenset({Perm((0, 1, 3, 2)), Perm((4, 3, 1, 2, 0))}): 1, frozenset({Perm((0, 1, 3, 2)), Perm((4, 2, 1, 3, 0))}): 1, frozenset({Perm((3, 2, 0, 1)), Perm((0, 3, 2, 1, 4))}): 1, frozenset({Perm((2, 3, 1, 0)), Perm((1, 0, 2, 3, 4))}): 1, frozenset({Perm((1, 0, 2, 3)), Perm((4, 3, 1, 2, 0))}): 1, frozenset({Perm((0, 1, 3, 2)), Perm((4, 1, 3, 2, 0))}): 1, frozenset({Perm((0, 1, 3, 2)), Perm((4, 1, 2, 3, 0))}): 1, frozenset({Perm((1, 0, 2, 3)), Perm((4, 3, 2, 0, 1))}): 1, frozenset({Perm((0, 1, 3, 2)), Perm((3, 4, 2, 1, 0))}): 1, frozenset({Perm((0, 1, 3, 2)), Perm((4, 3, 2, 1, 0))}): 1, frozenset({Perm((2, 3, 1, 0)), Perm((0, 1, 2, 3, 4))}): 1, frozenset({Perm((1, 0, 2, 3)), Perm((4, 2, 1, 3, 0))}): 1, frozenset({Perm((1, 0, 2, 3)), Perm((4, 1, 2, 3, 0))}): 1, frozenset({Perm((3, 2, 0, 1)), Perm((0, 3, 1, 2, 4))}): 1, frozenset({Perm((1, 0, 2, 3)), Perm((3, 4, 2, 0, 1))}): 1, frozenset({Perm((2, 3, 1, 0)), Perm((0, 1, 2, 4, 3))}): 1, frozenset({Perm((0, 2, 1, 3)), Perm((3, 4, 2, 0, 1))}): 1, frozenset({Perm((1, 0, 2, 3)), Perm((4, 2, 3, 1, 0))}): 1, frozenset({Perm((3, 2, 0, 1)), Perm((0, 2, 3, 1, 4))}): 1, frozenset({Perm((2, 3, 1, 0)), Perm((0, 2, 1, 3, 4))}): 1, frozenset({Perm((1, 0, 2, 3)), Perm((4, 1, 3, 2, 0))}): 1, frozenset({Perm((0, 1, 3, 2)), Perm((3, 4, 2, 0, 1))}): 1, frozenset({Perm((0, 1, 3, 2)), Perm((4, 3, 2, 0, 1))}): 1, frozenset({Perm((1, 0, 2, 3)), Perm((4, 3, 2, 1, 0))}): 1, frozenset({Perm((3, 2, 0, 1)), Perm((1, 0, 2, 4, 3))}): 1, frozenset({Perm((2, 3, 1, 0)), Perm((0, 1, 3, 2, 4))}): 1, frozenset({Perm((3, 2, 1, 0)), Perm((1, 0, 2, 4, 3))}): 1, frozenset({Perm((3, 2, 0, 1)), Perm((0, 1, 2, 4, 3))}): 1, frozenset({Perm((1, 0, 2, 3)), Perm((3, 4, 2, 1, 0))}): 1, frozenset({Perm((0, 1, 2, 3)), Perm((3, 4, 2, 0, 1))}): 1, frozenset({Perm((3, 2, 0, 1)), Perm((0, 2, 1, 3, 4))}): 1, frozenset({Perm((3, 2, 0, 1)), Perm((0, 1, 3, 2, 4))}): 1, frozenset({Perm((2, 3, 1, 0)), Perm((0, 3, 1, 2, 4))}): 1, frozenset({Perm((0, 1, 3, 2)), Perm((4, 2, 3, 1, 0))}): 1, frozenset({Perm((3, 2, 0, 1)), Perm((0, 1, 2, 3, 4))}): 1, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((2, 0, 1)), Perm((2, 1, 0))}): 9, frozenset({Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((2, 0, 1)), Perm((2, 1, 0))}): 3, frozenset({Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((2, 0, 1))}): 6, frozenset({Perm((0, 1, 2)), Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((2, 0, 1))}): 6, frozenset({Perm((0, 2, 1)), Perm((1, 2, 0)), Perm((2, 0, 1)), Perm((2, 1, 0))}): 3, frozenset({Perm((0, 1, 2)), Perm((1, 2, 0)), Perm((2, 0, 1)), Perm((2, 1, 0))}): 3, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 2, 0)), Perm((2, 0, 1))}): 6, frozenset({Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((2, 1, 0))}): 6, frozenset({Perm((0, 1, 2)), Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((2, 1, 0))}): 6, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((1, 2, 0))}): 3, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 2, 0)), Perm((2, 1, 0))}): 6, frozenset({Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 0, 1)), Perm((2, 1, 0))}): 6, frozenset({Perm((0, 1, 2)), Perm((1, 0, 2)), Perm((2, 0, 1)), Perm((2, 1, 0))}): 6, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 0, 1))}): 3, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((2, 0, 1)), Perm((2, 1, 0))}): 6, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 1, 0))}): 3, frozenset({Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((2, 0, 1)), Perm((2, 1, 0))}): 6, frozenset({Perm((0, 1, 2)), Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((2, 0, 1)), Perm((2, 1, 0))}): 6, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((2, 0, 1))}): 6, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 2, 0)), Perm((2, 0, 1)), Perm((2, 1, 0))}): 6, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((2, 1, 0))}): 6, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 0, 1)), Perm((2, 1, 0))}): 6, frozenset({Perm((1, 2, 0)), Perm((2, 0, 1)), Perm((1, 0, 3, 2))}): 4, frozenset({Perm((1, 2, 0)), Perm((2, 0, 1)), Perm((1, 0, 2, 3))}): 4, frozenset({Perm((1, 2, 0)), Perm((2, 0, 1)), Perm((0, 2, 1, 3))}): 2, frozenset({Perm((1, 2, 0)), Perm((2, 0, 1)), Perm((0, 1, 3, 2))}): 4, frozenset({Perm((1, 2, 0)), Perm((2, 0, 1)), Perm((0, 1, 2, 3))}): 4, frozenset({Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((3, 2, 0, 1))}): 3, frozenset({Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((3, 0, 1, 2))}): 3, frozenset({Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((3, 0, 2, 1))}): 3, frozenset({Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((3, 2, 1, 0))}): 3, frozenset({Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((0, 3, 1, 2))}): 3, frozenset({Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((0, 3, 2, 1))}): 3, frozenset({Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((0, 1, 3, 2))}): 3, frozenset({Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((0, 1, 2, 3))}): 3, frozenset({Perm((1, 2, 0)), Perm((2, 1, 0)), Perm((1, 0, 3, 2))}): 3, frozenset({Perm((1, 2, 0)), Perm((2, 1, 0)), Perm((1, 0, 2, 3))}): 2, frozenset({Perm((1, 2, 0)), Perm((2, 1, 0)), Perm((0, 2, 1, 3))}): 2, frozenset({Perm((1, 2, 0)), Perm((2, 1, 0)), Perm((0, 1, 3, 2))}): 2, frozenset({Perm((1, 2, 0)), Perm((2, 1, 0)), Perm((0, 1, 2, 3))}): 2, frozenset({Perm((0, 2, 1)), Perm((1, 2, 0)), Perm((3, 2, 0, 1))}): 3, frozenset({Perm((0, 2, 1)), Perm((1, 2, 0)), Perm((3, 0, 1, 2))}): 3, frozenset({Perm((0, 2, 1)), Perm((1, 2, 0)), Perm((2, 0, 1, 3))}): 3, frozenset({Perm((0, 2, 1)), Perm((1, 2, 0)), Perm((1, 0, 2, 3))}): 3, frozenset({Perm((0, 2, 1)), Perm((1, 2, 0)), Perm((3, 1, 0, 2))}): 3, frozenset({Perm((0, 2, 1)), Perm((1, 2, 0)), Perm((2, 1, 0, 3))}): 3, frozenset({Perm((0, 2, 1)), Perm((1, 2, 0)), Perm((3, 2, 1, 0))}): 3, frozenset({Perm((0, 2, 1)), Perm((1, 2, 0)), Perm((0, 1, 2, 3))}): 3, frozenset({Perm((0, 1, 2)), Perm((1, 2, 0)), Perm((3, 2, 0, 1))}): 3, frozenset({Perm((0, 1, 2)), Perm((1, 2, 0)), Perm((3, 0, 2, 1))}): 3, frozenset({Perm((0, 1, 2)), Perm((1, 2, 0)), Perm((1, 0, 3, 2))}): 3, frozenset({Perm((0, 1, 2)), Perm((1, 2, 0)), Perm((3, 1, 0, 2))}): 3, frozenset({Perm((0, 1, 2)), Perm((1, 2, 0)), Perm((2, 1, 0, 3))}): 3, frozenset({Perm((0, 1, 2)), Perm((1, 2, 0)), Perm((3, 2, 1, 0))}): 3, frozenset({Perm((0, 1, 2)), Perm((1, 2, 0)), Perm((0, 3, 2, 1))}): 3, frozenset({Perm((1, 0, 2)), Perm((2, 0, 1)), Perm((1, 2, 3, 0))}): 3, frozenset({Perm((1, 0, 2)), Perm((2, 0, 1)), Perm((2, 3, 1, 0))}): 3, frozenset({Perm((1, 0, 2)), Perm((2, 0, 1)), Perm((1, 3, 2, 0))}): 3, frozenset({Perm((1, 0, 2)), Perm((2, 0, 1)), Perm((3, 2, 1, 0))}): 3, frozenset({Perm((1, 0, 2)), Perm((2, 0, 1)), Perm((0, 2, 3, 1))}): 3, frozenset({Perm((1, 0, 2)), Perm((2, 0, 1)), Perm((0, 3, 2, 1))}): 3, frozenset({Perm((1, 0, 2)), Perm((2, 0, 1)), Perm((0, 1, 3, 2))}): 3, frozenset({Perm((1, 0, 2)), Perm((2, 0, 1)), Perm((0, 1, 2, 3))}): 3, frozenset({Perm((2, 0, 1)), Perm((2, 1, 0)), Perm((1, 0, 3, 2))}): 3, frozenset({Perm((2, 0, 1)), Perm((2, 1, 0)), Perm((1, 0, 2, 3))}): 2, frozenset({Perm((2, 0, 1)), Perm((2, 1, 0)), Perm((0, 2, 1, 3))}): 2, frozenset({Perm((2, 0, 1)), Perm((2, 1, 0)), Perm((0, 1, 3, 2))}): 2, frozenset({Perm((2, 0, 1)), Perm((2, 1, 0)), Perm((0, 1, 2, 3))}): 2, frozenset({Perm((0, 2, 1)), Perm((2, 0, 1)), Perm((1, 2, 3, 0))}): 3, frozenset({Perm((0, 2, 1)), Perm((2, 0, 1)), Perm((1, 2, 0, 3))}): 3, frozenset({Perm((0, 2, 1)), Perm((2, 0, 1)), Perm((2, 3, 1, 0))}): 3, frozenset({Perm((0, 2, 1)), Perm((2, 0, 1)), Perm((1, 0, 2, 3))}): 3, frozenset({Perm((0, 2, 1)), Perm((2, 0, 1)), Perm((2, 1, 3, 0))}): 3, frozenset({Perm((0, 2, 1)), Perm((2, 0, 1)), Perm((2, 1, 0, 3))}): 3, frozenset({Perm((0, 2, 1)), Perm((2, 0, 1)), Perm((3, 2, 1, 0))}): 3, frozenset({Perm((0, 2, 1)), Perm((2, 0, 1)), Perm((0, 1, 2, 3))}): 3, frozenset({Perm((0, 1, 2)), Perm((2, 0, 1)), Perm((2, 3, 1, 0))}): 3, frozenset({Perm((0, 1, 2)), Perm((2, 0, 1)), Perm((1, 3, 2, 0))}): 3, frozenset({Perm((0, 1, 2)), Perm((2, 0, 1)), Perm((1, 0, 3, 2))}): 3, frozenset({Perm((0, 1, 2)), Perm((2, 0, 1)), Perm((2, 1, 3, 0))}): 3, frozenset({Perm((0, 1, 2)), Perm((2, 0, 1)), Perm((2, 1, 0, 3))}): 3, frozenset({Perm((0, 1, 2)), Perm((2, 0, 1)), Perm((3, 2, 1, 0))}): 3, frozenset({Perm((0, 1, 2)), Perm((2, 0, 1)), Perm((0, 3, 2, 1))}): 3, frozenset({Perm((1, 0, 2)), Perm((2, 1, 0)), Perm((1, 2, 3, 0))}): 3, frozenset({Perm((1, 0, 2)), Perm((2, 1, 0)), Perm((3, 0, 1, 2))}): 3, frozenset({Perm((1, 0, 2)), Perm((2, 1, 0)), Perm((2, 3, 0, 1))}): 3, frozenset({Perm((1, 0, 2)), Perm((2, 1, 0)), Perm((0, 2, 3, 1))}): 3, frozenset({Perm((1, 0, 2)), Perm((2, 1, 0)), Perm((0, 3, 1, 2))}): 3, frozenset({Perm((1, 0, 2)), Perm((2, 1, 0)), Perm((0, 1, 3, 2))}): 3, frozenset({Perm((1, 0, 2)), Perm((2, 1, 0)), Perm((0, 1, 2, 3))}): 3, frozenset({Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((3, 2, 0, 1))}): 4, frozenset({Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 1, 0))}): 4, frozenset({Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1))}): 4, frozenset({Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((3, 2, 1, 0))}): 4, frozenset({Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((3, 1, 2, 0))}): 2, frozenset({Perm((0, 1, 2)), Perm((1, 0, 2)), Perm((3, 2, 0, 1))}): 2, frozenset({Perm((0, 1, 2)), Perm((1, 0, 2)), Perm((2, 3, 1, 0))}): 2, frozenset({Perm((0, 1, 2)), Perm((1, 0, 2)), Perm((2, 3, 0, 1))}): 3, frozenset({Perm((0, 1, 2)), Perm((1, 0, 2)), Perm((3, 2, 1, 0))}): 2, frozenset({Perm((0, 1, 2)), Perm((1, 0, 2)), Perm((3, 1, 2, 0))}): 2, frozenset({Perm((0, 2, 1)), Perm((2, 1, 0)), Perm((1, 2, 3, 0))}): 3, frozenset({Perm((0, 2, 1)), Perm((2, 1, 0)), Perm((1, 2, 0, 3))}): 3, frozenset({Perm((0, 2, 1)), Perm((2, 1, 0)), Perm((3, 0, 1, 2))}): 3, frozenset({Perm((0, 2, 1)), Perm((2, 1, 0)), Perm((2, 0, 1, 3))}): 3, frozenset({Perm((0, 2, 1)), Perm((2, 1, 0)), Perm((1, 0, 2, 3))}): 3, frozenset({Perm((0, 2, 1)), Perm((2, 1, 0)), Perm((2, 3, 0, 1))}): 3, frozenset({Perm((0, 2, 1)), Perm((2, 1, 0)), Perm((0, 1, 2, 3))}): 3, frozenset({Perm((0, 1, 2)), Perm((2, 1, 0)), Perm((1, 3, 0, 2))}): 3, frozenset({Perm((0, 1, 2)), Perm((2, 1, 0)), Perm((2, 0, 3, 1))}): 3, frozenset({Perm((0, 1, 2)), Perm((2, 1, 0)), Perm((1, 0, 3, 2))}): 3, frozenset({Perm((0, 1, 2)), Perm((2, 1, 0)), Perm((2, 3, 0, 1))}): 3, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((3, 2, 0, 1))}): 2, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((2, 3, 1, 0))}): 2, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((2, 3, 0, 1))}): 3, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((3, 2, 1, 0))}): 2, frozenset({Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((3, 1, 2, 0))}): 2, frozenset({Perm((1, 0)), Perm((0, 1, 2, 3, 4, 5))}): 1, frozenset({Perm((0, 1)), Perm((5, 4, 3, 2, 1, 0))}): 1, frozenset({Perm((1, 0)), Perm((0, 1, 2, 3, 4, 5, 6))}): 1, frozenset({Perm((0, 1)), Perm((6, 5, 4, 3, 2, 1, 0))}): 1, frozenset({Perm((1, 2, 0)), Perm((1, 0, 4, 2, 3, 5))}): 1, frozenset({Perm((1, 2, 0)), Perm((1, 0, 3, 2, 5, 4))}): 1, frozenset({Perm((1, 2, 0)), Perm((1, 0, 3, 2, 4, 5))}): 1, frozenset({Perm((1, 2, 0)), Perm((1, 0, 4, 3, 2, 5))}): 1, frozenset({Perm((1, 2, 0)), Perm((1, 0, 2, 4, 3, 5))}): 1, frozenset({Perm((1, 2, 0)), Perm((1, 0, 2, 3, 5, 4))}): 1, frozenset({Perm((1, 2, 0)), Perm((1, 0, 2, 3, 4, 5))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 4, 1, 2, 3, 5))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 3, 1, 2, 5, 4))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 3, 1, 2, 4, 5))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 4, 1, 3, 2, 5))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 2, 1, 3, 5, 4))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 2, 1, 3, 4, 5))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 4, 2, 1, 3, 5))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 3, 2, 1, 5, 4))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 3, 2, 1, 4, 5))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 1, 4, 2, 3, 5))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 1, 3, 2, 5, 4))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 1, 3, 2, 4, 5))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 1, 4, 3, 2, 5))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 1, 2, 4, 3, 5))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 1, 2, 3, 5, 4))}): 1, frozenset({Perm((1, 2, 0)), Perm((0, 1, 2, 3, 4, 5))}): 1, frozenset({Perm((2, 0, 1)), Perm((1, 0, 3, 4, 2, 5))}): 1, frozenset({Perm((2, 0, 1)), Perm((1, 0, 3, 2, 5, 4))}): 1, frozenset({Perm((2, 0, 1)), Perm((1, 0, 3, 2, 4, 5))}): 1, frozenset({Perm((2, 0, 1)), Perm((1, 0, 4, 3, 2, 5))}): 1, frozenset({Perm((2, 0, 1)), Perm((1, 0, 2, 4, 3, 5))}): 1, frozenset({Perm((2, 0, 1)), Perm((1, 0, 2, 3, 5, 4))}): 1, frozenset({Perm((2, 0, 1)), Perm((1, 0, 2, 3, 4, 5))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 2, 3, 4, 1, 5))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 2, 3, 1, 5, 4))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 2, 3, 1, 4, 5))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 2, 4, 3, 1, 5))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 2, 1, 3, 5, 4))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 2, 1, 3, 4, 5))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 3, 2, 4, 1, 5))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 3, 2, 1, 5, 4))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 3, 2, 1, 4, 5))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 1, 3, 4, 2, 5))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 1, 3, 2, 5, 4))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 1, 3, 2, 4, 5))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 1, 4, 3, 2, 5))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 1, 2, 4, 3, 5))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 1, 2, 3, 5, 4))}): 1, frozenset({Perm((2, 0, 1)), Perm((0, 1, 2, 3, 4, 5))}): 1, frozenset({Perm((1, 0, 2)), Perm((5, 2, 3, 4, 0, 1))}): 1, frozenset({Perm((1, 0, 2)), Perm((5, 3, 4, 2, 0, 1))}): 1, frozenset({Perm((1, 0, 2)), Perm((5, 2, 4, 3, 0, 1))}): 1, frozenset({Perm((1, 0, 2)), Perm((4, 5, 3, 1, 2, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((4, 5, 1, 2, 3, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((4, 5, 1, 3, 2, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((5, 4, 3, 2, 0, 1))}): 1, frozenset({Perm((1, 0, 2)), Perm((4, 5, 3, 2, 1, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((5, 4, 2, 3, 0, 1))}): 1, frozenset({Perm((1, 0, 2)), Perm((4, 5, 2, 3, 1, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((5, 2, 3, 4, 1, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((5, 4, 3, 1, 2, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((5, 3, 4, 2, 1, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((5, 4, 1, 2, 3, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((5, 2, 4, 3, 1, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((5, 4, 1, 3, 2, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((4, 5, 3, 2, 0, 1))}): 1, frozenset({Perm((1, 0, 2)), Perm((5, 4, 3, 2, 1, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((5, 1, 3, 4, 2, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((5, 1, 4, 2, 3, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((4, 5, 2, 3, 0, 1))}): 1, frozenset({Perm((1, 0, 2)), Perm((5, 4, 2, 3, 1, 0))}): 1, frozenset({Perm((1, 0, 2)), Perm((5, 1, 4, 3, 2, 0))}): 1, frozenset({Perm((2, 1, 0)), Perm((1, 0, 2, 4, 3, 5))}): 1, frozenset({Perm((2, 1, 0)), Perm((1, 0, 2, 3, 5, 4))}): 1, frozenset({Perm((2, 1, 0)), Perm((1, 0, 2, 3, 4, 5))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 2, 3, 4, 1, 5))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 2, 4, 1, 3, 5))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 2, 3, 1, 4, 5))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 3, 1, 4, 2, 5))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 4, 1, 2, 3, 5))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 3, 1, 2, 4, 5))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 2, 1, 3, 5, 4))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 2, 1, 3, 4, 5))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 3, 4, 1, 2, 5))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 1, 3, 4, 2, 5))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 1, 4, 2, 3, 5))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 1, 3, 2, 4, 5))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 1, 2, 4, 3, 5))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 1, 2, 3, 5, 4))}): 1, frozenset({Perm((2, 1, 0)), Perm((0, 1, 2, 3, 4, 5))}): 1, frozenset({Perm((0, 2, 1)), Perm((5, 2, 3, 4, 0, 1))}): 1, frozenset({Perm((0, 2, 1)), Perm((5, 3, 4, 2, 0, 1))}): 1, frozenset({Perm((0, 2, 1)), Perm((4, 5, 3, 1, 2, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((4, 5, 1, 2, 3, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((5, 3, 2, 4, 0, 1))}): 1, frozenset({Perm((0, 2, 1)), Perm((4, 5, 2, 1, 3, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((5, 4, 3, 2, 0, 1))}): 1, frozenset({Perm((0, 2, 1)), Perm((4, 5, 3, 2, 1, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((5, 4, 2, 3, 0, 1))}): 1, frozenset({Perm((0, 2, 1)), Perm((4, 5, 2, 3, 1, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((5, 2, 3, 4, 1, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((5, 4, 3, 1, 2, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((5, 2, 3, 1, 4, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((5, 3, 4, 2, 1, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((5, 4, 1, 2, 3, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((5, 3, 1, 2, 4, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((5, 3, 2, 4, 1, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((5, 4, 2, 1, 3, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((5, 3, 2, 1, 4, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((4, 5, 3, 2, 0, 1))}): 1, frozenset({Perm((0, 2, 1)), Perm((5, 4, 3, 2, 1, 0))}): 1, frozenset({Perm((0, 2, 1)), Perm((4, 5, 2, 3, 0, 1))}): 1, frozenset({Perm((0, 2, 1)), Perm((5, 4, 2, 3, 1, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((5, 3, 4, 2, 0, 1))}): 1, frozenset({Perm((0, 1, 2)), Perm((4, 5, 3, 1, 2, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((5, 4, 3, 2, 0, 1))}): 1, frozenset({Perm((0, 1, 2)), Perm((4, 5, 3, 2, 1, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((5, 4, 3, 1, 2, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((5, 2, 4, 1, 3, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((5, 3, 4, 2, 1, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((5, 3, 1, 4, 2, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((5, 2, 4, 3, 1, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((5, 4, 1, 3, 2, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((5, 2, 1, 4, 3, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((5, 3, 2, 4, 1, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((5, 4, 2, 1, 3, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((5, 3, 2, 1, 4, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((4, 5, 3, 2, 0, 1))}): 1, frozenset({Perm((0, 1, 2)), Perm((5, 4, 3, 2, 1, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((5, 4, 2, 3, 1, 0))}): 1, frozenset({Perm((0, 1, 2)), Perm((5, 1, 4, 3, 2, 0))}): 1}

class Info(tuple):
    def __lt__(self, other):
        return self[0].__lt__(other[0])

class MinimalGriddedPerms():
    def __init__(self, tiling: 'Tiling'):
        self.tiling = tiling
        self.obstructions = tiling.obstructions
        self.requirements = tiling.requirements
        self.yielded = set()  # type: Set[GriddedPerm]
        self.queue = []  # type: List[Info]
        self.cells_tried = defaultdict(set)  # type: Dict[Cell, Set[Cell]]
        self.work_packets_done = set()
        self.num_work_packets = 0
        self.relevant_obstructions = dict()
        self.relevant_obstructions_by_cell = dict()
        self.initial_gps_to_auto_yield = set()

        # given a goal gps and cell (x,y), this contains truncations of
        #   the reqs in gps to the cells < (x,y) in normal sort order
        self.requirements_up_to_cell = dict()

        # a priority queue sorted by length of the gridded perm. This is
        # ensured by overwriting the __lt__ operator in the Info class.
        heapify(self.queue)

    def get_requirements_up_to_cell(self, cell: Cell, gps: Tuple[GriddedPerm]) -> List[GriddedPerm]:
        if (cell, gps) not in self.requirements_up_to_cell:
            all_cells = product(range(self.tiling.dimensions[0]),
                                range(self.tiling.dimensions[1]))
            relevant_cells = [p for p in all_cells if p < cell]
            self.requirements_up_to_cell[(cell,gps)] = [
                req.get_gridded_perm_in_cells(relevant_cells)
                for req in gps]
        return self.requirements_up_to_cell[(cell, gps)]

    # Get just the obstructions that involve only cells involved in requirements
    def get_relevant_obstructions(self, gps):
        if gps not in self.relevant_obstructions:
            relevant_cells = set(chain.from_iterable(gp.pos for gp in gps))
            self.relevant_obstructions[gps] = [
                ob for ob in self.obstructions
                if all(p in relevant_cells for p in ob.pos)]
        return self.relevant_obstructions[gps]

    # Get just the obstructions that involve only cells involved in the
    #   requirements in [gps] and involve [cell]
    def get_relevant_obstructions_by_cell(self, gps, cell):
        if (gps, cell) not in self.relevant_obstructions_by_cell:
            relevant_obstructions = self.get_relevant_obstructions(gps)
            self.relevant_obstructions_by_cell[(gps,cell)] = [
                    ob for ob in relevant_obstructions
                    if cell in ob.pos]
        return self.relevant_obstructions_by_cell[(gps,cell)]

    def satisfies_requirements(self, gp: GriddedPerm) -> bool:
        """Check if a gridded permutation contains all requirements."""
        return all(gp.contains(*req) for req in self.requirements)

    def yielded_subgridded_perm(self, gp: GriddedPerm) -> bool:
        """Return True if a subgridded perm was yielded."""
        return gp.contains(*self.initial_gps_to_auto_yield) or gp.contains(*self.yielded)

    def prepare_queue(self, yield_if_non_minimal=False) -> None:
        """Add cell counters with gridded permutations to the queue."""
        if len(self.requirements) <= 1:
            return
        for gps in product(*self.requirements):
            # upward clousure
            upward_closure = self.upward_closure(*gps)

            # try to stitch together as much of the independent cells of the
            # gridded permutation together first
            initial_gp = self.initial_gp(*upward_closure)

            if not initial_gp.avoids(*self.get_relevant_obstructions(gps)):
                continue
            if self.satisfies_requirements(initial_gp):
                if yield_if_non_minimal:
                    yield initial_gp
                else:
                    # even if [initial_gp] meets the requirements yet, we can't
                    #   yield it yet, because it might not be minimal
                    # so, we add it to a list, and yield it when we see it later
                    #   if it actually is minimal
                    if VERBOSE:
                        print(" -- setting up to auto-yield --")
                    self.initial_gps_to_auto_yield.add(initial_gp)

            # collect the localised subgridded perms as we will insert into
            # cells not containing thest first as they are needed.
            localised_patts = self.localised_patts(*upward_closure)

            # max_cell_count is the theoretical bound on the size of the
            # largest minimal gridded permutation that contains each
            # gridded permutation in gps.
            max_cell_count = self.cell_counter(*upward_closure)

            # now we look for any cells containing more than one full req and
            #   are not involved with any other requirements, because we may be
            #   able to apply a better upper bound to the number of points
            #   required in the cell
            for cell in set(chain.from_iterable(gp.pos for gp in gps)):
                in_this_cell = set()
                good = True
                for req in gps:
                    # we ignore point requirements
                    if len(req) == 1:
                        continue
                    if set(req.pos) == set([cell]):
                        # [req] is entirely in [cell]
                        in_this_cell.add(req.patt)
                    elif cell in req.pos:
                        # [req] involves [cell], but also some other cell, so
                        #   this cell won't have a usable upper bound
                        good = False
                        continue
                if good:
                    if len(in_this_cell) >= 2:
                        # I think "upward closure" obviates this check, but I'll do it anyway
                        #   Christian: please weigh in here!
                        if not any(any(p != q and p.contains(q) for p in in_this_cell) for q in in_this_cell):
                            in_this_cell = frozenset(in_this_cell)
                            if in_this_cell in better_bounds:
                                max_cell_count[cell] -= better_bounds[in_this_cell]

            # we pass on this information, together with the target gps
            # will be used to guide us in choosing smartly which cells to
            # insert into - see the 'get_cells_to_try' method.
            mindices = {cell: -1 for cell in max_cell_count}
            if VERBOSE:
                print("-- initial --: {}".format(initial_gp))
            new_info = Info([initial_gp, localised_patts,
                             max_cell_count, tuple(gps), (-1, -1), True,
                             mindices])
            heappush(self.queue, new_info)

    @staticmethod
    def initial_gp(*gps):
        """
        Return the gridded perm that initialises with the first argument,
        then adds as many points as possible from the left to right, such that
        the cells don't share a row or column. In this instance, to contain
        both you must contain the respective subgridded perm in the independent
        cell.
        """
        # initialise with the first gridded permutation in gps.
        # the sort here is a heuristic. the idea is to try avoid having to
        # insert into more cells in the future.
        # gps = sorted(gps, key=lambda x: -len(x))
        # note from jay: some testing showed the heuristic made it a little worse
        res = GriddedPerm(gps[0].patt, gps[0].pos)
        active_cols = set(i for i, j in res.pos)
        active_rows = set(j for i, j in res.pos)
        for gp in gps[1:]:
            # for each subsequent gridded perm in gps, find all the cells
            # not on the same row or column
            indep_cells = [(i, j) for i, j in gp.pos
                           if i not in active_cols and j not in active_rows]
            if indep_cells:
                # take the subgp using the independent cells.
                # we will now glue together the result, and the new independent
                # cell in the unique way that this can be done
                subgp = gp.get_gridded_perm_in_cells(indep_cells)
                # update future active rows and cols
                active_cols.update(i for i, j in subgp.pos)
                active_rows.update(j for i, j in subgp.pos)
                # temp will be sorted, and standardised to create the unique
                # minimal gridded permutation containing both res and subgp.
                # We want cells at lower index front - if they are in the same
                # column, then they come from the same gridded permutation, so
                # we sort second by the index of its original gridded perm.
                # We will standardise based on values. Those in lower cells
                # will have smaller value, and if they are in the same row then
                # they come from the same gridded permutation so the second
                # entry is the value from its original gridded perm.
                temp = ([((cell[0], idx), (cell[1], val))
                         for (idx, val), cell in zip(enumerate(res.patt),
                                                     res.pos)] +
                        [((cell[0], idx), (cell[1], val))
                         for (idx, val), cell in zip(enumerate(subgp.patt),
                                                     subgp.pos)])
                temp.sort()
                # update the res
                new_pos = [(idx[0], val[0]) for idx, val in temp]
                new_patt = Perm.to_standard(val for _, val in temp)
                res = GriddedPerm(new_patt, new_pos)
        return res

    @staticmethod
    def cell_counter(*gps: GriddedPerm) -> Counter:
        """Returns a counter of the sum of number of cells used by the gridded
        permutations. If 'counter' is given, will update this Counter."""
        return Counter(chain.from_iterable(gp.pos for gp in gps))

    @staticmethod
    def localised_patts(*gps: GriddedPerm) -> Dict[Cell, List[GriddedPerm]]:
        """Return the localised patts that gps must contain."""
        res = defaultdict(set)  # type: Dict[Cell, Set[GriddedPerm]]
        # for each gp, and cell find the localised subgridded perm in the cell
        for gp in gps:
            for cell in set(gp.pos):
                res[cell].add(gp.get_gridded_perm_in_cells([cell]))
        # Only keep the upward closure for each cell.
        return {cell: MinimalGriddedPerms.upward_closure(*patts)
                for cell, patts in res.items()}

    @staticmethod
    def upward_closure(*gps: GriddedPerm) -> List[GriddedPerm]:
        """Return list of gridded perms such that every gridded perm contained
        in another is removed."""
        res = []  # type: List[GriddedPerm]
        for gp in sorted(gps, key=len, reverse=True):
            if all(gp not in g for g in res):
                res.append(gp)
        return res

    def get_cells_to_try(
                         self,
                         gp: GriddedPerm,
                         localised_patts: Dict[Cell, List[GriddedPerm]],
                         max_cell_count: Counter,
                         gps: List[GriddedPerm],
                         try_localised: bool
                        ) -> Iterator[Cell]:
        """Yield cells that a gridded permutation could be extended by."""
        cells = set()  # type: Set[Cell]
        for g, req in zip(gps, self.requirements):
            if gp.avoids(*req):
                # Only insert into cells in the requirements that are not
                # already satisfied.
                cells.update(g.pos)
            elif gp.avoids(g):
                # If any requirement contains a requirement, but not the target
                # gridded perm from that requirement in gps, then inserting
                # further will not result in a minimal gridded perm that will
                # not be found by another target.
                return

        cells = sorted(list(cells))
        if VERBOSE:
            print("\tcandidate cells: {}".format(cells))
        currcellcounts = self.cell_counter(gp)

        def try_yield(cells, localised):
            # Only insert into cells if we have not gone above the theoretical
            # bound on the number of points needed to contains all gridded
            # permutations in gps, and not yielded before.
            for cell in cells:
                if VERBOSE:
                    print("\t\t\tcell={}\tmcc > ccc ({} > {})\t{}".format(cell,max_cell_count[cell],currcellcounts[cell],self.cells_tried[(gp,gps)]))
                if (max_cell_count[cell] > currcellcounts[cell] and
                        cell not in self.cells_tried[(gp, gps)]):
                    # store this to prevent yielding same cell twice.
                    self.cells_tried[(gp, gps)].add(cell)
                    yield (cell, localised)

        if try_localised:
            for cell in cells:
                # try to insert into a cell that doesn't contain all of the
                # localised patterns frist
                if gp.avoids(*localised_patts[cell]):
                    if VERBOSE:
                        print("\t\twill try to yield {}".format(cell))
                    yield from try_yield([cell], True)
                    return
                else:
                    if VERBOSE:
                        print("\t\tcan't yield {}\n\t\t\tlp={}".format(cell,localised_patts[cell]))
        # otherwise, we are none the wiser which cell to insert into so try
        # all possible cells
        yield from try_yield(cells, False)

    # the "yield_if_non_minimal" flag is passed to prepare_queue, instructing
    #   it to yield an initial_gp that is on the tiling immediately, even
    #   though it may not be minimal. this is useful when trying to just
    #   determine whether or not a tiling is empty.
    def minimal_gridded_perms(self, yield_if_non_minimal=False) -> Iterator[GriddedPerm]:
        """Yield all minimal gridded perms on the tiling."""
        if not self.requirements:
            if Obstruction.empty_perm() not in self.obstructions:
                yield GriddedPerm.empty_perm()
            return
        if len(self.requirements) == 1:
            yield from map(lambda req : GriddedPerm(req.patt, req.pos), self.requirements[0])
            return

        yield from self.prepare_queue(yield_if_non_minimal=yield_if_non_minimal)

        while self.queue:
            # take the next gridded permutation of the queue, together with the
            # theoretical counts to create a gridded permutation containing
            # each of gps.
            (gp, localised_patts, max_cell_count, gps, last_cell,
             still_localising, last_mindices) = heappop(self.queue)
            if VERBOSE:
                print("processing {} ({})".format(gp, last_cell, last_mindices))

            # if gp was one of the initial_gps that satisfied obs/reqs, but
            #   we weren't sure at the time if it was minimal, then now is the
            #   time to check and yield!
            if gp in self.initial_gps_to_auto_yield:
                # removing this speed up a later check by a tiny bit
                self.initial_gps_to_auto_yield.remove(gp)
                if not self.yielded_subgridded_perm(gp):
                    if VERBOSE:
                        print(" -- yielding --")
                    self.yielded.add(gp)
                    yield gp
                continue

            # now we try inserting a new point into the cell
            for (cell, localised) in self.get_cells_to_try(gp, localised_patts,
                                              max_cell_count, gps, still_localising):
                # [localised] tells us whether we've been given a cell to try
                #   to build a localised_patt, or not. If not, then we must
                #   always be moving to greater cells
                if not localised and cell < last_cell:
                    if VERBOSE:
                        print("\t\tcell {} is no good".format(cell))
                    continue
                if VERBOSE:
                    print("\tcell {} good".format(cell))
                if not localised and cell > last_cell:
                    if not all(gp.contains(req) for req in self.get_requirements_up_to_cell(cell, gps)):
                        if VERBOSE:
                            print("\tpassing because of prior reqs  ")
                        continue

                # in this cell, we always insert to the right of all previously
                #   placed points
                mindex, maxdex, minval, maxval = gp.get_bounding_box(cell)
                mindex = max(mindex, last_mindices[cell])
                for idx, val in product(range(maxdex, mindex - 1, -1),
                                        range(minval, maxval + 1)):
                    nextgp = gp.insert_specific_point(cell, idx, val)

                    if nextgp.avoids(*self.get_relevant_obstructions_by_cell(gps,cell)):
                        if not self.yielded_subgridded_perm(nextgp):
                            if self.satisfies_requirements(nextgp):
                                if VERBOSE:
                                    print(" -- yielding --")
                                self.yielded.add(nextgp)
                                yield nextgp
                            else:

                                next_cell = last_cell if localised else cell
                                if (nextgp, gps, next_cell) not in self.work_packets_done:
                                    if VERBOSE:
                                        print("\tpushing {}".format(nextgp))
                                    next_mindices = {c: i if i <= idx else i + 1
                                                     for c, i in last_mindices.items() if c != cell}
                                    next_mindices[cell] = idx + 1
                                    self.work_packets_done.add((nextgp, gps, next_cell))
                                    heappush(self.queue,
                                             Info([nextgp, localised_patts,
                                                   max_cell_count, gps, next_cell, localised, next_mindices]))
                                else:
                                    if VERBOSE:
                                        print("\twork packet {} already made".format(nextgp))
        if VERBOSE:
            print("{} work packets".format(len(self.work_packets_done)))
