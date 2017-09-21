from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_WEST, DIR_SOUTH  # , DIRS
# from permuta.interfaces import Patt


# def cell_translation(cell, row, col):
#     x = cell[0] + 1 if cell[0] > insert_loc[0] else cell[0]
#     y = cell[1] + 1 if cell[1] > insert_loc[1] else cell[1]
#     return (x, y)



class Obstruction():
    def __init__(self, pattern, positions):
        # TODO: Write check to verify obstruction makes sense, that is, pattern
        # can be mapped on the positions given.
        if len(pattern) != len(positions):
            raise ValueError("Pattern and position list have unequal lengths.")
        if not isinstance(pattern, Perm):
            raise ValueError("Pattern should be a Perm")
        # Pattern should be a Perm of course
        self.patt = pattern
        # Position is a tuple of (x, y) coordinates, where the ith (x, y)
        # corresponds to the i-th point in the pattern.
        self.pos = tuple(positions)
        # Immutable set of cells which the obstruction spans.
        self._cells = frozenset(self.pos)
        self._rows = (min(x for x, _ in self.pos),
                      max(x for x, _ in self.pos))
        self._columns = (min(y for _, y in self.pos),
                         max(y for _, y in self.pos))

    @classmethod
    def single_cell(cls, pattern, cell):
        return cls(pattern, [cell for _ in range(len(pattern))])

    def spans_cell(self, cell):
        return self.spans_row(cell[1]) and self.spans_column(cell[1])

    def spans_column(self, column):
        return self._columns[0] <= column <= self._columns[1]

    def spans_row(self, row):
        return self._rows[0] <= row <= self._rows[1]

    def occupies(self, cell):
        return cell in self._cells

    def occurrences_in(self, other):
        """Returns all occurrences of self in other."""
        for occ in self.patt.occurrences_in(other.pattern):
            if all(self.pos[ind] == other.positions[ind] for ind in occ):
                yield occ

    def occurs_in(self, other):
        return any(self.occurrences_in(other))

    def remove_row(self, row):
        raise NotImplementedError()

    def remove_column(self, row):
        raise NotImplementedError()

    def remove_rows(self, rows):
        raise NotImplementedError()

    def remove_columns(self, columns):
        raise NotImplementedError()

    def remove_rows_columns(self, rows, columns):
        raise NotImplementedError()

    def insert_row(self, row):
        raise NotImplementedError()

    def points_in_cell(self, cell):
        for i in range(len(self)):
            if self.pos[i] == cell:
                yield i

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
        return [(i, self.patt[i]) for i in range(len(self))
                if self.pos[i][0] == col]

    def get_points_row(self, row):
        return [(i, self.patt[i]) for i in range(len(self))
                if self.pos[i][1] == row]

    def get_points_below_row(self, row):
        return [(i, self.patt[i]) for i in range(len(self))
                if self.pos[i][1] < row]

    def get_points_above_row(self, row):
        return [(i, self.patt[i]) for i in range(len(self))
                if self.pos[i][1] > row]

    def get_points_left_col(self, col):
        return [(i, self.patt[i]) for i in range(len(self))
                if self.pos[i][0] < col]

    def get_points_right_col(self, col):
        return [(i, self.patt[i]) for i in range(len(self))
                if self.pos[i][0] > col]

    def get_bounding_box(self, cell):
        row = self.get_points_row(cell[1])
        col = self.get_points_col(cell[0])
        if not row:
            above = self.get_points_above_row(cell[1])
            if not above:
                maxval = len(self)
            else:
                maxval = min(p[1] for p in above)
            below = self.get_points_below_row(cell[1])
            if not below:
                minval = 0
            else:
                minval = max(p[1] for p in below) + 1
        else:
            maxval = max(p[1] for p in row) + 1
            minval = min(p[1] for p in row)
        if not col:
            right = self.get_points_right_col(cell[0])
            if not right:
                maxdex = len(self)
            else:
                maxdex = min(p[0] for p in right)
            left = self.get_points_left_col(cell[0])
            if not left:
                mindex = 0
            else:
                mindex = max(p[0] for p in left) + 1
        else:
            maxdex = max(p[0] for p in row) + 1
            mindex = min(p[0] for p in row)
        return (mindex, maxdex, minval, maxval)

    def point_translation(self, point, insert_point, direction):
        diffx = 1 if direction == DIR_EAST or direction == DIR_WEST else 2
        diffy = 1 if direction == DIR_NORTH or direction == DIR_SOUTH else 2
        newx, newy = self.pos[point]
        if point >= insert_point[0]:
            newx += diffx
        if self.patt[point] >= insert_point[1]:
            newy += diffy
        return (newx, newy)

    def stretch_obstruction(self, insert_point, direction):
        newpos = [self.point_translation(p, insert_point, direction)
                  for p in range(len(self))]
        return Obstruction(self.patt, newpos)

    def place_point(self, cell, direction):
        """Places a point furthest to the direction 'direction' into a cell,
        returns the same obstruction if the obstruction does not span the rows
        or columns of the cell. Otherwise returns a list of new obstructions
        that are constructed from self by splitting it over the row and column
        of the cell, in every possible way.  If the obstruction occupies the
        cell, the placed point will use one of the points of the obstruction
        that occupies the cell and construct a new obstruction which has that
        point removed.
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
                                       (forced_index, self.patt[forced_index]),
                                       direction)
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
            for j in range(minval, maxval + 1):
                res.append(self.stretch_obstruction((i, j), direction))

        return res

    def __len__(self):
        return len(self.patt)

    def __repr__(self):
        return "<An obstruction with pattern {}>".format(str(self.patt))

    def __str__(self):
        return "Obstruction({}, {})".format(self.patt, self.pos)
