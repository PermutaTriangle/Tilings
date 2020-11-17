from typing import Callable, DefaultDict, Dict, Iterator, List, Optional, Tuple

from comb_spec_searcher.strategies.strategy import (
    DisjointUnionStrategy,
    StrategyFactory,
)
from tilings import GriddedPerm, Tiling
from tilings.algorithms import (
    get_col_info,
    gp_slide,
    gp_slide_inverse,
    slidable_pairs,
    slide_assumption,
    slide_column,
)


def _tiling_identity_map(tiling: Tiling) -> Tiling:
    return tiling


def _tiling_reverse(tiling: Tiling) -> Tiling:
    t: Tiling = tiling.reverse()
    return t


def _tiling_rotate90(tiling: Tiling) -> Tiling:
    t: Tiling = tiling.rotate90()
    return t


def _tiling_rotate90_inverse(tiling: Tiling) -> Tiling:
    t: Tiling = tiling.rotate270()
    return t


def _tiling_rotate90_and_reverse(tiling: Tiling) -> Tiling:
    t: Tiling = tiling.rotate90().reverse()
    return t


def _tiling_rotate90_and_reverse_inverse(tiling: Tiling) -> Tiling:
    t: Tiling = tiling.reverse().rotate270()
    return t


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
            _tiling_reverse,
            _tiling_reverse,
            _gp_reverse(c),
            _gp_reverse(c),
        )

    @classmethod
    def rotate90(cls, r: int) -> "_AdditionalMaps":
        return _AdditionalMaps(
            _tiling_rotate90,
            _tiling_rotate90_inverse,
            _gp_rotate90(r),
            _gp_rotate90_inverse(r),
        )

    @classmethod
    def rotate90_and_reverse(cls, r: int) -> "_AdditionalMaps":
        return _AdditionalMaps(
            _tiling_rotate90_and_reverse,
            _tiling_rotate90_and_reverse_inverse,
            _gp_rotate90_and_reverse(r),
            _gp_rotate90_and_reverse_inverse(r),
        )


class SlidingStrategy(DisjointUnionStrategy[Tiling, GriddedPerm]):
    """
    A class for a specific slidding strategy. The init probably gets the index of both
    column you slidding.
    """

    def __init__(
        self,
        av_12_column: int,
        av_123_column: int,
        col_info: DefaultDict[int, DefaultDict[int, Dict[GriddedPerm, List[int]]]],
        maps: _AdditionalMaps = _AdditionalMaps(),
    ):
        super().__init__(possibly_empty=False)
        self.av_12 = av_12_column
        self.av_123 = av_123_column
        self.col_info = col_info
        self.maps = maps

    def decomposition_function(self, tiling: Tiling) -> Tuple[Tiling]:
        """Return the slidded tiling if it slides, otherwise None."""
        return (
            self.maps.t_inv(
                slide_column(
                    self.maps.t_map(tiling), self.av_12, self.av_123, self.col_info
                )
            ),
        )

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
                    gp_slide_inverse(self.maps.g_map(gp), self.av_12, self.av_123)
                )
                for gp in gps
                if gp is not None
            )
        else:
            yield from (
                self.maps.g_inv(gp_slide(self.maps.g_map(gp), self.av_123, self.av_12))
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
                self.maps.g_inv(gp_slide(self.maps.g_map(gp), self.av_123, self.av_12)),
            )
        return (
            self.maps.g_inv(
                gp_slide_inverse(self.maps.g_map(gp), self.av_12, self.av_123)
            ),
        )

    @classmethod
    def from_dict(cls, d: dict) -> "SlidingStrategy":
        raise NotImplementedError()

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
                    slide_assumption(ass, self.av_12, self.av_123)
                )
                for ass in comb_class.assumptions
            },
        )


class SlidingFactory(StrategyFactory[Tiling]):
    """
    A strategy factory is producing all the valid strategies of a given type that can
    apply to the given tiling.

    Here you want the call the method to return all the valid sliding strategy for the
    given tiling.
    """

    def __init__(self, use_symmetries: bool = False):
        super().__init__()
        self.use_symmetries = use_symmetries

    def __call__(self, comb_class: Tiling, **kwargs) -> Iterator[SlidingStrategy]:
        if comb_class.dimensions[0] > 1 and comb_class.dimensions[1] == 1:
            col_info = get_col_info(comb_class)
            for pair in slidable_pairs(comb_class, col_info):
                print(comb_class, flush=True)
                yield SlidingStrategy(*pair, col_info)
        if self.use_symmetries:
            yield from SlidingFactory._symmetries(comb_class)

    @staticmethod
    def _symmetries(comb_class: Tiling) -> Iterator[SlidingStrategy]:
        c, r = comb_class.dimensions
        if r == 1 and c > 1:
            tiling = comb_class.rotate180().reverse()
            col_info = get_col_info(tiling)
            for pair in slidable_pairs(tiling, col_info):
                yield SlidingStrategy(*pair, col_info, _AdditionalMaps.reverse(c))
        elif r > 1 and c == 1:
            tiling = comb_class.rotate90()
            col_info = get_col_info(tiling)
            for pair in slidable_pairs(tiling, col_info):
                yield SlidingStrategy(*pair, col_info, _AdditionalMaps.rotate90(r))
            tiling = tiling.rotate180.reverse()
            col_info = get_col_info(tiling)
            for pair in slidable_pairs(tiling, col_info):
                yield SlidingStrategy(
                    *pair, col_info, _AdditionalMaps.rotate90_and_reverse(r)
                )

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return "Sliding"

    @classmethod
    def from_dict(cls, d: dict) -> "SlidingFactory":
        """
        Return the strategy from the json representation.
        """
        raise NotImplementedError()
