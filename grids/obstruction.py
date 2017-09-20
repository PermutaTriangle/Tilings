from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_WEST, DIR_SOUTH, DIR_NONE, DIRS
# from permuta.interfaces import Patt


# def cell_translation(cell, row, col):
    # x = cell[0] + 1 if cell[0] > insert_loc[0] else cell[0]
    # y = cell[1] + 1 if cell[1] > insert_loc[1] else cell[1]
    # return (x, y)

def point_translation(self, insert_point, 


class Obstruction():
    def __init__(self, pattern, positions):
        if len(pattern) != len(positions):
            raise ValueError("Pattern and position list have unequal lengths.")
        if not isinstance(pattern, Perm):
            raise ValueError("Pattern should be a Perm")
        # Pattern should be a Perm of course
        self.pattern = pattern
        # Position is a tuple of (x, y) coordinates, where the ith (x, y)
        # corresponds to the i-th point in the pattern.
        self.positions = tuple(positions)
        # Immutable set of cells which the obstruction spans.
        self._cells = frozenset(self.positions)
        self._rows = (min(x for x, _ in self.positions),
                      max(x for x, _ in self.positions))
        self._columns = (min(y for _, y in self.positions),
                         max(y for _, y in self.positions))
        # self._columns = frozenset(y for _, y in positions)

    @classmethod
    def single_cell(cls, pattern, cell):
        return cls(pattern, [cell for _ in range(len(pattern))])

    def spans_cell(self, cell):
        return self.spans_row(cell[1]) and self.spans_column(cell[1])

    def spans_column(self, column):
        return self._columns[0] <= column <= self._columns[1]

    def spans_rows(self, row):
        return self._rows[0] <= row <= self._rows[1]

    def occupies(self, cell):
        return cell in self._cells

    def occurrences_in(self, other):
        """Returns all occurrences of self in other."""
        for occ in self.pattern.occurrences_in(other.pattern):
            if all(self.positions[ind] == other.positions[ind] for ind in occ):
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
        for i in range(len(self.pattern)):
            if self.positions[i] == cell:
                yield i

    def find_forced_point(self, cell, direction):
        if self.occupies(cell):
            points = list(self.points_in_cell(cell))
            if direction == DIR_EAST:
                return max(points)
            elif direction == DIR_NORTH:
                return max((self.pattern[p], p) for p in points)[1]
            elif direction == DIR_WEST:
                return min((self.pattern[p], p) for p in points)[1]
            elif direction == DIR_SOUTH:
                return min(points)
            else:
                raise ValueError("You're lost, no valid direction")

    def place_point(self, cell, direction):
        """Places a point furthest to the direction 'direction' into a cell,
        returns the same obstruction if the obstruction does not span the rows
        or columns of the cell. Otherwise returns a new obstruction that has
        been split in all possible ways. If the obstruction spans the cell, the
        newly split obstruction will contain the split obstructions where one
        of the point has been used."""
        # If the obstruction does not span the cell
        if not self.spans_cell(cell):
            return self
        if self.occupies(cell):
            forced_point = self.find_forced_point(cell, direction)
            newpatt = Perm.to_standard(
                self.pattern[i] for i in range(len(self)) if i != forced_point)
            newposition = (
                [(x + 2, y) for (i, (x, y)) in enumerate(self.positions)
                 if i > forced_point] +
                [(x, y) for (i, (x, y)) in enumerate(self.positions)
                 if i < forced_point])


        # raise NotImplementedError()

    def __len__(self):
        return len(self.pattern)
