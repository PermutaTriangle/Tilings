import json
from array import array
from collections import Counter, defaultdict
from functools import partial, reduce
from itertools import chain
from operator import add, mul

import sympy

from comb_spec_searcher import CombinatorialClass
from permuta import Perm, PermSet
from permuta.misc import UnionFind

from .db_conf import check_database
from .griddedperm import GriddedPerm
from .misc import intersection_reduce, map_cell, union_reduce
from .obstruction import Obstruction
from .requirement import Requirement

__all__ = ("Tiling")


class Tiling(CombinatorialClass):
    # TODO:
    #   - Intersection of requirements
    """Tiling class.

    Zero-indexed coordinates/cells from bottom left corner where the (x, y)
    cell is the cell in the x-th column and y-th row.

    Tilings store the obstructions and requirements but also caches the empty
    cells and the active cells.
    """

    def __init__(self, obstructions=list(), requirements=list(),
                 remove_empty=True, derive_empty=True, minimize=True,
                 sorted_input=False):
        if sorted_input:
            # Set of obstructions
            self._obstructions = tuple(obstructions)
            # Set of requirement lists
            self._requirements = tuple(tuple(r) for r in requirements)
        else:
            # Set of obstructions
            self._obstructions = tuple(sorted(obstructions))
            # Set of requirement lists
            self._requirements = Tiling.sort_requirements(requirements)

        # Minimize the set of obstructions and the set of requirement lists
        if minimize:
            self._minimize_griddedperms()

        if not any(ob.is_empty() for ob in self.obstructions):
            # If assuming the non-active cells are empty, then add the
            # obstructions
            if derive_empty:
                self._fill_empty()

            # Remove empty rows and empty columns
            if remove_empty:
                self._minimize_tiling()

    def _fill_empty(self):
        add = []
        (i, j) = self.dimensions
        for x in range(i):
            for y in range(j):
                if ((x, y) not in self.active_cells and
                        (x, y) not in self.empty_cells):
                    add.append(Obstruction.single_cell(Perm((0,)), (x, y)))
        self._obstructions = tuple(sorted(tuple(add) + self._obstructions))

    def _minimize_griddedperms(self):
        """Minimizes the set of obstructions and the set of requirement lists.
        The set of obstructions are first reduced to a minimal set. The
        requirements that contain any obstructions are removed from their
        respective lists. If any requirement list is empty, then the tiling is
        empty.
        """
        while True:
            # Minimize the set of obstructions
            minimized_obs = self._minimal_obs()
            # Minimize the set of requiriments
            minimized_obs, minimized_reqs = self._minimal_reqs(minimized_obs)
            if (self._obstructions == minimized_obs and
                    self._requirements == minimized_reqs):
                break
            else:
                self._obstructions = minimized_obs
                self._requirements = minimized_reqs

    def _minimize_tiling(self):
        # Produce the mapping between the two tilings
        if not self.active_cells:
            self._obstructions = (Obstruction.single_cell(Perm((0,)), (0, 0)),)
            self._requirements = tuple()
            self._dimensions = (1, 1)
            return
        col_mapping, row_mapping = self._minimize_mapping()
        cell_map = partial(map_cell, col_mapping, row_mapping)

        # For tracking regions.
        self.forward_map = {(k_x, k_y): (v_x, v_y)
                            for k_x, v_x in col_mapping.items()
                            for k_y, v_y in row_mapping.items()}
        new_obs = []
        for ob in self._obstructions:
            cell = ob.is_point_obstr()
            if cell is None or (cell[0] in col_mapping and
                                cell[1] in row_mapping):
                new_obs.append(ob.minimize(cell_map))
        self._obstructions = tuple(new_obs)
        self._requirements = tuple(tuple(req.minimize(cell_map)
                                         for req in reqlist)
                                   for reqlist in self._requirements)
        self._dimensions = (max(col_mapping.values()) + 1,
                            max(row_mapping.values()) + 1)

    def _minimize_mapping(self):
        """Returns a pair of dictionaries, that map rows/columns to an
        equivalent set of rows/columns where empty ones have been removed. """
        active_cells = self.active_cells
        assert active_cells

        col_set, row_set = map(set, zip(*active_cells))

        col_list, row_list = sorted(col_set), sorted(row_set)
        col_mapping = {x: actual for actual, x in enumerate(col_list)}
        row_mapping = {y: actual for actual, y in enumerate(row_list)}
        return (col_mapping, row_mapping)

    def _clean_isolated(self, obstruction):
        """Remove the isolated factors that are implied by requirements
        from all obstructions."""
        for req_list in self._requirements:
            for factor in obstruction.factors():
                if all(factor in req for req in req_list):
                    obstruction = obstruction.remove_cells(factor.pos)
        return obstruction

    def _minimal_obs(self):
        """Returns a new list of minimal obstructions from the obstruction set
        of self. Every obstruction in the new list will have any isolated
        points in positive cells removed."""
        clean_ones = sorted(self._clean_isolated(co)
                            for co in self._obstructions)
        cleanobs = list()
        for cleanob in clean_ones:
            add = True
            for co in cleanobs:
                if co in cleanob:
                    add = False
                    break
            if add:
                cleanobs.append(cleanob)
        return tuple(cleanobs)

    def _minimal_reqs(self, obstructions):
        """Returns a new set of minimal lists of requirements from the
        requirement set of self, and a list of further reduced obstructions."""
        # TODO:
        #   - Factor requirements
        #   - Remove intersections of requirements from obstructions
        cleanreqs = list()
        for reqs in self._requirements:
            # If any gridded permutation in list is empty then you vacuously
            # contain this requirement
            if not all(reqs):
                continue
            redundant = set()
            for i in range(len(reqs)):
                for j in range(i+1, len(reqs)):
                    if j not in redundant:
                        if reqs[i] in reqs[j]:
                            redundant.add(j)
                if i not in redundant:
                    if any(ob in reqs[i] for ob in obstructions):
                        redundant.add(i)
            cleanreq = [req for i, req in enumerate(reqs)
                        if i not in redundant]
            # If cleanreq is empty, then can not contain this requirement so
            # the tiling is empty.
            if not cleanreq:
                return (Obstruction.empty_perm(),), tuple()
            cleanreqs.append(cleanreq)

        ind_to_remove = set()
        for i, reqs in enumerate(cleanreqs):
            if i not in ind_to_remove:
                for j, reqs2 in enumerate(cleanreqs):
                    if i != j and j not in ind_to_remove:
                        if all(any(r2 in r1 for r2 in reqs2) for r1 in reqs):
                            ind_to_remove.add(j)

        return (obstructions,
                Tiling.sort_requirements(reqs
                                         for i, reqs in enumerate(cleanreqs)
                                         if i not in ind_to_remove))

    # Compression

    def compress(self, patthash=None):
        """Compresses the tiling by flattening the sets of cells into lists of
        integers which are concatenated together, every list preceeded by its
        size. The obstructions are compressed and concatenated to the list, as
        are the requirement lists."""
        result = []
        result.append(len(self.obstructions))
        result.extend(chain.from_iterable(ob.compress(patthash)
                                          for ob in self.obstructions))
        result.append(len(self.requirements))
        for reqlist in self.requirements:
            result.append(len(reqlist))
            result.extend(chain.from_iterable(req.compress(patthash)
                                              for req in reqlist))
        res = array('H', result)
        return res.tobytes()

    @classmethod
    def decompress(cls, arrbytes, patts=None, remove_empty=False,
                   derive_empty=False, minimize=False, sorted_input=True):
        """Given a compressed tiling in the form of an 2-byte array, decompress
        it and return a tiling."""
        arr = array('H', arrbytes)
        offset = 1
        nobs = arr[offset - 1]
        obstructions = []
        for _ in range(nobs):
            if patts:
                patt = patts[arr[offset]]
            else:
                patt = Perm.unrank(arr[offset])
            obstructions.append(Obstruction.decompress(
                arr[offset:offset + 2*(len(patt)) + 1], patts))
            offset += 2 * len(patt) + 1

        nreqs = arr[offset]
        offset += 1
        requirements = []
        for _ in range(nreqs):
            reqlistlen = arr[offset]
            offset += 1
            reqlist = []
            for _ in range(reqlistlen):
                if patts:
                    patt = patts[arr[offset]]
                else:
                    patt = Perm.unrank(arr[offset])
                reqlist.append(Requirement.decompress(
                    arr[offset:offset + 2*(len(patt)) + 1], patts))
                offset += 2 * len(patt) + 1
            requirements.append(reqlist)

        return cls(obstructions=obstructions, requirements=requirements,
                   remove_empty=remove_empty, derive_empty=derive_empty,
                   minimize=minimize, sorted_input=sorted_input)

    @classmethod
    def from_string(cls, string):
        """Return a 1x1 tiling from string of form 'p1_p2'"""
        basis = [Obstruction.single_cell(Perm.to_standard(p), (0, 0))
                 for p in string.split('_')]
        return cls(obstructions=basis)

    # JSON methods
    def to_jsonable(self):
        """Returns a dictionary object which is JSON serializable which
        represents a Tiling."""
        output = dict()
        output['obstructions'] = list(map(lambda x: x.to_jsonable(),
                                      self.obstructions))
        output['requirements'] = list(map(lambda x:
                                          list(map(lambda y: y.to_jsonable(),
                                                   x)),
                                      self.requirements))
        return output

    @classmethod
    def from_json(cls, jsonstr):
        """Returns a Tiling object from JSON string."""
        jsondict = json.loads(jsonstr)
        return cls.from_dict(jsondict)

    @classmethod
    def from_dict(cls, jsondict):
        """Returns a Tiling object from a dictionary loaded from a JSON
        serialized Tiling object."""
        obstructions = map(lambda x: Obstruction.from_dict(x),
                           jsondict['obstructions'])
        requirements = map(lambda x:
                           map(lambda y: Requirement.from_dict(y), x),
                           jsondict['requirements'])
        return cls(obstructions=obstructions,
                   requirements=requirements)

    # Cell methods

    def cell_within_bounds(self, cell):
        """Checks if a cell is within the bounds of the tiling."""
        (i, j) = self.dimensions
        return cell[0] >= 0 and cell[0] < i and cell[1] >= 0 and cell[1] < j

    def empty_cell(self, cell):
        """Empties a cell in the tiling by adding a point obstruction into the
        cell.
        """
        if not self.cell_within_bounds(cell):
            raise ValueError(
                "Cell {} is not within the bounds of the tiling.".format(cell))
        return self.add_single_cell_obstruction(Perm((0,)), cell)

    def insert_cell(self, cell):
        """Performs 'cell insertion', adds a point requirement into the given
        cell. Cell should be active.

        TODO: Given a requirement list that contains the requirement
            Requirement(Perm((0, 1)), [(x_0, y_0), (x_1, y_1))
        and a requirement that does not occupy (x_0, y_0), consider what
        happens to this requirement when cell insertion is performed on (x_0,
        y_0). This is a case of a subrequirement contained in every requirement
        of some list, which then another requirement in another list contains.
        Since the first requirement list guarantees that the subrequirement is
        placed, the second requirement could remove the subrequirement from
        itself.
        """
        if not self.cell_within_bounds(cell):
            raise ValueError(
                "Cell {} is not within the bounds of the tiling.".format(cell))
        return self.add_single_cell_requirement(Perm((0,)), cell)

    def add_obstruction(self, patt, pos):
        """Returns a new tiling with the obstruction of the pattern
        patt with positionp pos."""
        return Tiling(
            self._obstructions + (Obstruction(patt, pos),),
            self._requirements)

    def add_requirement(self, patt, pos):
        """Returns a new tiling with the requirement of the pattern
        patt with position pos."""
        return Tiling(
            self._obstructions,
            self._requirements + ((Requirement(patt, pos),),))

    def add_single_cell_obstruction(self, patt, cell):
        """Returns a new tiling with the single cell obstruction of the pattern
        patt in the given cell."""
        return Tiling(
            self._obstructions + (Obstruction.single_cell(patt, cell),),
            self._requirements)

    def add_single_cell_requirement(self, patt, cell):
        """Returns a new tiling with the single cell requirement of the pattern
        patt in the given cell."""
        return Tiling(
            self._obstructions,
            self._requirements + ([Requirement.single_cell(patt, cell)],))

    def fully_isolated(self):
        """Check if all cells are isolated on their rows and columns."""
        seen_row = []
        seen_col = []
        for i, j in self.active_cells:
            if i in seen_col or j in seen_row:
                return False
            seen_col.append(i)
            seen_row.append(j)
        return True

    def only_positive_in_row_and_col(self, cell):
        """Check if the cell is the only positive cell in row and column."""
        return (self.only_positive_in_row(cell) and
                self.only_positive_in_col(cell))

    def only_positive_in_row(self, cell):
        """Check if the cell is the only positive cell in row."""
        if cell not in self.positive_cells:
            return False
        inrow = sum(1 for (x, y) in self.positive_cells
                    if y == cell[1])
        return inrow == 1

    def only_positive_in_col(self, cell):
        """Check if the cell is the only positive cell in column."""
        if cell not in self.positive_cells:
            return False
        incol = sum(1 for (x, y) in self.positive_cells
                    if x == cell[0])
        return incol == 1

    def only_cell_in_col(self, cell):
        """Checks if the cell is the only active cell in the column."""
        return sum(1 for (x, y) in self.active_cells if x == cell[0]) == 1

    def only_cell_in_row(self, cell):
        """Checks if the cell is the only active cell in the row."""
        return sum(1 for (x, y) in self.active_cells if y == cell[1]) == 1

    def cells_in_row(self, row):
        """Return all active cells in row."""
        return frozenset((x, y) for (x, y) in self.active_cells if y == row)

    def cells_in_col(self, col):
        """Return all active cells in column."""
        return frozenset((x, y) for (x, y) in self.active_cells if x == col)

    def cell_basis(self):
        """Returns a dictionary from cells to basis.

        The basis for each cell is a tuple of two lists of permutations.  The
        first list contains the patterns of the obstructions localized in the
        cell and the second contains the intersections of requirement lists
        that are localized in the cell.
        """
        obdict = defaultdict(list)
        reqdict = defaultdict(list)
        for ob in self.obstructions:
            if ob.is_localized():
                obdict[ob.is_localized()].append(ob.patt)
        for req_list in self.requirements:
            if len(req_list) == 1:
                req = req_list[0]
                if req.is_localized():
                    reqdict[req.is_localized()].append(req.patt)
        # TODO: Implement this for the intersection of requirements
        resdict = defaultdict(lambda: ([], []))
        for cell in chain(obdict.keys(), reqdict.keys()):
            resdict[cell] = (obdict[cell], reqdict[cell])
        return resdict

    def cell_graph(self):
        """
        Return the set of edges in the cell graph of the tiling.
        """
        edges = list()
        cells = sorted(self.active_cells)
        for c1, c2 in zip(cells[:-1], cells[1:]):
            if c1[0] == c2[0]:
                edges.append((c1, c2))
        cells = sorted(self.active_cells, key=lambda x: (x[1], x[0]))
        for c1, c2 in zip(cells[:-1], cells[1:]):
            if c1[1] == c2[1]:
                edges.append((c1, c2))
        return edges

    @staticmethod
    def sort_requirements(requirements):
        return tuple(sorted(tuple(sorted(set(reqlist)))
                            for reqlist in requirements))

    # Symmetries
    def _transform(self, transf, gptransf):
        """ Transforms the tiling according to the two transformation functions
        given. The first transf is mapping of cells while gptransf is a
        transformation of GriddedPerm that calls some internal method.
        """
        return Tiling(obstructions=(gptransf(ob) for ob in self.obstructions),
                      requirements=([gptransf(req) for req in reqlist]
                                    for reqlist in self.requirements))

    def reverse(self):
        """ |
        Reverses the tiling within its boundary. Every cell and obstruction
        gets flipped over the vertical middle axis."""
        def reverse_cell(cell):
            return (self.dimensions[0] - cell[0] - 1, cell[1])
        return self._transform(
            reverse_cell,
            lambda gp: gp.reverse(reverse_cell))

    def complement(self):
        """ -
        Flip over the horizontal axis.  """
        def complement_cell(cell):
            return (cell[0], self.dimensions[1] - cell[1] - 1)
        return self._transform(
            complement_cell,
            lambda gp: gp.complement(complement_cell))

    def inverse(self):
        """ /
        Flip over the diagonal"""
        def inverse_cell(cell):
            return (cell[1], cell[0])
        return self._transform(
            inverse_cell,
            lambda gp: gp.inverse(inverse_cell))

    def antidiagonal(self):
        """ \\
        Flip over the anti-diagonal"""
        def antidiagonal_cell(cell):
            return (self.dimensions[1] - cell[1] - 1,
                    self.dimensions[0] - cell[0] - 1)
        return self._transform(
            antidiagonal_cell,
            lambda gp: gp.antidiagonal(antidiagonal_cell))

    def rotate270(self):
        """Rotate 270 degrees"""
        def rotate270_cell(cell):
            return (self.dimensions[1] - cell[1] - 1,
                    cell[0])
        return self._transform(
            rotate270_cell,
            lambda gp: gp.rotate270(rotate270_cell))

    def rotate180(self):
        """Rotate 180 degrees"""
        def rotate180_cell(cell):
            return (self.dimensions[0] - cell[0] - 1,
                    self.dimensions[1] - cell[1] - 1)
        return self._transform(
            rotate180_cell,
            lambda gp: gp.rotate180(rotate180_cell))

    def rotate90(self):
        """Rotate 90 degrees"""
        def rotate90_cell(cell):
            return (cell[1],
                    self.dimensions[0] - cell[0] - 1)
        return self._transform(
            rotate90_cell,
            lambda gp: gp.rotate90(rotate90_cell))

    #
    # Properties and getters
    #

    def maximum_length_of_minimum_gridded_perm(self):
        """Returns the maximum length of the minimum gridded permutation that
        can be gridded on the tiling.
        """
        return sum(max(map(len, reqs)) for reqs in self.requirements)

    def is_empty(self):
        """Checks if the tiling is empty.

        Tiling is empty if it has been inferred to be contradictory due to
        contradicting requirements and obstructions or no gridded permutation
        can be gridded on the tiling.
        """
        if any(ob.is_empty() for ob in self.obstructions):
            return True
        if len(self.requirements) <= 1:
            return False
        try:
            next(self.gridded_perms())
            return False
        except StopIteration:
            return True

    def is_finite(self):
        """Returns True if all active cells have finite basis."""
        increasing = set()
        decreasing = set()
        for ob in self.obstructions:
            if ob.is_single_cell():
                if ob.patt.is_increasing():
                    increasing.add(ob.pos[0])
                if ob.patt.is_decreasing():
                    decreasing.add(ob.pos[0])
        return all(cell in increasing and cell in decreasing
                   for cell in self.active_cells)

    def objects_of_length(self, length):
        yield from self.gridded_perms_of_length(length)

    def gridded_perms_of_length(self, length):
        for gp in self.gridded_perms(maxlen=length):
            if len(gp) == length:
                yield gp

    def gridded_perms(self, maxlen=None):
        """Returns all gridded permutations griddable on the tiling.

        The gridded permutations are up to length of the longest minimum
        gridded permutations that is griddable on the tiling.
        """
        if maxlen is None:
            maxlen = max(self.maximum_length_of_minimum_gridded_perm(), 1)

        def insert_next_point(gp, col):
            for cell in self.active_cells:
                if cell[0] != col:
                    continue
                _, _, minval, maxval = gp.get_bounding_box(cell)
                for val in range(minval, maxval + 1):
                    yield gp.__class__(
                        gp._patt.insert(new_element=val), gp._pos + (cell,))

        def can_satisfy(gp, col, req):
            return req.get_subperm_left_col(col) in gp

        def can_satisfy_all(gp, col, reqs):
            return all(any(can_satisfy(gp, col, req) for req in reqlist)
                       for reqlist in reqs)

        def satisfies(gp, reqlist):
            return any(req in gp for req in reqlist)
        forbidden = satisfies

        def bt(curgp, curcol, reqs, yielded=False):
            # If all requirements have been satisfied, then yield
            if len(reqs) == 0 and not yielded:
                yield curgp
                yielded = True
            # If maximum length reached, then bail
            if len(curgp) >= maxlen or curcol >= self.dimensions[0]:
                return
            # Prune away unsatisfiable requirements and remove lists that have
            # already been satisfied
            satisfiable = [
                [req for req in reqlist if can_satisfy(curgp, curcol, req)]
                for reqlist in reqs if not satisfies(curgp, reqlist)]
            if any(len(reqlist) == 0 for reqlist in satisfiable):
                return

            if can_satisfy_all(curgp, curcol + 1, satisfiable):
                yield from bt(curgp, curcol + 1, satisfiable, yielded)

            for nextgp in insert_next_point(curgp, curcol):
                if not forbidden(nextgp, self.obstructions):
                    yield from bt(nextgp, curcol,
                                  [reqlist for reqlist in reqs
                                   if not satisfies(nextgp, reqlist)])

        yield from bt(GriddedPerm.empty_perm(), 0, self.requirements)

    def merge(self, remove_empty=True):
        """Return an equivalent tiling with a single requirement list."""
        if len(self.requirements) <= 1:
            return self
        reqs = sorted(self.requirements, key=len)
        req1 = reqs[0]
        req2 = reqs[1]
        reqs = reqs[2:]
        new_req = []
        for gp1 in req1:
            for gp2 in req2:
                # TODO: Do this step independent of tilings.
                temp_tiling = Tiling(self.obstructions, [[gp1], [gp2]],
                                     remove_empty=False)
                new_req.extend(Requirement(gp.patt, gp.pos)
                               for gp in temp_tiling.gridded_perms(
                                                  maxlen=len(gp1) + len(gp2)))
        merged_tiling = Tiling(self.obstructions, reqs + [new_req],
                               remove_empty=remove_empty)
        return merged_tiling

    @property
    def point_cells(self):
        if not hasattr(self, "_point_cells"):
            local_length2_obcells = Counter(
                ob.pos[0] for ob in self._obstructions
                if ob.is_localized() and len(ob) == 2)
            self._point_cells = frozenset(
                cell for cell in self.positive_cells
                if local_length2_obcells[cell] == 2)
        return self._point_cells

    @property
    def total_points(self):
        return len(self.point_cells)

    @property
    def positive_cells(self):
        if not hasattr(self, "_positive_cells"):
            self._positive_cells = frozenset(union_reduce(
                intersection_reduce(req.pos for req in reqs)
                for reqs in self._requirements))
        return self._positive_cells

    def total_positive(self):
        return len(self.positive_cells)

    @property
    def possibly_empty(self):
        """Computes the set of possibly empty cells on the tiling."""
        return self.active_cells - self.positive_cells

    @property
    def obstructions(self):
        return self._obstructions

    def total_obstructions(self):
        return len(self._obstructions)

    @property
    def requirements(self):
        return self._requirements

    def total_requirements(self):
        return len(self._requirements)

    @property
    def empty_cells(self):
        """Returns a set of all cells that contain a point obstruction, i.e.,
        are empty.
        """
        return frozenset(filter(None, map(lambda x: x.is_point_obstr(),
                                          self._obstructions)))

    @property
    def active_cells(self):
        """Returns a set of all cells that do not contain a point obstruction,
        i.e., not empty.
        """
        return (union_reduce(ob.pos for ob in self._obstructions
                             if not ob.is_point_obstr()) |
                union_reduce(union_reduce(req.pos for req in reqs)
                             for reqs in self._requirements))

    @property
    def dimensions(self):
        if not hasattr(self, "_dimensions"):
            obcells = union_reduce(ob.pos for ob in self._obstructions)
            reqcells = union_reduce(union_reduce(req.pos for req in reqlist)
                                    for reqlist in self._requirements)
            all_cells = obcells | reqcells
            rows = set(x for (x, y) in all_cells)
            cols = set(y for (x, y) in all_cells)
            if not rows and not cols:
                self._dimensions = (1, 1)
            else:
                self._dimensions = (max(rows) + 1,
                                    max(cols) + 1)
        return self._dimensions

    def find_factors(self, **kwargs):
        """
        Return list with the factors of the tiling.

        Two non-empty cells are in the same factor if they are in the same row
        or colum, or they share an obstruction or requirement.
        """
        n, m = self.dimensions
        cells = list(self.active_cells)
        uf = UnionFind(n * m)

        def cell_to_int(cell):
            return cell[0] * m + cell[1]

        def unite_list(iterable, same_row_or_col=False):
            for i in range(len(iterable)):
                for j in range(i+1, len(iterable)):
                    c1 = iterable[i]
                    c2 = iterable[j]
                    if not same_row_or_col or c1[0] == c2[0] or c1[1] == c2[1]:
                        uf.unite(cell_to_int(c1),
                                 cell_to_int(c2))

        # Unite if share an obstruction or requirement
        for ob in self.obstructions:
            unite_list(ob.pos)
        for req_list in self.requirements:
            unite_list(list(union_reduce(req.pos for req in req_list)))
        # Unite if same row or column
        unite_list(cells, same_row_or_col=True)

        # Collect the connected components of the cells
        all_components = {}
        for cell in cells:
            i = uf.find(cell_to_int(cell))
            if i in all_components:
                all_components[i].append(cell)
            else:
                all_components[i] = [cell]
        component_cells = list(set(cells) for cells in all_components.values())

        # Collect the factors of the tiling
        factors = []
        for cell_component in component_cells:
            obstructions = [ob for ob in self.obstructions
                            if ob.pos[0] in cell_component]
            requirements = [req for req in self.requirements
                            if req[0].pos[0] in cell_component]

            if obstructions or requirements:
                factors.append(Tiling(obstructions=obstructions,
                                      requirements=requirements))

        if kwargs.get('regions', False):
            def cell_map(cell_component, factor):
                map = factor.forward_map
                return {c: set([map[c]]) for c in cell_component
                        if (c in map and
                            map[c] in factor.active_cells)}
            return (factors,
                    [cell_map(cell_component, factor)
                     for cell_component, factor in zip(component_cells,
                                                       factors)])
        return factors

    def get_min_poly(self, root_func=None, root_class=None):
        """Return the minimum polynomial of the generating function implied by
        the tiling."""
        if root_func == self:
            return 0

        def base_cases(tiling):
            if tiling == Tiling(obstructions=(Obstruction(Perm((0,)), ((0, 0),)),)):
                return sympy.sympify("{} - 1".format(get_function(tiling)))
            if tiling ==  Tiling(obstructions=(Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
                                               Obstruction(Perm((1, 0)), ((0, 0), (0, 0))))):
                return sympy.sympify("{} - x - 1".format(get_function(tiling)))

        funcs = {root_class: root_func}
        def get_function(tiling):
            func = funcs.get(tiling)
            if func is None:
                label = len(funcs)
                func = sympy.Function("F_{}".format(label))(sympy.abc.x)
                funcs[tiling] = func
            return func

        def get_equations(tiling):
            if root_class == tiling:
                return []
            lhs = get_function(tiling)
            if tiling.is_empty():
                return [sympy.Eq(lhs, 0)]
            factors = tiling.find_factors()
            if len(factors) > 1:
                rhs = reduce(mul,
                             [get_function(factor) for factor in factors],
                             1)
                return ([sympy.Eq(lhs, rhs)] +
                        list(chain.from_iterable(get_equations(factor)
                                                 for factor in factors)))
            if tiling.requirements:
                req = tiling.requirements[0]
                newreqs = tiling.requirements[1:]
                newobs = (tiling.obstructions +
                          tuple(Obstruction(r.patt, r.pos) for r in req))
                avoids = Tiling(newobs, newreqs)
                without = Tiling(tiling.obstructions, newreqs)
                rhs = get_function(without) - get_function(avoids)
                return ([sympy.Eq(lhs, rhs)] +
                        get_equations(avoids) + get_equations(without))

            for ob in tiling.obstructions:
                if not ob.is_single_cell() and not ob.is_interleaving():
                    patt = Perm.to_standard([v for i, v in enumerate(ob.patt)
                                             if ob.pos[i] == ob.pos[0]])
                    avoids = tiling.add_single_cell_obstruction(patt,
                                                                ob.pos[0])
                    contains = tiling.add_single_cell_requirement(patt,
                                                                  ob.pos[0])
                    lhs = get_function(tiling)
                    rhs = get_function(avoids) + get_function(contains)
                    return ([sympy.Eq(lhs, rhs)] +
                             get_equations(avoids) + get_equations(contains))

            if tiling.dimensions == (1, 1) and not tiling.requirements:
                min_poly = None # check_database(self)
                if min_poly is None:
                    min_poly = base_cases(tiling)
                if min_poly is None:
                    import tilescopethree as t
                    pack = t.strategy_packs.point_placements
                    print("Starting a tilescope run.")
                    print(tiling)
                    searcher = t.TileScopeTHREE(tiling, pack)
                    tree = searcher.auto_search(verbose=False)
                    F = sympy.Function("F")(sympy.abc.x)
                    min_poly = tree.get_min_poly().subs({F: lhs})
                return [sympy.Eq(min_poly, 0)]
            error = "Can't handle tiling.\n{}".format(tiling)
            raise NotImplementedError(error)

        def check_poly(min_poly, initial, root_initial):
            """Return True if this is a minimum polynomial for the generating
            function F of self."""
            verification = min_poly.subs({get_function(self): initial})
            if root_initial is not None:
                verification = verification.subs({root_func: root_initial})
            verification = verification.expand()
            verification = verification + sympy.O(sympy.abc.x**verify)
            verification = verification.removeO()
            return verification == 0

        eqs = get_equations(self)
        class_func = get_function(self)
        all_funcs = set(x for eq in eqs for x in eq.atoms(sympy.Function)
                        if x!= class_func and x != root_func)
        basis = sympy.groebner(eqs, *all_funcs, root_func, class_func,
                                wrt=[sympy.abc.x, root_func], order='grevlex')


        # Compute some initial conditions to length verify.
        verify = 5
        if basis.polys:
            initial = 0
            root_initial = None
            if root_class is not None:
                root_initial = 0
            for i in range(verify + 1):
                class_coeff = len(list(self.objects_of_length(i)))
                initial += class_coeff * sympy.abc.x ** i
                if root_class is not None:
                    root_coeff = len(list(root_class.objects_of_length(i)))
                    root_initial += root_coeff * sympy.abc.x ** i

        # Check that a polynomial is actually a min poly for the class by
        # plugging in initial conditions.
        for poly in basis.polys:
            if (poly.atoms(sympy.Function) == {class_func} or
                    poly.atoms(sympy.Function) == {class_func, root_func}):
                eq = poly.as_expr()
                if check_poly(eq, initial, root_initial):
                    F = sympy.Function("F")(sympy.abc.x)
                    return eq.subs({class_func: F})

        raise RuntimeError(("Incorrect minimum polynomial:\n" + str(self)))

    def get_genf(self, *args, **kwargs):
        """
        Return generating function of a tiling.

        Currently works only for the point tiling and the empty tiling.
        """
        # If root has been given a function, return it if you see the root
        if (kwargs.get('root_func') is not None and
                self == kwargs.get('root_class')):
            return kwargs['root_func']

        if (kwargs.get('root_func') is not None and
            kwargs.get('root_class') is not None and
                (self == kwargs.get('root_class') or
                 self == kwargs.get('root_class').reverse() or
                 self == kwargs.get('root_class').inverse() or
                 self == kwargs.get('root_class').rotate90() or
                 self == kwargs.get('root_class').rotate180() or
                 self == kwargs.get('root_class').rotate270() or
                 self == kwargs.get('root_class').antidiagonal() or
                 self == kwargs.get('root_class').complement())):
            return kwargs['root_func']

        # Remove once fusion specifications are added to the database.
        if self == Tiling([Obstruction.single_cell(Perm((0, 1, 2)), (0, 0))]):
            return sympy.sympify('-1/2*(sqrt(-4*x + 1) - 1)/x')
        if self == Tiling([Obstruction.single_cell(Perm((2, 1, 0)), (0, 0))]):
            return sympy.sympify('-1/2*(sqrt(-4*x + 1) - 1)/x')

        if kwargs.get('substitutions'):
            if kwargs.get('subs') is None:
                kwargs['subs'] = {}
            if kwargs.get('symbols') is None:
                kwargs['symbols'] = {}
        if self.is_empty():
            return sympy.sympify(0)
        # Reduce tiling by multiplying together the factors.
        if kwargs.get('factored') is None:
            return reduce(mul, [factor.get_genf(factored=True, *args, **kwargs)
                                for factor in self.find_factors()], 1)
        del kwargs['factored']
        # Reduce requirements list by either containing or avoiding the first
        # requirement in the list
        for req_list in self.requirements:
            if len(req_list) > 1:
                req = req_list[0]
                return (self.add_obstruction(
                                req.patt, req.pos).get_genf(*args, **kwargs) +
                        self.add_requirement(
                                req.patt, req.pos).get_genf(*args, **kwargs))

        # At this stage, all requirement lists are length 1. Can count by
        # counting the tiling with the requirement removed and subtracting the
        # tiling with it added as an obstruction.
        if len(self.requirements) > 0:
            ignore = Tiling(obstructions=self.obstructions,
                            requirements=self.requirements[1:])
            req = self.requirements[0][0]
            return (ignore.get_genf(*args, **kwargs) -
                    ignore.add_obstruction(req.patt,
                                           req.pos).get_genf(*args, **kwargs))

        # Reduce factorable obstruction by either containing or avoiding
        # localized subobstruction
        for ob in self.obstructions:
            if not ob.is_single_cell() and not ob.is_interleaving():
                patt = Perm.to_standard([v for i, v in enumerate(ob.patt)
                                         if ob.pos[i] == ob.pos[0]])
                return (self.add_single_cell_obstruction(
                                patt, ob.pos[0]).get_genf(*args, **kwargs) +
                        self.add_single_cell_requirement(
                                patt, ob.pos[0]).get_genf(*args, **kwargs))

        # some special cases with one by one tilings
        if self.dimensions == (1, 1):
            # The empty tiling has exactly one gridded permutation of length 0
            if (not self.requirements and len(self.obstructions) == 1 and
                    len(self.obstructions[0]) == 1):
                return sympy.sympify(1)
            # The point tiling has exactly one gridded permutation of length 1
            if (len(self.obstructions) == 2 and
                    all(len(ob) == 2 for ob in self.obstructions) and
                    len(self.requirements) == 1 and
                    len(self.requirements[0]) == 1 and
                    len(self.requirements[0][0]) == 1):
                return sympy.abc.x

        if kwargs.get('substitutions'):
            symbols = kwargs.get('symbols')
            symbol = symbols.get(self)
            if symbol is None:
                symbol = sympy.Function('C_' + str(len(symbols)))(sympy.abc.x)
                symbols[self] = symbol
            subs = kwargs.get('subs')
            if symbol not in subs:
                subs[symbol] = check_database(self)
            return symbol
        # Check the database
        try:
            genf = check_database(self)
        except Exception:
            raise ValueError("Tiling not in database:\n" + repr(self))
        return genf
    #
    # Dunder methods
    #

    def __hash__(self):
        return (hash(self._requirements) ^ hash(self._obstructions))

    def __eq__(self, other):
        if not isinstance(other, Tiling):
            return False
        return ((self.obstructions == other.obstructions) and
                (self.requirements == other.requirements))

    def __ne__(self, other):
        if not isinstance(other, Tiling):
            return True
        return ((self.obstructions != other.obstructions) or
                (self.requirements != other.requirements))

    def __repr__(self):
        format_string = "Tiling(obstructions={}, requirements={})"
        return format_string.format(self.obstructions, self.requirements)

    def __str__(self):
        dim_i, dim_j = self.dimensions
        result = []
        # Create tiling lines
        for j in range(2*dim_j + 1):
            for i in range(2*dim_i + 1):
                # Whether or not a vertical line and a horizontal line is
                # present
                vertical = i % 2 == 0
                horizontal = j % 2 == 0
                if vertical:
                    if horizontal:
                        result.append("+")
                    else:
                        result.append("|")
                elif horizontal:
                    result.append("-")
                else:
                    result.append(" ")
            result.append("\n")

        labels = dict()

        # Put the sets in the tiles

        # How many characters are in a row in the grid
        row_width = 2*dim_i + 2
        curr_label = 1
        for cell, gridded_perms in sorted(self.cell_basis().items()):
            obstructions, _ = gridded_perms
            basis = list(sorted(obstructions))
            if basis == [Perm((0, ))]:
                continue
            # the block, is the basis and whether or not positive
            block = (tuple(basis), cell in self.positive_cells)
            label = labels.get(block)
            if label is None:
                if basis == [Perm((0, 1)), Perm((1, 0))]:
                    if cell in self.positive_cells:
                        label = '\u25cf'
                    else:
                        label = '\u25cb'
                elif basis == [Perm((0, 1))]:
                    label = '\\'
                elif basis == [Perm((1, 0))]:
                    label = '/'
                else:
                    label = str(curr_label)
                    curr_label += 1
                labels[block] = label
            row_index_from_top = dim_j - cell[1] - 1
            index = (2*row_index_from_top + 1)*row_width + 2*cell[0] + 1
            result[index] = label

        # Legend at bottom
        for block, label in sorted(labels.items(), key=lambda x: x[1]):
            basis, positive = block
            result.append(label)
            result.append(": ")
            if basis == (Perm((0, 1)), Perm((1, 0))) and positive:
                result.append("point")
            else:
                result.append("Av{}({})".format("+" if positive else "",
                                                ", ".join(str(p)
                                                          for p in basis)))
            result.append("\n")

        result.append("Crossing obstructions:\n")
        for ob in self.obstructions:
            if not ob.is_single_cell():
                result.append(str(ob))
                result.append("\n")
        for i, req in enumerate(self.requirements):
            result.append("Requirement {}:\n".format(str(i)))
            for r in req:
                result.append(str(r))
                result.append("\n")
        if self.requirements:
            result = result[:-1]

        return "".join(result)
