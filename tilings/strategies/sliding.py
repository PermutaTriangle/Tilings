from typing import Callable, Dict, Iterator, Optional, Tuple

from comb_spec_searcher.strategies.strategy import (
    DisjointUnionStrategy,
    StrategyFactory,
)
from tilings import GriddedPerm, Tiling
from tilings.algorithms import Sliding


def _tiling_identity_map(tiling: Tiling) -> Tiling:
    return tiling


def _gp_identity_map(gp: GriddedPerm) -> GriddedPerm:
    return gp


def _gp_reverse(c: int) -> Callable[[GriddedPerm], GriddedPerm]:
    def _tmp_func(gp: GriddedPerm) -> GriddedPerm:
        return GriddedPerm(gp.patt.reverse(), ((c - x - 1, 0) for x, _ in gp.pos))

    return _tmp_func


def _gp_rotate90(r: int) -> Callable[[GriddedPerm], GriddedPerm]:
    def _tmp_func(gp: GriddedPerm) -> GriddedPerm:
        return GriddedPerm(gp.patt.rotate(), ((y, 0) for _, y in gp.pos))

    return _tmp_func


def _gp_rotate90_inverse(r: int) -> Callable[[GriddedPerm], GriddedPerm]:
    def _tmp_func(gp: GriddedPerm) -> GriddedPerm:
        return GriddedPerm(gp.patt.rotate(-1), ((0, x) for x, _ in gp.pos))

    return _tmp_func


def _gp_rotate90_and_reverse(r: int) -> Callable[[GriddedPerm], GriddedPerm]:
    def _tmp_func(gp: GriddedPerm) -> GriddedPerm:
        return GriddedPerm(
            gp.patt.rotate(1).reverse(), ((r - y - 1, 0) for _, y in gp.pos)
        )

    return _tmp_func


def _gp_rotate90_and_reverse_inverse(r: int) -> Callable[[GriddedPerm], GriddedPerm]:
    def _tmp_func(gp: GriddedPerm) -> GriddedPerm:
        return GriddedPerm(
            gp.patt.reverse().rotate(-1), ((0, r - x - 1) for x, _ in gp.pos)
        )

    return _tmp_func


class _AdditionalMaps:
    def __init__(
        self,
        identifier: int = 0,
        param: int = 0,
        t_inv: Callable[[Tiling], Tiling] = _tiling_identity_map,
        g_map: Callable[[GriddedPerm], GriddedPerm] = _gp_identity_map,
        g_inv: Callable[[GriddedPerm], GriddedPerm] = _gp_identity_map,
    ) -> None:
        self.identifier = identifier
        self.param = param
        self.t_inv = t_inv
        self.g_map = g_map
        self.g_inv = g_inv

    @classmethod
    def reverse(cls, c: int) -> "_AdditionalMaps":
        return _AdditionalMaps(
            1,
            c,
            Tiling.reverse,
            _gp_reverse(c),
            _gp_reverse(c),
        )

    @classmethod
    def rotate90(cls, r: int) -> "_AdditionalMaps":
        return _AdditionalMaps(
            2,
            r,
            Tiling.rotate270,
            _gp_rotate90(r),
            _gp_rotate90_inverse(r),
        )

    @classmethod
    def rotate90_and_reverse(cls, r: int) -> "_AdditionalMaps":
        return _AdditionalMaps(
            3,
            r,
            Tiling.antidiagonal,
            _gp_rotate90_and_reverse(r),
            _gp_rotate90_and_reverse_inverse(r),
        )

    def to_jsonable(self) -> dict:
        """Return a dictionary form of the strategy."""
        return {"identifier": self.identifier, "param": self.param}

    @classmethod
    def from_dict(cls, d: dict) -> "_AdditionalMaps":
        """Create instance from dictionary."""
        _id = d["identifier"]
        if _id == 0:
            return cls()
        if _id == 1:
            return cls.reverse(d["param"])
        if _id == 2:
            return cls.rotate90(d["param"])
        return cls.rotate90_and_reverse(d["param"])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.identifier == other.identifier


class SlidingStrategy(DisjointUnionStrategy[Tiling, GriddedPerm]):
    """
    A class for a specific slidding strategy. The init gets the index of both
    column you slidding.
    """

    def __init__(
        self,
        av_12_column: int,
        av_123_column: int,
        sliding: Sliding,
        maps: _AdditionalMaps = _AdditionalMaps(),
    ):
        super().__init__(possibly_empty=False)
        self.av_12 = av_12_column
        self.av_123 = av_123_column
        self.sliding = sliding
        self.maps = maps

    def decomposition_function(self, _tiling: Tiling) -> Tuple[Tiling]:
        """Return the slidded tiling if it slides, otherwise None."""

        return (self.maps.t_inv(self.sliding.slide_column(self.av_12, self.av_123)),)

    def formal_step(self) -> str:
        return f"slide {self.av_123} through {self.av_12}"

    def backward_map(
        self,
        tiling: Tiling,
        gps: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        if self.av_12 < self.av_123:
            yield from (
                self.maps.g_inv(
                    Sliding.slide_gp_inverse(
                        self.maps.g_map(gp), self.av_12, self.av_123
                    )
                )
                for gp in gps
                if gp is not None
            )
        else:
            yield from (
                self.maps.g_inv(
                    Sliding.slide_gp(self.maps.g_map(gp), self.av_123, self.av_12)
                )
                for gp in gps
                if gp is not None
            )

    def forward_map(
        self,
        tiling: Tiling,
        gp: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[GriddedPerm]:
        if self.av_123 < self.av_12:
            return (
                self.maps.g_inv(
                    Sliding.slide_gp(self.maps.g_map(gp), self.av_123, self.av_12)
                ),
            )
        return (
            self.maps.g_inv(
                Sliding.slide_gp_inverse(self.maps.g_map(gp), self.av_12, self.av_123)
            ),
        )

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str], ...]:
        if not comb_class.extra_parameters:
            return super().extra_parameters(comb_class, children)
        if children is None:
            children = self.decomposition_function(comb_class)
        child = children[0]
        return (
            {
                comb_class.get_assumption_parameter(
                    ass
                ): child.get_assumption_parameter(
                    Sliding.slide_assumption(ass, self.av_12, self.av_123)
                )
                for ass in comb_class.assumptions
            },
        )

    def to_jsonable(self) -> dict:
        """Return a dictionary form of the strategy."""
        return {
            "class_module": "tilings.strategies.sliding",
            "strategy_class": "SlidingStrategy",
            "av_12_column": self.av_12,
            "av_123_column": self.av_123,
            "tiling": self.sliding.tiling.to_jsonable(),
            "maps": self.maps.to_jsonable(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SlidingStrategy":
        return cls(
            d["av_12_column"],
            d["av_123_column"],
            Sliding(Tiling.from_dict(d["tiling"])),
            _AdditionalMaps.from_dict(d["maps"]),
        )


class SlidingFactory(StrategyFactory[Tiling]):
    """A strategy factory that produces all valid slides for a tiling."""

    def __init__(self, use_symmetries: bool = False):
        super().__init__()
        self.use_symmetries = use_symmetries

    def __call__(self, comb_class: Tiling, **kwargs) -> Iterator[SlidingStrategy]:
        if comb_class.dimensions[0] > 1 and comb_class.dimensions[1] == 1:
            sliding = Sliding(comb_class)
            for pair in sliding.slidable_pairs():
                yield SlidingStrategy(*pair, sliding)
        if self.use_symmetries:
            yield from SlidingFactory._symmetries(comb_class)

    @staticmethod
    def _symmetries(comb_class: Tiling) -> Iterator[SlidingStrategy]:
        c, r = comb_class.dimensions
        if r == 1 and c > 1:
            tiling = comb_class.reverse()
            sliding = Sliding(tiling)
            for pair in sliding.slidable_pairs():
                yield SlidingStrategy(*pair, sliding, _AdditionalMaps.reverse(c))
        elif r > 1 and c == 1:
            tiling = comb_class.rotate90()
            sliding = Sliding(tiling)
            for pair in sliding.slidable_pairs():
                yield SlidingStrategy(*pair, sliding, _AdditionalMaps.rotate90(r))
            tiling = tiling.reverse()
            sliding = Sliding(tiling)
            for pair in sliding.slidable_pairs():
                yield SlidingStrategy(
                    *pair, sliding, _AdditionalMaps.rotate90_and_reverse(r)
                )

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return "Sliding"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["use_symmetries"] = self.use_symmetries
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "SlidingFactory":
        """
        Return the strategy from the json representation.
        """
        return cls(**d)
