from typing import Iterator, Optional, Tuple

from comb_spec_searcher import CartesianProductStrategy, Strategy, StrategyGenerator
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import (
    Factor,
    FactorWithInterleaving,
    FactorWithMonotoneInterleaving,
)


Cell = Tuple[int, int]


class FactorStrategy(CartesianProductStrategy):
    def __init__(
        self,
        partition: Optional[Tuple[Tuple[Cell, ...], ...]] = None,
        workable: bool = True,
        children: Optional[Tuple[Tiling, ...]] = None,
    ):
        if partition is None:
            self.partition = tuple(
                tuple(child.backward_cell_map()) for child in children
            )
        else:
            self.partition = sorted(partition)
        super().__init__(workable=workable)

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling, ...]:
        """
        # TODO: Taken from reducible factorisations function in Factor. Pick where.
        """
        return tuple(tiling.sub_tiling(cells) for cells in self.partition)

    def formal_step(self, union=False):
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


class FactorWithInterleavingStrategy(FactorStrategy):
    def constructor(self, tiling: Tiling):
        raise NotImplementedError


class FactorWithMonotoneInterleavingStrategy(FactorStrategy):
    def constructor(self, tiling: Tiling):
        raise NotImplementedError


class FactorStrategyGenerator(StrategyGenerator):

    factor_class = {
        None: FactorStrategy,
        "monotone": FactorWithInterleavingStrategy,
        "all": FactorWithMonotoneInterleavingStrategy,
    }

    def __init__(
        self,
        interleaving: Optional[str] = None,
        union: bool = False,
        workable: bool = True,
    ) -> None:
        assert (
            interleaving in FactorStrategy.factor_class
        ), "Invalid interleaving option. Must be in {}".format(
            FactorStrategy.factor_class.keys()
        )
        self.interleaving = interleaving
        self.union = union
        self.workable = workable

    def __call__(self, tiling: Tiling, **kwargs) -> Iterator[Strategy]:
        factor_algo = FactorStrategy.factor_class[self.interleaving](tiling)
        if factor_algo.factorable():
            yield factor_algo.factor_algo(workable=self.workable)
            if self.union:
                yield from factor_algo.all_union_rules(workable=False)

    def __str__(self) -> str:
        if self.interleaving is None:
            s = "factor"
        elif self.interleaving == "monotone":
            s = "factor with monotone interleaving"
        elif self.interleaving == "all":
            s = "factor with interleaving"
        else:
            raise Exception("Invalid interleaving type")
        if self.union:
            s = "unions of " + s
        return s

    def __repr__(self) -> str:
        return "FactorStrategy(interleaving={}, union={}, workable={})".format(
            self.interleaving, self.union, self.workable
        )

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["interleaving"] = self.interleaving
        d["union"] = self.union
        d["workable"] = self.workable
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "FactorStrategy":
        return cls(**d)
