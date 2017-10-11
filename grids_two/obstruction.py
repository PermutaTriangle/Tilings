from itertools import chain, combinations

from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NONE, DIR_NORTH, DIR_SOUTH, DIR_WEST


class Obstruction():
    def __init__(self, pattern, positions):
        # TODO: Write check to verify obstruction makes sense, that is, pattern
        # can be mapped on the positions given.

        if not isinstance(pattern, Perm):
            raise ValueError("Pattern should be a Perm")
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

            # Immutable set of cells which the obstruction spans.
            self._cells = frozenset(self.pos)
            self._rows = (min(x for x, _ in self.pos),
                          max(x for x, _ in self.pos))
            self._columns = (min(y for _, y in self.pos),
                             max(y for _, y in self.pos))

    @classmethod
    def single_cell(cls, pattern, cell):
        """Construct an obstruction where the cells are all located in a single
        cell."""
        return cls(pattern, [cell for _ in range(len(pattern))])

    @classmethod
    def empty_obstruction(cls):
        """Construct the empty obstruction."""
        return cls(Perm(tuple()), tuple())

    def spans_cell(self, cell):
        """Checks if the boundaries of the obstruction spans the cell."""
        return self.spans_column(cell[0]) and self.spans_row(cell[1])

    def spans_column(self, column):
        """Checks if the obstruction has a point in the given column."""
        return self._columns[0] <= column <= self._columns[1]

    def spans_row(self, row):
        """Checks if the obstruction has a point in the given row."""
        return self._rows[0] <= row <= self._rows[1]

    def occupies(self, cell):
        """Checks if the obstruction has a point in the given cell."""
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
        """Remove any points in the cell given and return a new obstruction."""
        remaining = [i for i in range(len(self)) if self.pos[i] not in cells]
        return Obstruction(Perm.to_standard(self.patt[i] for i in remaining),
                           (self.pos[i] for i in remaining))

    def points_in_cell(self, cell):
        """Yields the indices of the points in the cell given."""
        for i in range(len(self)):
            if self.pos[i] == cell:
                yield i

    def isolated_cells(self):
        """Yields the cells that contain only one point of the obstruction and
        are in their own row and column."""
        for i in range(len(self)):
            isolated = True
            for j in range(len(self)):
                if i == j:
                    continue
                if (self.pos[i][0] == self.pos[j][0]
                        or self.pos[i][1] == self.pos[j][1]):
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
        """Yields all points of the obstruction in the column col."""
        for i in range(len(self)):
            if self.pos[i][0] == col:
                yield (i, self.patt[i])

    def get_points_row(self, row):
        """Yields all points of the obstruction in the row."""
        for i in range(len(self)):
            if self.pos[i][1] == row:
                yield (i, self.patt[i])

    def get_points_below_row(self, row):
        """Yields all points of the obstruction below the row."""
        for i in range(len(self)):
            if self.pos[i][1] < row:
                yield (i, self.patt[i])

    def get_points_above_row(self, row):
        """Yields all points of the obstruction above the row."""
        for i in range(len(self)):
            if self.pos[i][1] > row:
                yield (i, self.patt[i])

    def get_points_left_col(self, col):
        """Yields all points of the obstruction left of column col."""
        for i in range(len(self)):
            if self.pos[i][0] < col:
                yield (i, self.patt[i])

    def get_points_right_col(self, col):
        """Yields all points of the obstruction right of column col."""
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
        """Given an index of a point in the obstruction and an insert location,
        compute the transformation of the point. The translation assumes that a
        new row and a new column is inserted in to the location.
        """
        x, y = self.pos[index]
        return (x + 2 if index >= insert_point[0] else x,
                y + 2 if self.patt[index] >= insert_point[1] else y)

    def stretch_obstruction(self, insert_point):
        newpos = [self.point_translation(p, insert_point)
                  for p in range(len(self))]
        return Obstruction(self.patt, newpos)

    def place_point(self, cell, direction, skip_redundant=False):
        """Places a point furthest to the direction 'direction' into a cell,
        returns the same obstruction if the obstruction does not span the rows
        or columns of the cell. Otherwise returns a list of new obstructions
        that are constructed from self by splitting it over the row and column
        of the cell, in every possible way.

        If the obstruction occupies the cell, the placed point will use one of
        the points of the obstruction that occupies the cell and construct a
        new obstruction which has that point removed.

        When generating the obstructions, any obstruction that contains the
        obstruction with removed point (placed point) is skipped if the
        `skip_redundant` is True.
        """
        # If the obstruction does not span the cell, the resulting list of new
        # obstructions would contain only the obstruction itself.
        res = list()
        # If the obstruction contains a point in the cell (occupies)
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
                res.append(Obstruction(newpatt, newposition))
            else:
                for index in self.points_in_cell(cell):
                    newpatt = Perm.to_standard(
                        self.patt[i] for i in range(len(self)) if i != index)
                    newposition = [
                        self.point_translation(p, (index, self.patt[index]))
                        for p in range(len(self)) if p != index]
                    res.append(Obstruction(newpatt, newposition))
        # Obstruction spans the cell, find the bounding box of all the possible
        # locations for the placed point in relation to the pattern.
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
                res.append(self.stretch_obstruction((i, j)))

        return res

    def insert_point(self, cell):
        """Insert a new point into cell of the obstruction, such that the point
        is added to the underlying pattern with the position at the cell.
        Yields all obstruction where the point has been mixed into the points
        in the cell."""
        mindex, maxdex, minval, maxval = self.get_bounding_box(cell)
        for idx in range(mindex, maxdex + 1):
            for val in range(minval, maxval + 1):
                yield Obstruction(self.patt.insert(idx, val),
                                  self.pos[:idx] + (cell,) + self.pos[idx:])

    def all_subobs(self):
        """Yields all subobstructions."""
        for r in range(len(self)):
            for subidx in combinations(range(len(self)), r):
                yield Obstruction(
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
                yield Obstruction(self.patt,
                                  [p if p[0] < cell[0] else (p[0] + 1, p[1])
                                   for p in self.pos])
                return
            lo, hi = points[0], points[-1] + 1
            if direction == DIR_WEST:
                hi = points[0] + 1
            else:
                lo = points[-1]
            for i in range(lo, hi + 1):
                yield Obstruction(self.patt,
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
                yield Obstruction(self.patt,
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
                yield Obstruction(self.patt,
                                  [self.pos[j] if self.patt[j] < i
                                   else (self.pos[j][0], self.pos[j][1] + 1)
                                   for j in range(len(self))])
        else:
            raise ValueError(("Invalid direction {} for point separation."
                              ).format(direction))

    def minimize(self, cell_mapping):
        return Obstruction(self.patt,
                           [cell_mapping(cell) for cell in self.pos])

    def is_point_obstr(self):
        if len(self) == 1:
            return self.pos[0]
        return None

    def is_single_cell(self):
        if len(set(self.pos)) == 1:
            return self.pos[0]
        return None

    def is_empty(self):
        return not bool(self.patt)

    def compress(self, patthash=None):
        """Compresses the obstruction into a list of integers. The first
        element in the list is the rank of the permutation, if the patthash
        dictionary is given the permutations value in the dictionary is used.
        The rest is the list of positions flattened."""
        if patthash:
            array = [patthash[self.patt]]
        else:
            array = [self.patt.rank()]
        array.extend(chain.from_iterable(self.pos))
        return array

    @classmethod
    def decompress(self, array, patthash=None):
        """Decompresses a list of integers in the form outputted by the
        compress method and constructns an Obstruction."""
        if patthash:
            patt = patthash[array[0]]
        else:
            patt = Perm.unrank(array[0])
        pos = zip(array[1::2], array[2::2])
        return Obstruction(patt, pos)

    # Symmetries
    def reverse(self, transf):
        """ |
        Reverses the tiling within its boundary. Every cell and obstruction
        gets flipped over the vertical middle axis."""
        return Obstruction(self.patt.reverse(),
                           reversed(map(transf, self.pos)))

    def complement(self, transf):
        """ -
        Flip over the horizontal axis.  """
        return Obstruction(self.patt.complement(),
                           map(transf, self.pos))

    def inverse(self, transf):
        """ /
        Flip over the diagonal"""
        flipped = self.patt.inverse()
        pos = self.patt.inverse().compose(flipped).apply(self.pos)
        return Obstruction(flipped, map(transf, pos))

    def antidiagonal(self, transf):
        """ \\
        Flip over the diagonal"""
        flipped = self.patt.flip_antidiagonal()
        pos = self.patt.inverse().compose(flipped).apply(self.pos)
        return Obstruction(flipped, map(transf, pos))

    def rotate270(self, transf):
        """Rotate 270 degrees"""
        rotated = self.patt._rotate_left()
        pos = self.patt.inverse().compose(rotated).apply(self.pos)
        return Obstruction(rotated, map(transf, pos))

    def rotate180(self, transf):
        """Rotate 180 degrees"""
        return Obstruction(self.patt._rotate_180(),
                           reversed(map(transf, self.pos)))

    def rotate90(self, transf):
        """Rotate 90 degrees"""
        return Obstruction(self.patt._rotate_right(),
                           map(transf, self.patt.inverse().apply(self.pos)))

    def __len__(self):
        return len(self.patt)

    def __repr__(self):
        return "<An obstruction with pattern {}>".format(str(self.patt))

    def __str__(self):
        return "Obstruction({}, {})".format(self.patt, self.pos)

    def __hash__(self):
        return hash(self.patt) ^ hash(self.pos)

    def __eq__(self, other):
        if not isinstance(other, Obstruction):
            return False
        return self.patt == other.patt and self.pos == other.pos

    def __lt__(self, other):
        return (self.patt, self.pos) < (other.patt, other.pos)

    def __contains__(self, other):
        return bool(list(other.occurrences_in(self)))
