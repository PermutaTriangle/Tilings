from itertools import chain, combinations

from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NONE, DIR_NORTH, DIR_SOUTH, DIR_WEST


class GriddedPerm():
    def __init__(self, pattern, positions):
        # TODO: Write check to verify gridded permutation makes sense, that is,
        # pattern can be mapped on the positions given.

        if not isinstance(pattern, Perm):
            raise ValueError("Pattern should be a instance of permuat.Perm")
        if not len(pattern):
            self.patt = pattern
            self.pos = tuple(positions)
            self._cells = frozenset()
            self._rows = 1
            self._columns = 1
        else:
            # Pattern should be a Perm of course
            self.patt = pattern
            # Position is a tuple of (x, y) coordinates, where the ith (x, y)
            # corresponds to the i-th point in the pattern.
            self.pos = tuple(positions)

            if len(self.patt) != len(self.pos):
                raise ValueError(("Pattern and position list have unequal"
                                  "lengths."))

            # Immutable set of cells which the gridded permutation spans.
            self._cells = frozenset(self.pos)

    @classmethod
    def single_cell(cls, pattern, cell):
        """Construct a gridded permutation where the cells are all located in a
        single cell."""
        return cls(pattern, [cell for _ in range(len(pattern))])

    @classmethod
    def empty_perm(cls):
        """Construct the empty gridded permutation."""
        return cls(Perm(tuple()), tuple())

    def occupies(self, cell):
        """Checks if the gridded permutation has a point in the given cell."""
        return cell in self._cells

    def occurrences_in(self, other):
        """Returns all occurrences of self in other."""
        for occ in self.patt.occurrences_in(other.patt):
            if all(self.pos[i] == other.pos[occ[i]] for i in range(len(occ))):
                yield occ

    def occurs_in(self, other):
        """Checks if self occurs in other."""
        return any(self.occurrences_in(other))

    def remove_cells(self, cells):
        """Remove any points in the cell given and return a new gridded
        permutation."""
        remaining = [i for i in range(len(self)) if self.pos[i] not in cells]
        return self.__class__(
            Perm.to_standard(self.patt[i] for i in remaining),
            (self.pos[i] for i in remaining))

    def points_in_cell(self, cell):
        """Yields the indices of the points in the cell given."""
        for i in range(len(self)):
            if self.pos[i] == cell:
                yield i

    def isolated_cells(self):
        """Yields the cells that contain only one point of the gridded
        permutation and are in their own row and column."""
        for i in range(len(self)):
            isolated = True
            for j in range(len(self)):
                if i == j:
                    continue
                if (self.pos[i][0] == self.pos[j][0] or
                        self.pos[i][1] == self.pos[j][1]):
                    isolated = False
                    break
            if isolated:
                yield self.pos[i]

    def forced_point_index(self, cell, direction):
        """Search in the cell given for the point with the strongest force with
        respect to the given force."""
        if self.occupies(cell):
            points = list(self.points_in_cell(cell))
            if direction == DIR_EAST:
                return max(points)
            elif direction == DIR_NORTH:
                return max((self.patt[p], p) for p in points)[1]
            elif direction == DIR_WEST:
                return min(points)
            elif direction == DIR_SOUTH:
                return min((self.patt[p], p) for p in points)[1]
            else:
                raise ValueError("You're lost, no valid direction")

    def get_points_col(self, col):
        """Yields all points of the gridded permutation in the column col."""
        for i in range(len(self)):
            if self.pos[i][0] == col:
                yield (i, self.patt[i])

    def get_points_row(self, row):
        """Yields all points of the gridded permutation in the row."""
        for i in range(len(self)):
            if self.pos[i][1] == row:
                yield (i, self.patt[i])

    def get_points_below_row(self, row):
        """Yields all points of the gridded permutation below the row."""
        for i in range(len(self)):
            if self.pos[i][1] < row:
                yield (i, self.patt[i])

    def get_points_above_row(self, row):
        """Yields all points of the gridded permutation above the row."""
        for i in range(len(self)):
            if self.pos[i][1] > row:
                yield (i, self.patt[i])

    def get_points_left_col(self, col):
        """Yields all points of the gridded permutation left of column col."""
        for i in range(len(self)):
            if self.pos[i][0] < col:
                yield (i, self.patt[i])

    def get_points_right_col(self, col):
        """Yields all points of the gridded permutation right of column col."""
        for i in range(len(self)):
            if self.pos[i][0] > col:
                yield (i, self.patt[i])

    def get_bounding_box(self, cell):
        row = list(self.get_points_row(cell[1]))
        col = list(self.get_points_col(cell[0]))
        if not row:
            above = list(self.get_points_above_row(cell[1]))
            if not above:
                maxval = len(self)
            else:
                maxval = min(p[1] for p in above)
            below = list(self.get_points_below_row(cell[1]))
            if not below:
                minval = 0
            else:
                minval = max(p[1] for p in below) + 1
        else:
            maxval = max(p[1] for p in row) + 1
            minval = min(p[1] for p in row)
        if not col:
            right = list(self.get_points_right_col(cell[0]))
            if not right:
                maxdex = len(self)
            else:
                maxdex = min(p[0] for p in right)
            left = list(self.get_points_left_col(cell[0]))
            if not left:
                mindex = 0
            else:
                mindex = max(p[0] for p in left) + 1
        else:
            maxdex = max(p[0] for p in col) + 1
            mindex = min(p[0] for p in col)
        return (mindex, maxdex, minval, maxval)

    def point_translation(self, index, insert_point):
        """Given an index of a point in the gridded permutation and an insert
        location, compute the transformation of the point. The translation
        assumes that a new row and a new column is inserted in to the location.
        """
        x, y = self.pos[index]
        return (x + 2 if index >= insert_point[0] else x,
                y + 2 if self.patt[index] >= insert_point[1] else y)

    def stretch_gridding(self, insert_point):
        """Given an cell location, translate all the points of the gridded
        permutation as when a point is inserted into the cell."""
        newpos = [self.point_translation(p, insert_point)
                  for p in range(len(self))]
        return self.__class__(self.patt, newpos)

    def place_point(self, cell, direction, skip_redundant=False):
        """Places a point furthest to the direction 'direction' into a cell,
        returns the same gridded permutation if the gridded permutation does
        not span the rows or columns of the cell. Otherwise returns a list of
        new gridded permutations that are constructed from self by splitting it
        over the row and column of the cell, in every possible way.

        If the gridded permutation occupies the cell, the placed point will use
        one of the points of the gridded permutation that occupies the cell and
        construct a new gridded permutation which has that point removed.

        When generating the gridded permutation, any gridded permutation that
        contains the gridded permutation with removed point (placed point) is
        skipped if the `skip_redundant` is True.
        """
        # If the gridded permutation does not span the cell, the resulting list
        # of new obstructions would contain only the gridded permutation
        # itself.
        res = list()
        # If the gridded permutation contains a point in the cell (occupies)
        mindex, maxdex, minval, maxval = self.get_bounding_box(cell)
        forced_index = None
        if self.occupies(cell):
            if direction != DIR_NONE:
                forced_index = self.forced_point_index(cell, direction)
                forced_val = self.patt[forced_index]
                newpatt = Perm.to_standard(
                    self.patt[i] for i in range(len(self))
                    if i != forced_index)
                newposition = [
                    self.point_translation(p, (forced_index, forced_val))
                    for p in range(len(self)) if p != forced_index]
                res.append(self.__class__(newpatt, newposition))
            else:
                for index in self.points_in_cell(cell):
                    newpatt = Perm.to_standard(
                        self.patt[i] for i in range(len(self)) if i != index)
                    newposition = [
                        self.point_translation(p, (index, self.patt[index]))
                        for p in range(len(self)) if p != index]
                    res.append(self.__class__(newpatt, newposition))
        # Gridded permutation spans the cell, find the bounding box of all the
        # possible locations for the placed point in relation to the pattern.
            if direction == DIR_EAST:
                mindex = forced_index + 1
            elif direction == DIR_NORTH:
                minval = forced_val + 1
            elif direction == DIR_WEST:
                maxdex = forced_index
            elif direction == DIR_SOUTH:
                maxval = forced_val
        for i in range(mindex, maxdex + 1):
            if skip_redundant and forced_index is not None:
                if ((direction == DIR_SOUTH or direction == DIR_NORTH) and
                        (i == forced_index + 1 or i == forced_index)):
                    continue
            for j in range(minval, maxval + 1):
                if skip_redundant and forced_index is not None:
                    if ((direction == DIR_WEST or direction == DIR_EAST) and
                            (j == forced_val + 1 or j == forced_val)):
                        continue
                res.append(self.stretch_gridding((i, j)))

        return res

    def insert_point(self, cell):
        """Insert a new point into cell of the obstruction, such that the point
        is added to the underlying pattern with the position at the cell.
        Yields all obstruction where the point has been mixed into the points
        in the cell."""
        mindex, maxdex, minval, maxval = self.get_bounding_box(cell)
        for idx in range(mindex, maxdex + 1):
            for val in range(minval, maxval + 1):
                yield self.__class__(self.patt.insert(idx, val),
                                     self.pos[:idx] + (cell,) + self.pos[idx:])

    def _isolate_point(self, cell, row=True):
        """Isolates point in the given cell within the row or column, depending
        on the `row` flag."""
        pos = self.pos
        if self.occupies(cell):
            point = tuple(self.points_in_cell(cell))[0]
            if row:
                pos = [(x, y) if self.patt[i] < self.patt[point] else
                       (x, y + 2) if self.patt[i] > self.patt[point] else
                       (x, y + 1) for (i, (x, y)) in enumerate(pos)]
            else:
                pos = [(x, y) if i < point else
                       (x + 2, y) if i > point else
                       (x + 1, y) for (i, (x, y)) in enumerate(pos)]
            yield self.__class__(self.patt, pos)
        else:
            if row:
                rowpoints = sorted(self.get_points_row(cell[1]),
                                   key=lambda x: x[1])
                if not rowpoints:
                    yield self.__class__(self.patt,
                                         ((x, y) if y < cell[1] else (x, y + 2)
                                          for (x, y) in pos))
                    return
                for p in range(rowpoints[0][1], rowpoints[-1][1] + 2):
                    yield self.__class__(
                        self.patt,
                        ((x, y) if self.patt[j] < p else (x, y + 2)
                         for (j, (x, y)) in enumerate(pos)))
            else:
                colpoints = list(self.get_points_col(cell[0]))
                if not colpoints:
                    yield self.__class__(self.patt,
                                         ((x, y) if x < cell[0] else (x + 2, y)
                                          for (x, y) in pos))
                    return
                for i in range(colpoints[0][0], colpoints[-1][0] + 2):
                    yield self.__class__(self.patt,
                                         ((x, y) if j < i else (x + 2, y)
                                          for (j, (x, y)) in enumerate(pos)))

    def isolate_point_row(self, cell):
        """Isolates point in the given cell within the row."""
        return self._isolate_point(cell)

    def isolate_point_col(self, cell):
        """Isolates point in the given cell within the column."""
        return self._isolate_point(cell, False)

    def all_subperms(self):
        """Yields all gridded subpermutations."""
        for r in range(len(self)):
            for subidx in combinations(range(len(self)), r):
                yield self.__class__(
                    Perm.to_standard(self.patt[i] for i in subidx),
                    (self.pos[i] for i in subidx))

    def point_separation(self, cell, direction):
        """Performs point separation on cell and assumes point is placed in the
        cell of given direction of the two resulting cells."""
        points = list(self.points_in_cell(cell))
        if direction == DIR_WEST or direction == DIR_EAST:
            for p in self.pos:
                if p[0] == cell[0] and p[1] != cell[1]:
                    raise ValueError(("Obstruction occupies cell in the same "
                                      "column as point separation cell {}"
                                      ).format(cell))
            if not points:
                yield self.__class__(self.patt,
                                     [p if p[0] < cell[0] else (p[0] + 1, p[1])
                                      for p in self.pos])
                return
            lo, hi = points[0], points[-1] + 1
            if direction == DIR_WEST:
                hi = points[0] + 1
            else:
                lo = points[-1]
            for i in range(lo, hi + 1):
                yield self.__class__(self.patt,
                                     [self.pos[j] if j < i
                                      else (self.pos[j][0] + 1, self.pos[j][1])
                                      for j in range(len(self))])

        elif direction == DIR_NORTH or direction == DIR_SOUTH:
            for p in self.pos:
                if p[0] != cell[0] and p[1] == cell[1]:
                    raise ValueError(("Obstruction occupies cell in the same "
                                      "row as point separation cell {}"
                                      ).format(cell))
            if not points:
                yield self.__class__(self.patt,
                                     [p if p[1] < cell[1] else (p[0], p[1] + 1)
                                      for p in self.pos])
                return
            vals = sorted([self.patt[i] for i in points])
            lo, hi = vals[0], vals[-1] + 1
            if direction == DIR_SOUTH:
                hi = vals[0] + 1
            else:
                lo = vals[-1]
            for i in range(lo, hi + 1):
                yield self.__class__(self.patt,
                                     [self.pos[j] if self.patt[j] < i
                                      else (self.pos[j][0], self.pos[j][1] + 1)
                                      for j in range(len(self))])
        else:
            raise ValueError(("Invalid direction {} for point separation."
                              ).format(direction))

    def minimize(self, cell_mapping):
        return self.__class__(self.patt,
                              [cell_mapping(cell) for cell in self.pos])

    def is_point_perm(self):
        if len(self) == 1:
            return self.pos[0]
        return None

    def is_single_cell(self):
        if len(set(self.pos)) == 1:
            return self.pos[0]
        return None

    def is_empty(self):
        return not bool(self.patt)

    def is_interleaving(self):
        seen = []
        for cell in self.pos:
            for seen_cell in seen:
                if cell[0] == seen_cell[0]:
                    if cell[1] != seen_cell[1]:
                        return True
                else:
                    if cell[1] == seen_cell[1]:
                        return True
            seen.append(cell)
        return False

    def compress(self, patthash=None):
        """Compresses the gridded permutation into a list of integers. The
        first element in the list is the rank of the permutation, if the
        patthash dictionary is given the permutations value in the dictionary
        is used.  The rest is the list of positions flattened."""
        if patthash:
            array = [patthash[self.patt]]
        else:
            array = [self.patt.rank()]
        array.extend(chain.from_iterable(self.pos))
        return array

    @classmethod
    def decompress(cls, array, patthash=None):
        """Decompresses a list of integers in the form outputted by the
        compress method and constructns an Obstruction."""
        if patthash:
            patt = patthash[array[0]]
        else:
            patt = Perm.unrank(array[0])
        pos = zip(array[1::2], array[2::2])
        return cls(patt, pos)

    # Symmetries
    def reverse(self, transf):
        """ |
        Reverses the tiling within its boundary. Every cell and obstruction
        gets flipped over the vertical middle axis."""
        return self.__class__(self.patt.reverse(),
                              reversed(list(map(transf, self.pos))))

    def complement(self, transf):
        """ -
        Flip over the horizontal axis.  """
        return self.__class__(self.patt.complement(),
                              map(transf, self.pos))

    def inverse(self, transf):
        """ /
        Flip over the diagonal"""
        flipped = self.patt.inverse()
        pos = self.patt.inverse().apply(self.pos)
        return self.__class__(flipped, map(transf, pos))

    def antidiagonal(self, transf):
        """ \\
        Flip over the diagonal"""
        flipped = self.patt.flip_antidiagonal()
        pos = self.patt._rotate_left().apply(self.pos)
        return self.__class__(flipped, map(transf, pos))

    def rotate270(self, transf):
        """Rotate 270 degrees"""
        rotated = self.patt._rotate_left()
        pos = rotated.apply(self.pos)
        return self.__class__(rotated, map(transf, pos))

    def rotate180(self, transf):
        """Rotate 180 degrees"""
        return self.__class__(self.patt._rotate_180(),
                              reversed(list(map(transf, self.pos))))

    def rotate90(self, transf):
        """Rotate 90 degrees"""
        return self.__class__(self.patt._rotate_right(),
                              map(transf, self.patt.inverse().apply(self.pos)))

    def __len__(self):
        return len(self.patt)

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__,
                                   self.patt, self.pos)

    def __str__(self):
        return "<{} with {}>".format(self.__class__.__name__,
                                     str(self.patt))

    def __hash__(self):
        return hash(self.patt) ^ hash(self.pos)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.patt == other.patt and self.pos == other.pos

    def __lt__(self, other):
        return (self.patt, self.pos) < (other.patt, other.pos)

    def __contains__(self, other):
        return bool(list(other.occurrences_in(self)))
