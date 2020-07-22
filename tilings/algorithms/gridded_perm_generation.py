from heapq import heapify, heappop, heappush
from typing import TYPE_CHECKING, Dict, List, Set, Tuple

from tilings.griddedperm import GriddedPerm

from .minimal_gridded_perms import MinimalGriddedPerms

if TYPE_CHECKING:
    from tilings import Tiling

Cell = Tuple[int, int]


class QueuePacket:
    def __init__(
        self, gp: GriddedPerm, last_cell: Cell, mindices: Dict[Cell, int], placed: int
    ):
        self.gp = gp
        self.last_cell = last_cell
        self.mindices = mindices
        self.placed: int = placed

    def __lt__(self, other: "QueuePacket"):
        return len(self.gp) < len(other.gp)


class GriddedPermsOnTiling:
    """
    An Iterable of all gridded permutations griddable on the tiling.

    The gridded permutations yielded in order of size, shortest first. They are
    built by inserting points into the minimal gridded permutations.
    """

    def __init__(self, tiling: "Tiling"):
        self._tiling = tiling
        self._minimal_gps = MinimalGriddedPerms(tiling)
        self._yielded_gridded_perms: Set[GriddedPerm] = set()

    def prepare_queue(self, size: int) -> List[QueuePacket]:
        queue: List[QueuePacket] = []
        heapify(queue)
        for mgp in self._minimal_gps.minimal_gridded_perms():
            if len(mgp) <= size:
                packet = QueuePacket(mgp, (-1, -1), dict(), 0)
                heappush(queue, packet)
            else:
                break
        return queue

    def gridded_perms(self, size: int, place_at_most: int = None):
        if place_at_most is None:
            place_at_most = size
        queue = self.prepare_queue(size)
        work_packets_done: Set[Tuple[GriddedPerm, Cell]] = set()
        while queue:
            packet = heappop(queue)
            gp, mindices = (
                packet.gp,
                packet.mindices,
            )
            if len(gp) <= size:
                if gp not in self._yielded_gridded_perms:
                    self._yielded_gridded_perms.add(gp)
                    yield gp
            else:
                return
            if packet.placed >= place_at_most:
                continue
            for cell in self._tiling.active_cells:
                if cell < packet.last_cell:
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
                        queue,
                        QueuePacket(nextgp, cell, next_mindices, packet.placed + 1),
                    )
