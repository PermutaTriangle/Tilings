import abc
from importlib import import_module
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from permuta import Perm

from .griddedperm import GriddedPerm

Cell = Tuple[int, int]

if TYPE_CHECKING:
    from tilings import Tiling

AssumptionClass = TypeVar("AssumptionClass", bound="Assumption")
CountAssumption = Union["OddCountAssumption", "EvenCountAssumption"]


class Assumption:
    """
    An abstract class for assumption made on tilings. This consists of
    a set of cells that are passed around according to forward and
    backward maps of strategies.
    """

    def __init__(self, gps: Iterable[GriddedPerm]):
        self.gps = tuple(sorted(set(gps)))
        self.cells = frozenset(gp.pos[0] for gp in self.gps)

    @classmethod
    def from_cells(
        cls: Type[AssumptionClass], cells: Iterable[Cell]
    ) -> AssumptionClass:
        gps = [GriddedPerm.single_cell((0,), cell) for cell in cells]
        return cls(gps)

    def avoiding(
        self: AssumptionClass,
        obstructions: Iterable[GriddedPerm],
        active_cells: Optional[Iterable[Cell]] = None,
    ) -> AssumptionClass:
        """
        Return the tracking absumption where all of the gridded perms avoiding
        the obstructions are removed. If active_cells is not None, then any
        assumptions involving a cell not in active_cells will be removed.
        """
        obstructions = tuple(obstructions)
        if active_cells is not None:
            return self.__class__(
                tuple(
                    gp
                    for gp in self.gps
                    if all(cell in active_cells for cell in gp.pos)
                    and gp.avoids(*obstructions)
                )
            )
        return self.__class__(tuple(gp for gp in self.gps if gp.avoids(*obstructions)))

    def to_jsonable(self) -> dict:
        """Return a dictionary form of the assumption."""
        c = self.__class__
        return {
            "class_module": c.__module__,
            "assumption": c.__name__,
            "gps": [gp.to_jsonable() for gp in self.gps],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Assumption":
        """Return the assumption from the json dict representation."""
        module = import_module(d["class_module"])
        AssClass: Type["TrackingAssumption"] = getattr(module, d["assumption"])
        assert issubclass(AssClass, Assumption), "Not a valid Assumption"
        gps = [GriddedPerm.from_dict(gp) for gp in d["gps"]]
        return AssClass(gps)

    def __eq__(self, other) -> bool:
        if other.__class__ == self.__class__:
            return bool(self.gps == other.gps)
        return NotImplemented

    def __len__(self) -> int:
        return len(self.gps)

    def __lt__(self, other) -> bool:
        if isinstance(other, Assumption):
            key_self = (self.__class__.__name__, self.gps)
            key_other = (other.__class__.__name__, other.gps)
            return key_self < key_other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(hash(self.gps) + hash(self.__class__.__name__))

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"({self.gps})"


class TrackingAssumption(Assumption):
    """
    An assumption used to keep track of the occurrences of a set of gridded
    permutations.
    """

    def get_value(self, gp: GriddedPerm) -> int:
        """
        Return the number of occurrences of each of the gridded perms being track in
        the gridded perm gp.
        """
        return len(list(chain.from_iterable(p.occurrences_in(gp) for p in self.gps)))

    def get_components(self, tiling: "Tiling") -> List[List[GriddedPerm]]:
        """
        Return the lists of gps that count exactly one occurrence.
        Only implemented for when a size one gp is in a point cell.
        """
        return [
            [gp] for gp in self.gps if len(gp) == 1 and gp.pos[0] in tiling.point_cells
        ]

    def remove_components(self, tiling: "Tiling") -> "TrackingAssumption":
        """
        Return the TrackingAssumption found by removing all the components
        found by the get_components method.
        """
        gps_to_remove = set(chain.from_iterable(self.get_components(tiling)))
        return self.__class__(gp for gp in self.gps if gp not in gps_to_remove)

    def __str__(self) -> str:
        if all(len(gp) == 1 for gp in self.gps):
            cells = ", ".join(str(gp.pos[0]) for gp in self.gps)
            return f"can count points in cell{'s' if len(self.gps) > 1 else ''} {cells}"
        return f"can count occurrences of {', '.join(str(gp) for gp in self.gps)}"


class ComponentAssumption(TrackingAssumption):
    """
    An assumption used to keep track of the number of components in a
    region of a tiling.

    In order to inherit from TrackingAssumption, the set of cells should be
    given as a set of length 1 gridded perms using each cell. This ensures
    most strategies work without change.
    """

    def __init__(self, gps: Iterable[GriddedPerm]):
        super().__init__(gps)
        assert all(len(gp) == 1 for gp in self.gps)

    @abc.abstractmethod
    def decomposition(self, perm: Perm) -> List[Perm]:
        """Count the number of component in a permutation."""

    @abc.abstractmethod
    def tiling_decomposition(self, tiling: "Tiling") -> List[List[Cell]]:
        """Return the components of a given tiling."""

    @abc.abstractmethod
    def opposite_tiling_decomposition(self, tiling: "Tiling") -> List[List[Cell]]:
        """Return the alternative components of a given tiling."""

    @abc.abstractmethod
    def one_or_fewer_components(self, tiling: "Tiling", cell: Cell) -> bool:
        """Return True if the cell contains one or fewer components."""

    def get_components(self, tiling: "Tiling") -> List[List[GriddedPerm]]:
        sub_tiling = tiling.sub_tiling(self.cells)
        separated_tiling, fwd_map = sub_tiling.row_and_column_separation_with_mapping()
        back_map = {b: a for a, b in fwd_map.items()}
        components = self.tiling_decomposition(separated_tiling)
        return [
            [
                GriddedPerm.point_perm(sub_tiling.backward_map.map_cell(back_map[cell]))
                for cell in comp
            ]
            for comp in components
            if self.is_component(comp, separated_tiling)
        ]

    def is_component(self, cells: List[Cell], tiling: "Tiling") -> bool:
        """
        Return True if cells form a component on the tiling.

        Cells are assumed to have come from cell_decomposition.
        """
        sub_tiling = tiling.sub_tiling(cells)
        skew_cells = self.opposite_tiling_decomposition(sub_tiling)

        if any(
            scells[0] in sub_tiling.positive_cells
            and self.one_or_fewer_components(sub_tiling, scells[0])
            for scells in skew_cells
            if len(scells) == 1
        ):
            return True

        def is_positive(scells) -> bool:
            return any(
                all(any(cell in gp.pos for cell in scells) for gp in req)
                for req in sub_tiling.requirements
            )

        return sum(1 for scells in skew_cells if is_positive(scells)) > 1

    def cell_decomposition(self, tiling: "Tiling"):
        sub_tiling = tiling.sub_tiling(self.cells)
        return [
            [sub_tiling.backward_map.map_cell(cell) for cell in comp]
            for comp in self.tiling_decomposition(sub_tiling)
        ]

    def get_value(self, gp: GriddedPerm) -> int:
        """
        Return the number of components in the tracked region of the gridded perm.
        """
        subgp = gp.get_gridded_perm_in_cells(self.cells)
        return len(self.decomposition(subgp.patt))

    def __str__(self) -> str:
        return f"can count components in cells {self.cells}"


class SumComponentAssumption(ComponentAssumption):
    @staticmethod
    def decomposition(perm: Perm) -> List[Perm]:
        return perm.sum_decomposition()  # type: ignore

    @staticmethod
    def tiling_decomposition(tiling: "Tiling") -> List[List[Cell]]:
        return tiling.sum_decomposition()

    @staticmethod
    def opposite_tiling_decomposition(tiling: "Tiling") -> List[List[Cell]]:
        return tiling.skew_decomposition()

    @staticmethod
    def one_or_fewer_components(tiling: "Tiling", cell: Cell) -> bool:
        return GriddedPerm.single_cell(Perm((0, 1)), cell) in tiling.obstructions

    def __str__(self) -> str:
        return f"can count sum components in cells {self.cells}"


class SkewComponentAssumption(ComponentAssumption):
    @staticmethod
    def decomposition(perm: Perm) -> List[Perm]:
        return perm.skew_decomposition()  # type: ignore

    @staticmethod
    def tiling_decomposition(tiling: "Tiling") -> List[List[Cell]]:
        return tiling.skew_decomposition()

    @staticmethod
    def opposite_tiling_decomposition(tiling: "Tiling") -> List[List[Cell]]:
        return tiling.sum_decomposition()

    @staticmethod
    def one_or_fewer_components(tiling: "Tiling", cell: Cell) -> bool:
        return GriddedPerm.single_cell(Perm((1, 0)), cell) in tiling.obstructions

    def __str__(self) -> str:
        return f"can count skew components in cells {self.cells}"


class PredicateAssumption(Assumption):
    """
    An assumption that checks some boolean holds for the sub gridded
    permutation at the cells.
    """

    def satisfies(self, gp: GriddedPerm) -> bool:
        """Return True if sub gp at cells satisfies the predicate."""
        return self._gp_satisfies(gp.get_gridded_perm_in_cells(self.cells))

    @abc.abstractmethod
    def _gp_satisfies(self, gp: GriddedPerm) -> bool:
        """Return True if gp satisfies the predicate."""

    @abc.abstractmethod
    def can_be_satisfied(self, tiling: "Tiling") -> bool:
        """
        Return True if the predicate can be satisfied by some gridded
        perm on the tiling.
        """

    def refinements(self) -> Iterator[Tuple["PredicateAssumption", ...]]:
        """
        Yield tuples of Assumption that such that the predicate
        satisfies a gp iff all refined predicates satisfies a gp.
        """
        yield (self,)


class OddCountAssumption(PredicateAssumption):
    """There is an odd number of points at the cells"""

    def can_be_satisfied(self, tiling: "Tiling") -> bool:
        return True

    def _gp_satisfies(self, gp: GriddedPerm) -> bool:
        return bool(len(gp) % 2)

    def refinements(self) -> Iterator[Tuple[CountAssumption, ...]]:
        """
        Yield tuples of single cell Odd/Even CountAssumption that
        combine to match the parity.
        """
        yield from self.helper_refinements(list(self.cells), True)

    @staticmethod
    def helper_refinements(
        cells: List[Cell], odd: bool
    ) -> Iterator[Tuple[CountAssumption, ...]]:
        cell = cells.pop()
        if cells:
            for refinement in OddCountAssumption.helper_refinements(list(cells), odd):
                yield (EvenCountAssumption.from_cells([cell]),) + refinement
            for refinement in OddCountAssumption.helper_refinements(
                list(cells), not odd
            ):
                yield (OddCountAssumption.from_cells([cell]),) + refinement

        elif odd:
            yield (OddCountAssumption.from_cells([cell]),)
        else:
            yield (EvenCountAssumption.from_cells([cell]),)

    def __str__(self) -> str:
        return f"odd number of points in cells {self.cells}"


class EvenCountAssumption(PredicateAssumption):
    """There is an even number of points at the cells"""

    def can_be_satisfied(self, tiling: "Tiling") -> bool:
        return True

    def _gp_satisfies(self, gp: GriddedPerm) -> bool:
        return not bool(len(gp) % 2)

    def refinements(self) -> Iterator[Tuple[CountAssumption, ...]]:
        """
        Yield tuples of single cell Odd/Even CountAssumption that
        combine to match the parity.
        """
        yield from OddCountAssumption.helper_refinements(list(self.cells), False)

    def __str__(self) -> str:
        return f"even number of points in cells {self.cells}"


class EqualParityAssumption(PredicateAssumption):
    def can_be_satisfied(self, tiling: "Tiling") -> bool:
        return True

    def satisfies(self, gp: GriddedPerm) -> bool:
        return all(
            idx % 2 == val % 2
            for idx, val in enumerate(gp.patt)
            if gp.pos[idx] in self.cells
        )

    def _gp_satisies(self, gp: GriddedPerm) -> bool:
        raise NotImplementedError

    def refinements(self) -> Iterator[Tuple["EqualParityAssumption", ...]]:
        yield tuple(EqualParityAssumption.from_cells([cell]) for cell in self.cells)

    def __str__(self) -> str:
        return f"points are equal parity in cells {self.cells}"


class OppositeParityAssumption(PredicateAssumption):
    def can_be_satisfied(self, tiling: "Tiling") -> bool:
        return True

    def satisfies(self, gp: GriddedPerm) -> bool:
        return all(
            idx % 2 != val % 2
            for idx, val in enumerate(gp.patt)
            if gp.pos[idx] in self.cells
        )

    def _gp_satisies(self, gp: GriddedPerm) -> bool:
        raise NotImplementedError

    def refinements(self) -> Iterator[Tuple["OppositeParityAssumption", ...]]:
        yield tuple(OppositeParityAssumption.from_cells([cell]) for cell in self.cells)

    def __str__(self) -> str:
        return f"points are opposite parity in cells {self.cells}"
