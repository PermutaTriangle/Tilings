import itertools
from string import ascii_uppercase
from typing import TYPE_CHECKING, Dict, FrozenSet, Iterable, Iterator, List, Set, Tuple

from permuta import Perm

if TYPE_CHECKING:
    from tilings import GriddedPerm, Tiling
    from tilings.parameter_counter import PreimageCounter

__all__ = ["TilingDisplayer"]

Cell = Tuple[int, int]
POINT_BASIS = frozenset([Perm((0, 1)), Perm((1, 0))])


def words_generator(alphabet: str) -> Iterator[str]:
    """
    Iterator on word over the alphabet in lexicographic order.
    """
    length = 1
    while True:
        yield from map("".join, itertools.product(alphabet, repeat=length))
        length += 1


class TilingDisplayer:
    LABELS: Dict[FrozenSet[Perm], str] = {
        frozenset([Perm((0,))]): " ",
        POINT_BASIS: "\u25cb",
        frozenset([Perm((0, 1))]): "\\",
        frozenset([Perm((1, 0))]): "/",
    }
    LABEL_ITERATOR = words_generator(ascii_uppercase)

    def __init__(self, tiling: "Tiling"):
        self.tiling = tiling
        self.label_used: Set[FrozenSet[Perm]] = set()

    def ascii(self) -> str:
        lines = self.grid_lines(self.tiling)
        lines.extend(self.legend())
        lines.extend(self.crossing_obs_lines(self.tiling.obstructions))
        lines.extend(self.req_lines(self.tiling.requirements))
        lines.extend(self.params_lines())
        return "\n".join(lines)

    def get_label(self, basis: Iterable[Perm], positive: bool) -> str:
        """
        Return the appropriate label of the basis
        """
        basis = frozenset(basis)
        self.label_used.add(basis)
        if basis not in self.LABELS:
            self.LABELS[basis] = next(self.LABEL_ITERATOR)
        label = self.LABELS[basis]
        if positive:
            if basis == POINT_BASIS:
                return "\u25cf"
            else:
                label += "+"
        return label

    def legend(self) -> List[str]:
        content = []
        for basis in self.label_used:
            label = self.LABELS[basis]
            if label[0] in ascii_uppercase:
                content.append(f"{label}: Av({', '.join(map(str, basis))})")
        content.sort()
        return content

    def grid_lines(self, tiling: "Tiling") -> List[str]:
        """
        Compute the grid that represents the given tiling.
        """
        grid = [
            [" " for _ in range(tiling.dimensions[0])]
            for _ in range(tiling.dimensions[1])
        ]
        for cell, (basis, _) in sorted(tiling.cell_basis().items()):
            label = self.get_label(basis, cell in tiling.positive_cells)
            grid[-1 - cell[1]][cell[0]] = label
        col_widths = [
            max(len(row[i]) for row in grid) for i in range(tiling.dimensions[0])
        ]
        grid = [
            [
                label + " " * (width - len(label))
                for label, width in zip(row, col_widths)
            ]
            for row in grid
        ]
        horizontal_line = f"+{'+'.join('-' * width for width in col_widths)}+"
        lines = [horizontal_line]
        for row in grid:
            lines.append(f"|{'|'.join(row)}|")
            lines.append(horizontal_line)
        return lines

    def crossing_obs_lines(self, obs: Iterable["GriddedPerm"]) -> List[str]:
        lines = []
        for ob in obs:
            if not ob.is_single_cell():
                lines.append(str(ob))
        if lines:
            lines = ["Crossing obstructions:"] + lines
        return lines

    def req_lines(self, reqs: Iterable[Iterable["GriddedPerm"]]) -> List[str]:
        lines = []
        for i, req in enumerate(reqs):
            lines.append(f"Requirement {i}:")
            for r in req:
                lines.append(str(r))
        return lines

    def params_lines(self) -> List[str]:
        lines = []
        for i, param in enumerate(self.tiling.parameters):
            lines.append(f"** Parameter {i} **")
            for preimage_counter in param:
                lines.extend(
                    self.indent(self.preimage_counter_lines(preimage_counter), 2)
                )
        return lines

    def preimage_counter_lines(self, preimage: "PreimageCounter") -> List[str]:
        lines = []
        if any(k != v for k, v in preimage.map.row_map.items()):
            lines.append(f"row map: {self.map_str(preimage.map.row_map)}")
        if any(k != v for k, v in preimage.map.col_map.items()):
            lines.append(f"col map: {self.map_str(preimage.map.col_map)}")
        lines.extend(self.grid_lines(preimage.tiling))
        extra_obs, extra_reqs = preimage.extra_obs_and_reqs(self.tiling)
        lines.extend(self.crossing_obs_lines(extra_obs))
        lines.extend(self.req_lines(extra_reqs))
        return lines

    @staticmethod
    def map_str(d: dict) -> str:
        content = ", ".join(f"{k}:{v}" for k, v in d.items())
        return f"{{{content}}}"

    @staticmethod
    def indent(lines: List[str], space: int) -> List[str]:
        """
        Indent all the given line by the given amount of withe space.
        """
        return [" " * space + line for line in lines]
