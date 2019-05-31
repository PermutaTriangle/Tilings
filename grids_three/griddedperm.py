import json
from itertools import chain, combinations

from permuta import Perm
from permuta.misc import (DIR_EAST, DIR_NONE, DIR_NORTH, DIR_SOUTH, DIR_WEST,
                          UnionFind)


class GriddedPerm():
    # TODO: Intersection of griddedperms
    def __init__(self, pattern, positions):
        # TODO: Write check to verify gridded permutation makes sense, that is,
        # pattern can be mapped on the positions given.

        if not isinstance(pattern, Perm):
            raise ValueError("Pattern should be a instance of permuta.Perm")
        if not len(pattern):
            self._patt = pattern
            self._pos = tuple(positions)
            self._cells = frozenset()
            self._rows = 1
            self._columns = 1
        else:
            # Pattern should be a Perm of course
            self._patt = pattern
            # Position is a tuple of (x, y) coordinates, where the ith (x, y)
            # corresponds to the i-th point in the pattern.
            self._pos = tuple(positions)

            if len(self._patt) != len(self._pos):
                raise ValueError(("Pattern and position list have unequal"
                                  "lengths."))

            # Immutable set of cells which the gridded permutation spans.
            self._cells = frozenset(self._pos)

    @classmethod
    def single_cell(cls, pattern, cell):
        """Construct a gridded permutation where the cells are all located in a
        single cell."""
        return cls(pattern, [cell for _ in range(len(pattern))])

    @classmethod
    def empty_perm(cls):
        """Construct the empty gridded permutation."""
        return cls(Perm(tuple()), tuple())

    def contradictory(self):
        """Checks if the points of the griddedperm contradict the permutation.

        Checks if for every 0 <= i < j < n
            patt[i] <= patt[j]
            if patt[i] < patt[j] then pos[i] <= pos[j]
            if patt[i] > patt[j] then pos[i] >= pos[j]
        """
        for i in range(len(self)):
            for j in range(i + 1, len(self)):
                if self.pos[i][0] > self.pos[j][0]:
                    return True
                if (self.patt[i] < self.patt[j] and
                        self.pos[i][1] > self.pos[j][1]):
                    return True
                if (self.patt[i] > self.patt[j] and
                        self.pos[i][1] < self.pos[j][1]):
                    return True
        return False

    def occupies(self, cell):
        """Checks if the gridded permutation has a point in the given cell."""
        return cell in self._cells

    def occurrences_in(self, other):
        """Returns all occurrences of self in other."""
        for occ in self._patt.occurrences_in(other.patt):
            if all(self._pos[i] == other.pos[occ[i]] for i in range(len(occ))):
                yield occ

    def occurs_in(self, other):
        """Checks if self occurs in other."""
        return any(self.occurrences_in(other))

    def remove_cells(self, cells):
        """Remove any points in the cell given and return a new gridded
        permutation."""
        remaining = [i for i in range(len(self)) if self._pos[i] not in cells]
        return self.__class__(
            Perm.to_standard(self._patt[i] for i in remaining),
            (self._pos[i] for i in remaining))

    def points_in_cell(self, cell):
        """Yields the indices of the points in the cell given."""
        for i in range(len(self)):
            if self._pos[i] == cell:
                yield i

    def isolated_cells(self):
        """Yields the cells that contain only one point of the gridded
        permutation and are in their own row and column."""
        for i in range(len(self)):
            isolated = True
            for j in range(len(self)):
                if i == j:
                    continue
                if (self._pos[i][0] == self._pos[j][0] or
                        self._pos[i][1] == self._pos[j][1]):
                    isolated = False
                    break
            if isolated:
                yield self._pos[i]

    def is_isolated(self, indices):
        """Checks if the cells at the indices do not share a row or column with
        any other cell in the gridded permutation."""
        for i in range(len(self)):
            if i in indices:
                continue
            if any((self._pos[i][0] == self._pos[j][0] or
                    self._pos[i][1] == self._pos[j][1]) for j in indices):
                return False
        return True

    def forced_point_index(self, cell, direction):
        """Search in the cell given for the point with the strongest force with
        respect to the given force."""
        if self.occupies(cell):
            points = list(self.points_in_cell(cell))
            if direction == DIR_EAST:
                return max(points)
            elif direction == DIR_NORTH:
                return max((self._patt[p], p) for p in points)[1]
            elif direction == DIR_WEST:
                return min(points)
            elif direction == DIR_SOUTH:
                return min((self._patt[p], p) for p in points)[1]
            else:
                raise ValueError("You're lost, no valid direction")

    def get_points_col(self, col):
        """Yields all points of the gridded permutation in the column col."""
        for i in range(len(self)):
            if self._pos[i][0] == col:
                yield (i, self._patt[i])

    def get_points_row(self, row):
        """Yields all points of the gridded permutation in the row."""
        for i in range(len(self)):
            if self._pos[i][1] == row:
                yield (i, self._patt[i])

    def get_points_below_row(self, row):
        """Yields all points of the gridded permutation below the row."""
        for i in range(len(self)):
            if self._pos[i][1] < row:
                yield (i, self._patt[i])

    def get_points_above_row(self, row):
        """Yields all points of the gridded permutation above the row."""
        for i in range(len(self)):
            if self._pos[i][1] > row:
                yield (i, self._patt[i])

    def get_points_left_col(self, col):
        """Yields all points of the gridded permutation left of column col."""
        for i in range(len(self)):
            if self._pos[i][0] < col:
                yield (i, self._patt[i])

    def get_subperm_left_col(self, col):
        """Returns the gridded subpermutation of points left of column col."""
        return self.__class__(
            Perm.to_standard(self.patt[i] for i in range(len(self))
                             if self.pos[i][0] < col),
            (self.pos[i] for i in range(len(self)) if self.pos[i][0] < col))

    def get_points_right_col(self, col):
        """Yields all points of the gridded permutation right of column col."""
        for i in range(len(self)):
            if self._pos[i][0] > col:
                yield (i, self._patt[i])

    def get_gridded_perm_in_cells(self, cells):
        """Returns the subgridded permutation of points in cells."""
        return self.__class__(
            Perm.to_standard(self.patt[i] for i in range(len(self))
                             if self.pos[i] in cells),
            (self.pos[i] for i in range(len(self)) if self.pos[i] in cells))

    def get_bounding_box(self, cell):
        """Determines the indices and values of the gridded permutation in
        which a point that is being inserted into the cell given."""
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
        x, y = self._pos[index]
        return (x + 2 if index >= insert_point[0] else x,
                y + 2 if self._patt[index] >= insert_point[1] else y)

    def partial_point_translation(self, index, insert_point, row=True):
        """Given an index of a point in the gridded permutation and an insert
        location, compute the transformation of the point. If row=True, the
        translation assumes that a new row is inserted. If row=False, it
        assumes a new column is inserted.
        """
        x, y = self._pos[index]
        return (x + 2 if not row and index >= insert_point[0] else x,
                y + 2 if row and self._patt[index] >= insert_point[1] else y)

    def stretch_gridding(self, insert_point):
        """Given an cell location, translate all the points of the gridded
        permutation as when a point is inserted into the cell."""
        newpos = [self.point_translation(p, insert_point)
                  for p in range(len(self))]
        return self.__class__(self._patt, newpos)

    def partial_stretch_gridding(self, insert_point, row=True):
        """Given an cell location, translate all the points of the gridded
        permutation as when a point is inserted into the cell. If row=True it
        is assumed a new row is added. If row=False it is assumed a new column
        is added."""
        newpos = [self.partial_point_translation(p, insert_point, row)
                  for p in range(len(self))]
        return self.__class__(self._patt, newpos)

    def insertion_encoding(self, cell):
        """Places the minimum point in a row in the given cellself.

        If the gridded perm occupies the cell then considers if the minimum in
        the row can use the points. It will also yield all of the gridded
        permutation split across the cells.

        An assumption is made that there are never cells in the same column.
        """
        def split_around_index(pos, index, skip=False):
            new_pos = []
            for ind, (x, y) in enumerate(pos):
                if skip and ind == index:
                    continue
                if ind >= index:
                    x += 2
                if y >= self.pos[index][1]:
                    y += 1
                new_pos.append((x, y))
            return new_pos

        res = []
        if self.occupies(cell):
            forced_index = self.forced_point_index(cell, DIR_SOUTH)
            if forced_index == min(self.get_points_row(cell[1]),
                                   key=lambda x: x[1])[0]:
                pos = split_around_index(self.pos, forced_index, skip=True)
                patt = Perm.to_standard(self.patt[i] for i in range(len(self))
                                        if i != forced_index)
                res.append(self.__class__(patt, pos))
            for ind in self.points_in_cell(cell):
                pos = split_around_index(self.pos, ind, skip=False)
                res.append(self.__class__(self.patt, pos))
        pos = []
        for (x, y) in self.pos:
            if x > cell[0]:
                x += 2
            if y >= cell[1]:
                y += 1
            pos.append((x, y))
        res.append(self.__class__(self.patt, pos))
        return res

    def place_point(self, cell, direction, partial=False, row=True):
        """Places a point furthest to the direction 'direction' into a cell,
        returns the same gridded permutation if the gridded permutation does
        not span the rows or columns of the cell. Otherwise returns a list of
        new gridded permutations that are constructed from self by splitting it
        over the row and column of the cell, in every possible way.

        If the gridded permutation occupies the cell, the placed point will use
        one of the points of the gridded permutation that occupies the cell and
        construct a new gridded permutation which has that point removed.

        If partial=True then it will partially place onto its own row.
        If partial=True and row=False it will partially place onto its own
        column.
        """
        # If the gridded permutation does not span the cell, the resulting list
        # of new obstructions would contain only the gridded permutation
        # itself.
        res = list()
        # If the gridded permutation contains a point in the cell (occupies)
        mindex, maxdex, minval, maxval = self.get_bounding_box(cell)
        if partial:
            # New indices of the point.
            point_cell = (cell[0] if row else cell[0] + 1,
                          cell[1] + 1 if row else cell[1])
            assert (direction == DIR_NONE or (row == (direction == DIR_NORTH or
                                                      direction == DIR_SOUTH)))
        forced_index = None
        if self.occupies(cell):
            if direction != DIR_NONE:
                forced_index = self.forced_point_index(cell, direction)
                forced_val = self._patt[forced_index]
                newpatt = Perm.to_standard(
                    self._patt[i] for i in range(len(self))
                    if partial or i != forced_index)
                if partial:
                    newposition = [
                        self.partial_point_translation(
                                        p, (forced_index, forced_val), row)
                        if p != forced_index else point_cell
                        for p in range(len(self))]
                else:
                    newposition = [
                        self.point_translation(p, (forced_index, forced_val))
                        for p in range(len(self)) if p != forced_index]
                res.append(self.__class__(newpatt, newposition))
            else:
                for index in self.points_in_cell(cell):
                    newpatt = Perm.to_standard(
                        self._patt[i] for i in range(len(self))
                        if partial or i != index)
                    if partial:
                        newposition = [
                            self.partial_point_translation(
                                        p, (index, self._patt[index]), row)
                            if p != index else point_cell
                            for p in range(len(self))]
                    else:
                        newposition = [
                            self.point_translation(
                                            p, (index, self._patt[index]))
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

        if partial:
            if row:
                maxdex = mindex
            else:
                maxval = minval

        for i in range(mindex, maxdex + 1):
            for j in range(minval, maxval + 1):
                if partial:
                    res.append(self.partial_stretch_gridding((i, j), row))
                else:
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
                yield self.__class__(
                    self._patt.insert(idx, val),
                    self._pos[:idx] + (cell,) + self._pos[idx:])

    def remove_point(self, index):
        """Remove the point at index from the gridded permutation."""
        patt = Perm.to_standard(self.patt[:index] + self.patt[index + 1:])
        pos = self.pos[:index] + self.pos[index + 1:]
        return self.__class__(patt, pos)

    def all_subperms(self, proper=True):
        """Yields all gridded subpermutations."""
        for r in range(len(self) if proper else len(self) + 1):
            for subidx in combinations(range(len(self)), r):
                yield self.__class__(
                    Perm.to_standard(self._patt[i] for i in subidx),
                    (self._pos[i] for i in subidx))

    def minimize(self, cell_mapping):
        """Map the coordinates to a new list of coordinates according to the
        cell_mapping given."""
        return self.__class__(self._patt,
                              [cell_mapping(cell) for cell in self._pos])

    def is_point_perm(self):
        """Checks if the gridded permutation is of length 1."""
        if len(self) == 1:
            return self._pos[0]
        return None

    def is_localized(self):
        """Check if the gridded permutation occupies only a single cell."""
        return self.is_single_cell()

    def is_single_cell(self):
        """Check if the gridded permutation occupies only a single cell."""
        if len(set(self._pos)) == 1:
            return self._pos[0]
        return None

    def is_single_row(self):
        """Check if the gridded permutation occupies only a single row."""
        if len(set(y for (x, y) in self._pos)) == 1:
            return True
        return False

    def is_empty(self):
        """Check if the gridded permutation is the gridded permutation."""
        return not bool(self._patt)

    def is_interleaving(self):
        """Check if the gridded permutation occupies two cells that are in the
        same row or column."""
        seen = []
        for cell in self._pos:
            for seen_cell in seen:
                if cell[0] == seen_cell[0]:
                    if cell[1] != seen_cell[1]:
                        return True
                else:
                    if cell[1] == seen_cell[1]:
                        return True
            seen.append(cell)
        return False

    def factors(self):
        """Return a list containing the factors of a gridded permutation.
        A factor is a sub gridded permutation that is isolated on its own rows
        and columns."""
        uf = UnionFind(len(self.pos))
        for i in range(len(self.pos)):
            for j in range(i+1, len(self.pos)):
                c1, c2 = self.pos[i], self.pos[j]
                if c1[0] == c2[0] or c1[1] == c2[1]:
                    uf.unite(i, j)
        # Collect the connected factors of the cells
        all_factors = {}
        for i, cell in enumerate(self.pos):
            x = uf.find(i)
            if x in all_factors:
                all_factors[x].append(cell)
            else:
                all_factors[x] = [cell]
        factor_cells = list(set(cells) for cells in all_factors.values())
        return [self.get_gridded_perm_in_cells(comp)
                for comp in factor_cells]

    def compress(self):
        """Compresses the gridded permutation into a list of integers. It starts
        with a list of the values in the permutation. The rest is the list of
        positions flattened."""
        array = [p for p in self._patt]
        array.extend(chain.from_iterable(self._pos))
        return array

    @classmethod
    def decompress(cls, array):
        """Decompresses a list of integers in the form outputted by the
        compress method and constructs an Obstruction."""
        n = len(array)
        patt = Perm(array[i] for i in range(n//3))
        pos = zip(array[n//3::2], array[n//3+1::2])
        return cls(patt, pos)

    # Symmetries
    def reverse(self, transf):
        """ |
        Reverses the tiling within its boundary. Every cell and obstruction
        gets flipped over the vertical middle axis."""
        return self.__class__(self._patt.reverse(),
                              reversed(list(map(transf, self._pos))))

    def complement(self, transf):
        """ -
        Flip over the horizontal axis.  """
        return self.__class__(self._patt.complement(),
                              map(transf, self._pos))

    def inverse(self, transf):
        """ /
        Flip over the diagonal"""
        flipped = self._patt.inverse()
        pos = self._patt.inverse().apply(self._pos)
        return self.__class__(flipped, map(transf, pos))

    def antidiagonal(self, transf):
        """ \\
        Flip over the diagonal"""
        flipped = self._patt.flip_antidiagonal()
        pos = self._patt._rotate_left().apply(self._pos)
        return self.__class__(flipped, map(transf, pos))

    def rotate270(self, transf):
        """Rotate 270 degrees"""
        rotated = self._patt._rotate_left()
        pos = rotated.apply(self._pos)
        return self.__class__(rotated, map(transf, pos))

    def rotate180(self, transf):
        """Rotate 180 degrees"""
        return self.__class__(self._patt._rotate_180(),
                              reversed(list(map(transf, self._pos))))

    def rotate90(self, transf):
        """Rotate 90 degrees"""
        return self.__class__(
            self._patt._rotate_right(),
            map(transf, self._patt.inverse().apply(self._pos)))

    def to_jsonable(self):
        """Returns a dictionary object which is JSON serializable representing
        a GriddedPerm."""
        output = dict()
        output['patt'] = self._patt
        output['pos'] = self._pos
        return output

    @classmethod
    def from_json(cls, jsonstr):
        """Returns a GriddedPerm object from JSON string."""
        jsondict = json.loads(jsonstr)
        return cls.from_dict(jsondict)

    @classmethod
    def from_dict(cls, jsondict):
        """Returns a GriddedPerm object from a dictionary loaded from a JSON
        serialized GriddedPerm object."""
        return cls(Perm(jsondict['patt']), map(tuple, jsondict['pos']))

    @property
    def patt(self):
        return self._patt

    @property
    def pos(self):
        return self._pos

    def __len__(self):
        return len(self._patt)

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__,
                                   repr(self._patt), self._pos)

    def __str__(self):
        return "{}: {}".format(str(self._patt), ", ".join(str(c)
                                                          for c in self.pos))

    def __hash__(self):
        return hash(self._patt) ^ hash(self._pos)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self._patt == other.patt and self._pos == other.pos

    def __lt__(self, other):
        return (self._patt, self._pos) < (other.patt, other.pos)

    def __contains__(self, other):
        try:
            next(other.occurrences_in(self))
            return True
        except StopIteration:
            return False
