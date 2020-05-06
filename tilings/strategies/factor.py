from itertools import chain
from typing import Iterable, Iterator, Optional, Tuple

from comb_spec_searcher import (
    CartesianProductStrategy,
    Constructor,
    Strategy,
    StrategyGenerator,
)
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import (
    Factor,
    FactorWithInterleaving,
    FactorWithMonotoneInterleaving,
)
from tilings.exception import InvalidOperationError
from tilings.misc import partitions_iterator

Cell = Tuple[int, int]

__all__ = (
    "AllFactorStrategy",
    "FactorStrategy",
    "FactorWithInterleavingStrategy",
    "FactorWithMonotoneInterleavingStrategy",
)


class FactorStrategy(CartesianProductStrategy[Tiling]):
    def __init__(
        self,
        partition: Iterable[Iterable[Cell]],
        ignore_parent: bool = True,
        workable: bool = True,
    ):
        self.partition = tuple(sorted(tuple(sorted(p)) for p in partition))
        super().__init__(ignore_parent=ignore_parent, workable=workable)

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling, ...]:
        """
        # TODO: Taken from reducible factorisations function in Factor. Pick where.
        """
        return tuple(tiling.sub_tiling(cells) for cells in self.partition)

    def formal_step(self) -> str:
        """
        Return a string that describe the operation performed on the tiling.
        """
        return "Factor with partition {}".format(
            " / ".join(
                "{{{}}}".format(", ".join(str(c) for c in part))
                for part in self.partition
            )
        )

    def backward_map(
        self,
        tiling: Tiling,
        gps: Tuple[GriddedPerm, ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> GriddedPerm:
        if children is None:
            children = self.children(tiling)
        gps_to_combine = tuple(
            tiling.backward_map(gp) for gp, tiling in zip(gps, children)
        )
        temp = [
            ((cell[0], idx), (cell[1], val))
            for gp in gps_to_combine
            for (idx, val), cell in zip(enumerate(gp.patt), gp.pos)
        ]
        temp.sort()
        new_pos = [(idx[0], val[0]) for idx, val in temp]
        new_patt = Perm.to_standard(val for _, val in temp)
        return GriddedPerm(new_patt, new_pos)

    def forward_map(
        self,
        tiling: Tiling,
        gp: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm, ...]:
        if children is None:
            children = self.children(tiling)
        return tuple(
            tiling.forward_map(gp.get_gridded_perm_in_cells(part))
            for tiling, part in zip(children, self.partition)
        )

    def __str__(self) -> str:
        return "factor"

    def __repr__(self) -> str:
        return self.__class__.__name__ + "(paritition={}, workable={})".format(
            self.partition, self.workable
        )

    # JSON methods

    def to_jsonable(self) -> dict:
        """Return a dictionary form of the strategy."""
        d: dict = super().to_jsonable()
        d["partition"] = self.partition
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "FactorStrategy":
        partition = tuple(tuple(tuple(c) for c in p) for p in d["partition"])
        return cls(
            partition=partition,
            ignore_parent=d["ignore_parent"],
            workable=d["workable"],
        )


class FactorWithInterleavingStrategy(FactorStrategy):
    def constructor(self, tiling: Tiling) -> Constructor:
        raise NotImplementedError

    def backward_map(
        self,
        tiling: Tiling,
        gps: Tuple[GriddedPerm, ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> GriddedPerm:
        raise NotImplementedError

    def forward_map(
        self,
        tiling: Tiling,
        gp: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm, ...]:
        raise NotImplementedError


class FactorWithMonotoneInterleavingStrategy(FactorWithInterleavingStrategy):
    def constructor(self, tiling: Tiling) -> Constructor:
        raise NotImplementedError


class AllFactorStrategy(StrategyGenerator):

    FACTOR_ALGO_AND_CLASS = {
        None: (Factor, FactorStrategy),
        "monotone": (
            FactorWithMonotoneInterleaving,
            FactorWithMonotoneInterleavingStrategy,
        ),
        "all": (FactorWithInterleaving, FactorWithInterleavingStrategy),
    }

    def __init__(
        self,
        interleaving: Optional[str] = None,
        unions: bool = False,
        ignore_parent: bool = True,
        workable: bool = True,
    ) -> None:
        try:
            self.factor_algo, self.factor_class = self.FACTOR_ALGO_AND_CLASS[
                interleaving
            ]
        except KeyError:
            raise InvalidOperationError(
                "Invalid interleaving option. Must be in {}, used {}".format(
                    AllFactorStrategy.FACTOR_ALGO_AND_CLASS.keys(), interleaving
                )
            )
        self.unions = unions
        self.ignore_parent = ignore_parent
        self.workable = workable

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Strategy]:
        factor_algo = self.factor_algo(tiling)
        if factor_algo.factorable():
            min_comp = factor_algo.get_components()
            if self.unions:
                for partition in partitions_iterator(min_comp):
                    components = tuple(
                        tuple(chain.from_iterable(part)) for part in partition
                    )
                    yield self.factor_class(
                        components, ignore_parent=self.ignore_parent, workable=False
                    )
            yield self.factor_class(
                min_comp, ignore_parent=self.ignore_parent, workable=self.workable
            )

    def __str__(self) -> str:
        if self.factor_class is FactorStrategy:
            s = "factor"
        elif self.factor_class is FactorWithInterleavingStrategy:
            s = "factor with monotone interleaving"
        elif self.factor_class is FactorWithMonotoneInterleavingStrategy:
            s = "factor with interleaving"
        else:
            raise Exception("Invalid interleaving type")
        if self.unions:
            s = "unions of " + s
        return s

    def __repr__(self) -> str:
        if self.factor_class is FactorStrategy:
            interleaving = None
        elif self.factor_class is FactorWithInterleavingStrategy:
            interleaving = "all"
        elif self.factor_class is FactorWithMonotoneInterleavingStrategy:
            interleaving = "monotone"
        return "AllFactorStrategy(interleaving={}, unions={}, ignore_parent={}, workable={})".format(
            interleaving, self.ignore_parent, self.unions, self.workable
        )

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        if self.factor_class is FactorStrategy:
            interleaving = None
        elif self.factor_class is FactorWithInterleavingStrategy:
            interleaving = "all"
        elif self.factor_class is FactorWithMonotoneInterleavingStrategy:
            interleaving = "monotone"
        d["interleaving"] = interleaving
        d["unions"] = self.unions
        d["ignore_parent"] = self.ignore_parent
        d["workable"] = self.workable
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AllFactorStrategy":
        return cls(
            interleaving=d["interleaving"],
            unions=d["unions"],
            ignore_parent=d["ignore_parent"],
            workable=d["workable"],
        )
