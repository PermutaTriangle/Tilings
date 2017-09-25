from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST  # , DIRS


class Obstruction():
    def __init__(self, pattern, positions):
        # TODO: Write check to verify obstruction makes sense, that is, pattern
        # can be mapped on the positions given.

        if not isinstance(pattern, Perm):
            raise ValueError("Pattern should be a Perm")

        # Pattern should be a Perm of course
        self.patt = pattern
        # Position is a tuple of (x, y) coordinates, where the ith (x, y)
        # corresponds to the i-th point in the pattern.
        self.pos = tuple(positions)

        if len(self.patt) != len(self.pos):
            raise ValueError("Pattern and position list have unequal lengths.")

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
            print(occ)
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
        """Yields the cells that contain only one point of the obstruction."""
        for i in range(len(self)):
            isolated = True
            for j in range(len(self)):
                if i == j:
                    continue
                if (self.pos[i][0] == self.pos[j][0]
                        and self.pos[i][1] == self.pos[j][1]):
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

    def point_translation(self, point, insert_point):
        # TODO: TOOOOODOOOOOOOOOOOOOOOOOOO
        # diffx = 1 if direction == DIR_EAST or direction == DIR_WEST else 2
        # diffy = 1 if direction == DIR_NORTH or direction == DIR_SOUTH else 2
        diffx = 2
        diffy = 2
        newx, newy = self.pos[point]
        if point >= insert_point[0]:
            newx += diffx
        if self.patt[point] >= insert_point[1]:
            newy += diffy
        return (newx, newy)

    def stretch_obstruction(self, insert_point):
        newpos = [self.point_translation(p, insert_point)
                  for p in range(len(self))]
        return Obstruction(self.patt, newpos)

    def place_point(self, cell, direction, skip_redundant=True):
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
        forced_index = None
        if self.occupies(cell):
            forced_index = self.forced_point_index(cell, direction)
            newpatt = Perm.to_standard(
                self.patt[i] for i in range(len(self)) if i != forced_index)
            newposition = [
                self.point_translation(p,
                                       (forced_index, self.patt[forced_index]))
                for p in range(len(self)) if p != forced_index]
            res.append(Obstruction(newpatt, newposition))
        # Obstruction spans the cell, find the bounding box of all the possible
        # locations for the placed point in relation to the pattern.
        mindex, maxdex, minval, maxval = self.get_bounding_box(cell)
        if forced_index is not None:
            if direction == DIR_EAST:
                mindex = forced_index + 1
            elif direction == DIR_NORTH:
                minval = self.patt[forced_index] + 1
            elif direction == DIR_WEST:
                maxdex = forced_index
            elif direction == DIR_SOUTH:
                maxval = self.patt[forced_index]
        for i in range(mindex, maxdex + 1):
            if skip_redundant and forced_index is not None:
                if i == forced_index or i == forced_index + 1:
                    continue
            for j in range(minval, maxval + 1):
                res.append(self.stretch_obstruction((i, j)))

        return res

    def minimize(self, cell_mapping):
        return Obstruction(self.patt,
                           [cell_mapping(cell) for cell in self.pos])

    def point_cell(self):
        # TODO: Rename this
        if len(self) == 1:
            return self._pos[0]
        return None

    def is_single_cell(self):
        if len(set(self.pos)) == 1:
            return self.pos[0]
        return None

    def __len__(self):
        return len(self.patt)

    def __repr__(self):
        return "<An obstruction with pattern {}>".format(str(self.patt))

    def __str__(self):
        return "Obstruction({}, {})".format(self.patt, self.pos)

    def __hash__(self):
        return hash(self.patt) ^ hash(self.pos)

    def __eq__(self, other):
        return self.patt == other.patt and self.pos == other.pos

    def __lt__(self, other):
        return (self.patt, self.pos) < (other.patt, other.pos)

    def __contains__(self, other):
        return bool(other.occurrences_in(self))
