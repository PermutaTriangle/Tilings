from typing import Iterable, List, Optional, Tuple

from comb_spec_searcher import DisjointUnionStrategy, StrategyGenerator
from tilings import GriddedPerm, Tiling
from tilings.algorithms import (
    AllObstructionInferral,
    ObstructionTransitivity,
    SubobstructionInferral,
)

__all__ = [
    "EmptyCellInferralStrategy",
    "ObstructionInferralStrategy",
    "ObstructionTransitivityStrategy",
    "SubobstructionInferral",
]


class ObstructionInferralStrategy(DisjointUnionStrategy[Tiling]):
    def __init__(self, gps: Iterable[GriddedPerm]):
        self.gps = tuple(sorted(gps))
        super().__init__(
            ignore_parent=True, inferrable=True, possibly_empty=False, workable=True,
        )

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling]:
        return (tiling.add_obstructions(self.gps),)

    def formal_step(self) -> str:
        """ Return a string describing the operation performed. """
        if all(len(gp) == 1 for gp in self.gps):
            empty_cells_str = ", ".join(map(str, (gp.pos[0] for gp in self.gps)))
            return "the cells {{{}}} are empty".format(empty_cells_str)
        return "added the obstructions {{{}}}".format(
            ", ".join(str(p) for p in self.gps),
        )

    def backward_map(
        self,
        tiling: Tiling,
        gps: Tuple[GriddedPerm, ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> GriddedPerm:
        if children is None:
            children = self.decomposition_function(tiling)
        return children[0].backward_map(gps[0])

    def forward_map(
        self,
        tiling: Tiling,
        gp: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm]:
        if children is None:
            children = self.decomposition_function(tiling)
        return (children[0].forward_map(gp),)

    def __repr__(self) -> str:
        return self.__class__.__name__ + "(gps={})".format(self.gps)

    def __str__(self) -> str:
        return self.formal_step()

    # JSON methods

    def to_jsonable(self) -> dict:
        """Return a dictionary form of the strategy."""
        d: dict = super().to_jsonable()
        d["gps"] = [gp.to_jsonable() for gp in self.gps]
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "ObstructionInferralStrategy":
        gps = [GriddedPerm.from_dict(gp) for gp in d["gps"]]
        return cls(gps=gps)


class AllObstructionInferralStrategy(StrategyGenerator[Tiling]):
    """
    A strategy used for adding obstruction that the tiling avoids, but not
    currently in the obstructions.

    Note: it isn't really a generator. This is utilised to avoid the need to
    recompute new_obs which is needed for the strategy.
    """

    def __init__(self, maxlen: int = 3):
        self.maxlen = maxlen
        super().__init__()

    def new_obs(self, tiling: Tiling) -> List[GriddedPerm]:
        """
        Returns the list of new obstructions that can be added to the tiling.
        """
        return AllObstructionInferral(tiling, self.maxlen).new_obs()

    def __call__(self, tiling: Tiling, **kwargs) -> List[Tiling]:
        """
        Return a tuple of tiling. The first one avoids all the pattern in the
        list while the other contain one of the patterns in the list.
        """
        gps = self.new_obs(tiling)
        if gps:
            return [ObstructionInferralStrategy(gps)]
        return []

    def to_jsonable(self):
        d = super().to_jsonable()
        d["maxlen"] = self.maxlen
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(maxlen=d["maxlen"])

    def __repr__(self):
        return "{}(maxlen={})".format(self.__class__.__name__, self.maxlen)

    def __str__(self):
        if self.maxlen == 1:
            return "empty cell inferral"
        return "obstruction inferral (max length is {})".format(self.maxlen)


class EmptyCellInferralStrategy(AllObstructionInferralStrategy):
    def __init__(self):
        super().__init__(maxlen=1)

    @classmethod
    def from_dict(cls, d):
        return cls()


class SubobstructionInferralStrategy(AllObstructionInferralStrategy):
    def __init__(self):
        super().__init__(maxlen=None)

    def new_obs(self, tiling: Tiling) -> List[GriddedPerm]:
        """
        Returns the list of new obstructions that can be added to the tiling.
        """
        return SubobstructionInferral(tiling).new_obs()

    @classmethod
    def from_dict(cls, d):
        return cls()

    def __repr__(self):
        return self.__class__.__name__ + "()"

    def __str__(self):
        return "subobstruction inferral"


class ObstructionTransitivityStrategy(AllObstructionInferralStrategy):
    """
    The obstruction transitivity strategy.

    The obstruction transitivity considers all length 2 obstructions with both
    points in the same row or some column. By considering these length 2
    obstructions in similar manner as the row and column separation, as
    inequality relations. When the obstructions use a positive cell,
    transitivity applies, i.e. if a < b < c and b is positive, then a < c.
    """

    def __init__(self):
        super().__init__(maxlen=2)

    def new_obs(self, tiling: Tiling):
        return ObstructionTransitivity(tiling).new_obs()

    def __str__(self) -> str:
        return "obstruction transitivity"

    def __repr__(self) -> str:
        return "ObstructionTransitivityStrategy()"

    @classmethod
    def from_dict(cls, d: dict) -> "ObstructionTransitivityStrategy":
        return cls()
