from itertools import chain
from typing import Iterator, Optional, Tuple

from comb_spec_searcher import CartesianProductStrategy, Strategy, StrategyGenerator
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


class FactorStrategy(CartesianProductStrategy):
    def __init__(
        self,
        partition: Optional[Tuple[Tuple[Cell, ...], ...]],
        workable: bool = True,
        children: Optional[Tuple[Tiling, ...]] = None,
    ):
        self.partition = tuple(sorted(partition))
        super().__init__(workable=workable)

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling, ...]:
        """
        # TODO: Taken from reducible factorisations function in Factor. Pick where.
        """
        return tuple(tiling.sub_tiling(cells) for cells in self.partition)

    def formal_step(self):
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

    def __str__(self):
        return "factor"

    def __repr__(self):
        return self.__class__.__name__ + "()"


class FactorWithInterleavingStrategy(FactorStrategy):
    def constructor(self, tiling: Tiling):
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
    def constructor(self, tiling: Tiling):
        raise NotImplementedError


class AllFactorStrategy(StrategyGenerator):

    factor_algo_and_classes = {
        None: (Factor, FactorStrategy),
        "monotone": (FactorWithInterleaving, FactorWithInterleavingStrategy),
        "all": (FactorWithMonotoneInterleaving, FactorWithMonotoneInterleavingStrategy),
    }

    def __init__(
        self,
        interleaving: Optional[str] = None,
        unions: bool = False,
        workable: bool = True,
    ) -> None:
        try:
            self.factor_algo, self.factor_class = self.factor_algo_and_classes[
                interleaving
            ]
        except KeyError:
            raise InvalidOperationError(
                "Invalid interleaving option. Must be in {}".format(
                    FactorStrategy.factor_classes.keys()
                )
            )
        self.unions = unions
        self.workable = workable

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Strategy]:
        factor_algo = self.factor_algo(tiling)
        if factor_algo.factorable():
            min_comp = factor_algo.get_components()
            if self.unions:
                min_comp = tuple(tuple(x) for x in min_comp)
                for partition in partitions_iterator(min_comp):
                    partition = tuple(
                        tuple(x for x in chain(*part)) for part in partition
                    )
                    yield self.factor_class(partition, workable=False)
            yield self.factor_class(min_comp, workable=self.workable)

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
        return "AllFactorStrategy(interleaving={}, unions={}, workable={})".format(
            self.interleaving, self.unions, self.workable
        )

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["interleaving"] = self.interleaving
        d["unions"] = self.unions
        d["workable"] = self.workable
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AllFactorStrategy":
        return cls(**d)
