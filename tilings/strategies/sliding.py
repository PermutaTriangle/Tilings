from typing import Callable, Dict, Iterator, Optional, Tuple

from comb_spec_searcher.strategies import Rule
from comb_spec_searcher.strategies.strategy import (
    DisjointUnionStrategy,
    StrategyFactory,
)
from tilings import GriddedPerm, Tiling
from tilings.algorithms import Sliding

_NO_SYMMETRY, _ROTATE, _REVERSE, _ROTATE_AND_REVERSE = range(4)


def _tiling_identity_map(tiling: Tiling) -> Tiling:
    return tiling


def _gp_identity_map(gp: GriddedPerm) -> GriddedPerm:
    return gp


def _gp_reverse(c: int) -> Callable[[GriddedPerm], GriddedPerm]:
    def _tmp_func(gp: GriddedPerm) -> GriddedPerm:
        return GriddedPerm(
            gp.patt.reverse(), ((c - x - 1, 0) for x, _ in reversed(gp.pos))
        )

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
        t_map: Callable[[Tiling], Tiling] = _tiling_identity_map,
        t_inv: Callable[[Tiling], Tiling] = _tiling_identity_map,
        g_map: Callable[[GriddedPerm], GriddedPerm] = _gp_identity_map,
        g_inv: Callable[[GriddedPerm], GriddedPerm] = _gp_identity_map,
    ) -> None:
        self.t_map = t_map
        self.t_inv = t_inv
        self.g_map = g_map
        self.g_inv = g_inv

    @classmethod
    def reverse(cls, c: int) -> "_AdditionalMaps":
        return _AdditionalMaps(
            Tiling.reverse,
            Tiling.reverse,
            _gp_reverse(c),
            _gp_reverse(c),
        )

    @classmethod
    def rotate90(cls, r: int) -> "_AdditionalMaps":
        return _AdditionalMaps(
            Tiling.rotate90,
            Tiling.rotate270,
            _gp_rotate90(r),
            _gp_rotate90_inverse(r),
        )

    @classmethod
    def rotate90_and_reverse(cls, r: int) -> "_AdditionalMaps":
        return _AdditionalMaps(
            Tiling.antidiagonal,
            Tiling.antidiagonal,
            _gp_rotate90_and_reverse(r),
            _gp_rotate90_and_reverse_inverse(r),
        )

    @classmethod
    def enum_to_map(cls, symmetry_type: int, tiling_size: int) -> "_AdditionalMaps":
        if symmetry_type == _NO_SYMMETRY:
            return cls()
        if symmetry_type == _REVERSE:
            return cls.reverse(tiling_size)
        if symmetry_type == _ROTATE:
            return cls.rotate90(tiling_size)
        if symmetry_type == _ROTATE_AND_REVERSE:
            return cls.rotate90_and_reverse(tiling_size)
        raise ValueError("Unknown symmetry type")

    @staticmethod
    def enum_to_str(symmetry_type: int) -> str:
        if symmetry_type == _NO_SYMMETRY:
            return "no symmetry"
        if symmetry_type == _REVERSE:
            return "reverse"
        if symmetry_type == _ROTATE:
            return "rotate"
        if symmetry_type == _ROTATE_AND_REVERSE:
            return "antidiagonal"
        raise ValueError("Unknown symmetry type")


class SlidingStrategy(DisjointUnionStrategy[Tiling, GriddedPerm]):
    """
    A class for a specific slidding strategy. The init gets the index of both
    column you slidding.
    """

    def __init__(self, av_12: int, av_123: int, symmetry_type: int):
        super().__init__(possibly_empty=False)
        self.av_12 = av_12
        self.av_123 = av_123
        self.symmetry_type = symmetry_type

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling]:
        """Return the slidded tiling if it slides, otherwise None."""
        maps = _AdditionalMaps.enum_to_map(self.symmetry_type, max(tiling.dimensions))
        sliding = Sliding(maps.t_map(tiling))
        return (maps.t_inv(sliding.slide_column(self.av_12, self.av_123)),)

    def formal_step(self) -> str:
        sym = _AdditionalMaps.enum_to_str(self.symmetry_type)
        return f"slide {self.av_123} through {self.av_12} after applying {sym}"

    def backward_map(
        self,
        tiling: Tiling,
        gps: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        maps = _AdditionalMaps.enum_to_map(self.symmetry_type, max(tiling.dimensions))
        if self.av_12 < self.av_123:
            yield from (
                maps.g_inv(Sliding.slide_gp(maps.g_map(gp), self.av_12, self.av_123))
                for gp in gps
                if gp is not None
            )
        else:
            yield from (
                maps.g_inv(
                    Sliding.slide_gp_inverse(maps.g_map(gp), self.av_123, self.av_12)
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
        maps = _AdditionalMaps.enum_to_map(self.symmetry_type, max(tiling.dimensions))
        if self.av_123 < self.av_12:
            return (
                maps.g_inv(Sliding.slide_gp(maps.g_map(gp), self.av_123, self.av_12)),
            )
        return (
            maps.g_inv(
                Sliding.slide_gp_inverse(maps.g_map(gp), self.av_12, self.av_123)
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
        maps = _AdditionalMaps.enum_to_map(
            self.symmetry_type, max(comb_class.dimensions)
        )
        return (
            {
                comb_class.get_assumption_parameter(
                    ass
                ): child.get_assumption_parameter(
                    Sliding.slide_assumption(
                        ass, self.av_12, self.av_123, maps.g_map, maps.g_inv
                    )
                )
                for ass in comb_class.assumptions
            },
        )

    def to_jsonable(self) -> dict:
        """Return a dictionary form of the strategy."""
        return {
            "class_module": "tilings.strategies.sliding",
            "strategy_class": "SlidingStrategy",
            "av_12": self.av_12,
            "av_123": self.av_123,
            "symmetry_type": self.symmetry_type,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SlidingStrategy":
        return cls(
            d["av_12"],
            d["av_123"],
            d["symmetry_type"],
        )

    def __str__(self) -> str:
        return self.formal_step()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(av_12={self.av_12}, av_123={self.av_123}, "
            f"symmetry_type={self.symmetry_type})"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False
        return all(
            (
                self.av_12 == other.av_12,
                self.av_123 == other.av_123,
                self.symmetry_type == other.symmetry_type,
            )
        )


class SlidingFactory(StrategyFactory[Tiling]):
    """A strategy factory that produces all valid slides for a tiling."""

    def __init__(self, use_symmetries: bool = False):
        super().__init__()
        self.use_symmetries = use_symmetries

    def __call__(self, comb_class: Tiling) -> Iterator[Rule]:
        if comb_class.dimensions[0] > 1 and comb_class.dimensions[1] == 1:
            sliding = Sliding(comb_class)
            for pair in sliding.slidable_pairs():
                child = (sliding.slide_column(*pair),)
                yield SlidingStrategy(*pair, _NO_SYMMETRY)(comb_class, child)
        if self.use_symmetries:
            yield from SlidingFactory._symmetries(comb_class)

    @staticmethod
    def _symmetries(comb_class: Tiling) -> Iterator[Rule]:
        c, r = comb_class.dimensions
        if r == 1 and c > 1:
            tiling = comb_class.reverse()
            sliding = Sliding(tiling)
            for pair in sliding.slidable_pairs():
                maps = _AdditionalMaps.enum_to_map(_REVERSE, c)
                child = (maps.t_inv(sliding.slide_column(*pair)),)
                yield SlidingStrategy(*pair, _REVERSE)(comb_class, child)
        elif r > 1 and c == 1:
            tiling = comb_class.rotate90()
            sliding = Sliding(tiling)
            for pair in sliding.slidable_pairs():
                maps = _AdditionalMaps.enum_to_map(_ROTATE, r)
                child = (maps.t_inv(sliding.slide_column(*pair)),)
                yield SlidingStrategy(*pair, _ROTATE)(comb_class, child)
            tiling = tiling.reverse()
            sliding = Sliding(tiling)
            for pair in sliding.slidable_pairs():
                maps = _AdditionalMaps.enum_to_map(_ROTATE_AND_REVERSE, r)
                child = (maps.t_inv(sliding.slide_column(*pair)),)
                yield SlidingStrategy(*pair, _ROTATE_AND_REVERSE)(comb_class, child)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(use_symmetries={self.use_symmetries})"

    def __str__(self) -> str:
        return f"Sliding{' (with symmetries)' if self.use_symmetries else ''}"

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
