from collections import Counter
from heapq import heapify, heappop, heappush
from typing import (
    TYPE_CHECKING,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
)

from .minimal_gridded_perms import MinimalGriddedPerms
from permuta import Perm
from tilings.griddedperm import GriddedPerm

if TYPE_CHECKING:
    from tilings import Tiling

Cell = Tuple[int, int]


class GriddedPermsOnTiling:
    """
    An Iterable of all gridded permutations griddable on the tiling.

    The gridded permutations are up to length of the longest minimum
    gridded permutations that is griddable on the tiling unless maxlen is
    specified.
    """

    def __init__(self, tiling: "Tiling", maxlen: Optional[int] = None):
        self._active_cells = tiling.active_cells
        self._obstructions = tiling.obstructions
        self._requirements = tiling.requirements
        self._num_columns = tiling.dimensions[0]
        self._maxlen = (
            maxlen
            if maxlen is not None
            else max(tiling.maximum_length_of_minimum_gridded_perm(), 1)
        )
        self._cell_counts = self.min_cell_counts()

    def patts_contained_in_cell(self, cell: Cell) -> Set[Perm]:
        """
        All the patterns that must be contained in the given cell of the
        tiling.
        """
        res: Set[Perm] = set()
        for req_list in self._requirements:
            subgp = req_list[0].get_gridded_perm_in_cells([cell])
            patts = set(subgp.all_subperms(proper=False))
            for req in req_list[1:]:
                subgp = req.get_gridded_perm_in_cells([cell])
                patts.intersection_update(subgp.all_subperms(proper=False))
            res.update(patts)
        return res

    def min_cell_counts(self) -> Dict[Cell, int]:
        """
        The minimum number of points that must be in each cell of the tiling
        according to the requirements.
        """
        res: Dict[Cell, int] = dict()
        for cell in self._active_cells:
            patts_in_cell = self.patts_contained_in_cell(cell)
            points_in_cell = max((len(p) for p in patts_in_cell), default=0)
            if sum(1 for p in patts_in_cell if len(p) == points_in_cell) > 1:
                points_in_cell += 1
            res[cell] = points_in_cell
        return res

    def can_satisfy_cell_counts(self, gp: GriddedPerm) -> bool:
        """
        Determine if the given gridded permutation can satisfy the lower bound
        on the number of point in each cell.
        """
        points_in_cells = Counter(gp.pos)
        needed = sum(
            max(0, (self._cell_counts[cell] - points_in_cells[cell]))
            for cell in self._active_cells
        )
        to_place = self._maxlen - len(gp)
        return needed <= to_place

    def insert_next_point(self, gp: GriddedPerm, col: int,) -> Iterator[GriddedPerm]:
        """
        Insert the next point in the given column in all possible way.
        """
        active_cell_in_col = (cell for cell in self._active_cells if cell[0] == col)
        for cell in active_cell_in_col:
            _, _, minval, maxval = gp.get_bounding_box(cell)
            for val in range(minval, maxval + 1):
                next_gp = GriddedPerm(gp.patt.insert(new_element=val), gp.pos + (cell,))
                yield next_gp

    def can_satisfy_all(
        self, gp: GriddedPerm, col: int, reqs: Iterable[Iterable[GriddedPerm]]
    ) -> bool:
        """
        Indicate if all the requirement lists can be satisfied by the gridded
        perm if we keep extending from the given column.
        """
        return all(
            any(self.can_satisfy(gp, col, req) for req in reqlist) for reqlist in reqs
        )

    @staticmethod
    def can_satisfy(gp: GriddedPerm, col: int, req: GriddedPerm) -> bool:
        return req.get_subperm_left_col(col) in gp

    @staticmethod
    def satisfies(gp: GriddedPerm, reqlist: Iterable[GriddedPerm]) -> bool:
        return any(req in gp for req in reqlist)

    def forbidden(self, gp: GriddedPerm) -> bool:
        """
        Determine if the gridded contains one of the obstructions of the
        tiling.
        """
        return any(ob in gp for ob in self._obstructions)

    def backtracking(
        self,
        curgp: GriddedPerm,
        curcol: int,
        reqs: Sequence[Sequence[GriddedPerm]],
        yielded: Optional[bool] = False,
    ) -> Iterator[GriddedPerm]:
        """
        The backtracking algorithm to generate the gridded permutation.

        INPUT:
        - `curgp`: The current gridded permutation under consideration
        - `reqs`: Iterable of unsatisfied list requirements
        - `yielded`: True if the permutation has already been yielded.
        """
        # If all requirements have been satisfied, then yield
        if not reqs and not yielded:
            yield curgp
            yielded = True
        # If maximum length reached, then bail
        if len(curgp) >= self._maxlen or curcol >= self._num_columns:
            return
        # Prune away unsatisfiable requirements and remove lists that have
        # already been satisfied
        satisfiable = tuple(
            tuple(r for r in reqlist if self.can_satisfy(curgp, curcol, r))
            for reqlist in reqs
        )
        if any(not reqlist for reqlist in satisfiable):
            return

        if not self.can_satisfy_cell_counts(curgp):
            return

        if self.can_satisfy_all(curgp, curcol + 1, satisfiable):
            yield from self.backtracking(curgp, curcol + 1, satisfiable, yielded)

        for nextgp in self.insert_next_point(curgp, curcol):
            if not self.forbidden(nextgp):
                unsatisfied_reqs = tuple(
                    reqlist for reqlist in reqs if not self.satisfies(nextgp, reqlist)
                )
                yield from self.backtracking(nextgp, curcol, unsatisfied_reqs)

    def __iter__(self) -> Iterator[GriddedPerm]:
        if not GriddedPerm(Perm(tuple()), tuple()) in self._obstructions:
            yield from self.backtracking(
                GriddedPerm.empty_perm(), 0, self._requirements
            )


class QueuePacket:
    def __init__(
        self, gp: GriddedPerm, last_cell: Cell, mindices: Dict[Cell, int], placed: int
    ):
        self.gp = gp
        self.last_cell = last_cell
        self.mindices = mindices
        self.placed: int = placed

    def __lt__(self, other: "QueuePacket"):
        return self.gp < other.gp


class AlternativeGriddedPermsOnTiling:
    """
    An Iterable of all gridded permutations griddable on the tiling.

    The gridded permutations yielded in order of size, shortest first. They are
    built by inserting points into the minimal gridded permutations.
    """

    def __init__(self, tiling: "Tiling"):
        self._tiling = tiling
        self._minimal_gps = MinimalGriddedPerms(tiling)
        self._yielded_gridded_perms: Set[GriddedPerm] = set()

    def gridded_perms(self, size: int, place_at_most: int = None):
        if place_at_most is None:
            place_at_most = size
        queue: List[QueuePacket] = []
        heapify(queue)
        for mgp in self._minimal_gps.minimal_gridded_perms():
            if len(mgp) <= size:
                packet = QueuePacket(mgp, (-1, -1), dict(), 0)
                heappush(queue, packet)
            else:
                break
        work_packets_done: Set[Tuple[GriddedPerm, Cell]] = set()
        while queue:
            packet = heappop(queue)
            gp, last_cell, mindices, placed = (
                packet.gp,
                packet.last_cell,
                packet.mindices,
                packet.placed,
            )
            if len(gp) <= size:
                if gp not in self._yielded_gridded_perms:
                    self._yielded_gridded_perms.add(gp)
                    yield gp
            else:
                return
            if placed >= place_at_most:
                continue
            for cell in self._tiling.active_cells:
                if cell < last_cell:
                    continue
                for idx, nextgp in self._minimal_gps.insert_point(
                    gp, cell, mindices.get(cell, 0)
                ):
                    key = (nextgp, cell)
                    if key in work_packets_done:
                        continue
                    work_packets_done.add(key)
                    if not self._minimal_gps.satisfies_obstructions(
                        nextgp, must_contain=cell
                    ):
                        continue
                    next_mindices = {
                        c: i if i <= idx else i + 1
                        for c, i in mindices.items()
                        if c != cell
                    }
                    next_mindices[cell] = idx + 1
                    heappush(
                        queue, QueuePacket(nextgp, cell, next_mindices, placed + 1),
                    )
