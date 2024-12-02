import itertools
from typing import Iterator, Optional, Tuple

from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.strategies import Constructor, Rule, Strategy, StrategyFactory
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms.map import RowColMap
from tilings.strategies.fusion import FusionStrategy


def all_gap_vectors(length: int, max_norm: int) -> Iterator[Tuple[int, ...]]:
    if length == 0:
        yield ()
    else:
        for n in range(max_norm + 1):
            for v in all_gap_vectors(length - 1, max_norm - n):
                yield (n,) + v


def is_good_gap_vector(gv: Tuple[int, ...]):
    # Change to 2 for ignoring vector that makes cell empty
    return sum(gv) > 1


def good_gap_vectors(length: int, max_norm: int) -> Iterator[Tuple[int, ...]]:
    return filter(is_good_gap_vector, all_gap_vectors(length, max_norm))


class ForbidGapVectorStrategy(Strategy[Tiling, GriddedPerm]):
    """
    A strategy that restricts the set of gap vector for which you have permutation on
    the tiling.

    The ouptut of the strategy is expected to be fusable with regular fusion.
    """

    def __init__(self, gap_vectors: Tuple[Tuple[int, ...], ...], child: Tiling):
        super().__init__(workable=False)
        self.gap_vectors = gap_vectors
        self.child = child

    def to_jsonable(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, d: dict) -> "ForbidGapVectorStrategy":
        raise NotImplementedError

    def can_be_equivalent(self) -> bool:
        return False

    def is_two_way(self, comb_class: Tiling) -> bool:
        return False

    def is_reversible(self, comb_class: Tiling) -> bool:
        return False

    def shifts(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[int, ...]:
        return (0,)

    def expected_parent(self) -> Tiling:
        """
        Return the tiling that is obtained by forbidding the gap vectors on the child
        tiling.
        """
        new_obs = itertools.chain.from_iterable(map(self.sk_from_gap, self.gap_vectors))
        return self.child.add_obstructions(new_obs)

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling]:
        if self.expected_parent() == comb_class:
            return (self.child,)
        raise StrategyDoesNotApply("Dimension don't match with gap vectors.")

    def formal_step(self) -> str:
        return f"Forbid gap vectors {', '.join(map(str, self.gap_vectors))}"

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], ...]:
        raise NotImplementedError

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
        left_points: Optional[int] = None,
    ) -> Iterator[GriddedPerm]:
        """
        The backward direction of the underlying bijection used for object
        generation and sampling.
        """
        raise NotImplementedError

    def constructor(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ):
        raise NotImplementedError

    def reverse_constructor(  # pylint: disable=no-self-use
        self,
        idx: int,
        comb_class: Tiling,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Constructor:
        raise NotImplementedError

    def sk_from_gap(self, gap_vector: Tuple[int, ...]) -> Iterator[GriddedPerm]:
        col_pos_seq = tuple(
            itertools.chain.from_iterable(
                itertools.repeat(n, num) for n, num in enumerate(gap_vector)
            )
        )
        for perm in Perm.of_length(len(col_pos_seq)):
            yield GriddedPerm(perm, ((c, 0) for c in col_pos_seq))


class EnumerationSchemeRecursionFactory(StrategyFactory):
    def __init__(self, max_norm: int, max_num_vec: int) -> None:
        self.max_norm = max_norm
        self.max_num_vec = max_num_vec

    def __call__(self, comb_class: Tiling) -> Iterator[Rule[Tiling, GriddedPerm]]:
        unfused_tilings = []
        for tiling, strat in self.fusion_strategy(comb_class):
            unfused_tilings.append(tiling)
            yield strat(tiling)
        n_row, n_col = comb_class.dimensions
        gap_vectors = list(
            good_gap_vectors(comb_class.dimensions[0] + 1, self.max_norm)
        )
        print(gap_vectors)
        for n in range(1, self.max_num_vec + 1):
            for vec_set in itertools.combinations(gap_vectors, n):
                for t in unfused_tilings:
                    forbid_strat = ForbidGapVectorStrategy(vec_set, t)
                    parent = forbid_strat.expected_parent()
                    yield forbid_strat(parent, (t,))

    def fusion_strategy(
        self, comb_class: Tiling
    ) -> Iterator[Tuple[Tiling, FusionStrategy]]:
        """
        Iterator of pair tiling, fusion strategy for all the fusion rule we want to
        create.
        """
        num_col, num_row = comb_class.dimensions
        assert num_row == 1
        for col in range(num_col):
            fuse_col_map = {i: i for i in range(num_col)}
            fuse_col_map.update({i: i - 1 for i in range(col + 1, num_col + 1)})
            fuse_map = RowColMap(
                row_map={0: 0}, col_map=fuse_col_map, is_identity=False
            )
            fusion_strat = FusionStrategy(col_idx=col)
            yield fuse_map.preimage_tiling(comb_class), fusion_strat

    def __repr__(self) -> str:
        return "Repr"

    def __str__(self) -> str:
        return "enumeration recursion"

    def from_dict(self, d):
        raise NotImplementedError
