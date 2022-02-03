from itertools import chain
from typing import Dict, Iterator, Optional, Tuple

from comb_spec_searcher import DisjointUnionStrategy, StrategyFactory
from comb_spec_searcher.exception import StrategyDoesNotApply
from tilings import GriddedPerm, Tiling, TrackingAssumption
from tilings.algorithms import Fusion


class SlidingStrategy(DisjointUnionStrategy[Tiling, GriddedPerm]):
    """
    A strategy that slides column idx and idx + 1.
    """

    def __init__(self, idx: int):
        super().__init__()
        self.idx = idx

    def decomposition_function(self, comb_class: Tiling) -> Tuple[Tiling]:
        return (
            Tiling(
                self.slide_gps(comb_class.obstructions),
                map(self.slide_gps, comb_class.requirements),
                [
                    TrackingAssumption(self.slide_gps(ass.gps))
                    for ass in comb_class.assumptions
                ],
            ),
        )

    def formal_step(self) -> str:
        return f"Sliding index {self.idx}"

    def backward_map(
        self,
        comb_class: Tiling,
        objs: Tuple[Optional[GriddedPerm], ...],
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Iterator[GriddedPerm]:
        # if children is None:
        #     children = self.decomposition_function(comb_class)
        # idx = DisjointUnionStrategy.backward_map_index(objs)
        # yield children[idx].backward_map.map_gp(cast(GriddedPerm, objs[idx]))
        raise NotImplementedError

    def forward_map(
        self,
        comb_class: Tiling,
        obj: GriddedPerm,
        children: Optional[Tuple[Tiling, ...]] = None,
    ) -> Tuple[Optional[GriddedPerm], Optional[GriddedPerm]]:
        # if children is None:
        #     children = self.decomposition_function(comb_class)
        # if obj.avoids(*self.gps):
        #     return (children[0].forward_map.map_gp(obj), None)
        # return (None, children[1].forward_map.map_gp(obj))
        raise NotImplementedError

    def extra_parameters(
        self, comb_class: Tiling, children: Optional[Tuple[Tiling, ...]] = None
    ) -> Tuple[Dict[str, str], ...]:
        if not comb_class.extra_parameters:
            return super().extra_parameters(comb_class, children)
        if children is None:
            children = self.decomposition_function(comb_class)
            if children is None:
                raise StrategyDoesNotApply("Strategy does not apply")
        child = children[0]
        return (
            {
                comb_class.get_assumption_parameter(
                    ass
                ): child.get_assumption_parameter(
                    TrackingAssumption(self.slide_gps(ass.gps))
                )
                for ass in comb_class.assumptions
            },
        )

    def slide_gp(self, gp: GriddedPerm) -> GriddedPerm:
        pos = sorted(
            x if x < self.idx or x > self.idx + 1 else x + 1 if x == self.idx else x - 1
            for x, _ in gp.pos
        )
        return GriddedPerm(gp.patt, ((x, 0) for x in pos))

    def slide_gps(self, gps: Tuple[GriddedPerm, ...]) -> Tuple[GriddedPerm, ...]:
        return tuple(map(self.slide_gp, gps))

    def from_dict(cls, d: dict):
        return cls()


class SlidingFactory(StrategyFactory[Tiling]):
    def __call__(self, comb_class: Tiling) -> Iterator[SlidingStrategy]:
        if comb_class.dimensions[1] == 1 and not comb_class.requirements:
            for col in range(comb_class.dimensions[0] - 1):
                local_cells = (
                    comb_class.cell_basis()[(col, 0)][0],
                    comb_class.cell_basis()[(col + 1, 0)][0],
                )
                if (
                    len(local_cells[0]) == 1
                    and len(local_cells[0]) == 1
                    and (
                        (
                            local_cells[0][0].is_increasing()
                            and local_cells[1][0].is_increasing()
                        )
                        or (
                            (
                                local_cells[0][0].is_decreasing()
                                and local_cells[1][0].is_decreasing()
                            )
                        )
                    )
                ):
                    shortest = (
                        col
                        if len(local_cells[0][0]) <= len(local_cells[1][0])
                        else col + 1
                    )
                    algo = Fusion(comb_class, col_idx=col)
                    fused_obs = tuple(
                        algo.fuse_gridded_perm(gp)
                        for gp in comb_class.obstructions
                        if not all(x == shortest for x, _ in gp.pos)
                    )
                    unfused_obs = tuple(
                        chain.from_iterable(
                            algo.unfuse_gridded_perm(gp) for gp in fused_obs
                        )
                    )
                    if comb_class == comb_class.add_obstructions(unfused_obs):
                        yield SlidingStrategy(col)

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def __str__(self):
        return "sliding"

    @classmethod
    def from_dict(cls, d: dict):
        return cls()


if __name__ == "__main__":
    from permuta import Perm
    from tilings import Tiling

    t = Tiling.from_dict(
        {
            "class_module": "tilings.tiling",
            "comb_class": "Tiling",
            "obstructions": [
                {"patt": Perm((0, 1, 2)), "pos": ((1, 0), (1, 0), (1, 0))},
                {"patt": Perm((0, 1, 2, 3)), "pos": ((0, 0), (0, 0), (0, 0), (0, 0))},
                {"patt": Perm((0, 1, 2, 3)), "pos": ((0, 0), (0, 0), (0, 0), (1, 0))},
                {"patt": Perm((0, 1, 2, 3)), "pos": ((0, 0), (0, 0), (0, 0), (2, 0))},
                {"patt": Perm((0, 1, 2, 3)), "pos": ((0, 0), (0, 0), (1, 0), (1, 0))},
                {"patt": Perm((0, 1, 2, 3)), "pos": ((0, 0), (0, 0), (1, 0), (2, 0))},
                {"patt": Perm((0, 1, 2, 3)), "pos": ((0, 0), (0, 0), (2, 0), (2, 0))},
                {"patt": Perm((0, 1, 2, 3)), "pos": ((0, 0), (1, 0), (1, 0), (2, 0))},
                {"patt": Perm((0, 1, 2, 3)), "pos": ((0, 0), (1, 0), (2, 0), (2, 0))},
                {"patt": Perm((0, 1, 2, 3)), "pos": ((0, 0), (2, 0), (2, 0), (2, 0))},
                {"patt": Perm((0, 1, 2, 3)), "pos": ((1, 0), (1, 0), (2, 0), (2, 0))},
                {"patt": Perm((0, 1, 2, 3)), "pos": ((1, 0), (2, 0), (2, 0), (2, 0))},
                {"patt": Perm((0, 1, 2, 3)), "pos": ((2, 0), (2, 0), (2, 0), (2, 0))},
            ],
            "requirements": [],
            "assumptions": [],
        }
    )

    # strat = SlidingStrategy(2)
    # rule = strat(t)
    # print(rule)
    # rule.sanity_check(5)

    t2 = Tiling.from_dict(
        {
            "class_module": "tilings.tiling",
            "comb_class": "Tiling",
            "obstructions": [
                {"patt": Perm((2, 1, 0)), "pos": ((2, 0), (2, 0), (2, 0))},
                {"patt": Perm((3, 2, 1, 0)), "pos": ((1, 0), (1, 0), (1, 0), (1, 0))},
                {"patt": Perm((3, 2, 1, 0)), "pos": ((1, 0), (1, 0), (1, 0), (2, 0))},
                {"patt": Perm((3, 2, 1, 0)), "pos": ((1, 0), (1, 0), (1, 0), (3, 0))},
                {"patt": Perm((3, 2, 1, 0)), "pos": ((1, 0), (1, 0), (2, 0), (2, 0))},
                {"patt": Perm((3, 2, 1, 0)), "pos": ((1, 0), (1, 0), (2, 0), (3, 0))},
                {"patt": Perm((3, 2, 1, 0)), "pos": ((1, 0), (1, 0), (3, 0), (3, 0))},
                {"patt": Perm((3, 2, 1, 0)), "pos": ((1, 0), (2, 0), (2, 0), (3, 0))},
                {"patt": Perm((3, 2, 1, 0)), "pos": ((1, 0), (2, 0), (3, 0), (3, 0))},
                {"patt": Perm((3, 2, 1, 0)), "pos": ((1, 0), (3, 0), (3, 0), (3, 0))},
                {"patt": Perm((3, 2, 1, 0)), "pos": ((2, 0), (2, 0), (3, 0), (3, 0))},
                {"patt": Perm((3, 2, 1, 0)), "pos": ((2, 0), (3, 0), (3, 0), (3, 0))},
                {"patt": Perm((3, 2, 1, 0)), "pos": ((3, 0), (3, 0), (3, 0), (3, 0))},
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
                },
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (0, 0), (0, 0), (1, 0)),
                },
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (0, 0), (0, 0), (2, 0)),
                },
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (0, 0), (0, 0), (3, 0)),
                },
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (0, 0), (1, 0), (1, 0)),
                },
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (0, 0), (1, 0), (2, 0)),
                },
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (0, 0), (1, 0), (3, 0)),
                },
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (0, 0), (2, 0), (2, 0)),
                },
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (0, 0), (2, 0), (3, 0)),
                },
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (0, 0), (3, 0), (3, 0)),
                },
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (1, 0), (1, 0), (1, 0)),
                },
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (1, 0), (1, 0), (2, 0)),
                },
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (1, 0), (1, 0), (3, 0)),
                },
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (1, 0), (2, 0), (2, 0)),
                },
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (1, 0), (2, 0), (3, 0)),
                },
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (1, 0), (3, 0), (3, 0)),
                },
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (2, 0), (2, 0), (3, 0)),
                },
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (2, 0), (3, 0), (3, 0)),
                },
                {
                    "patt": Perm((0, 4, 3, 2, 1)),
                    "pos": ((0, 0), (0, 0), (3, 0), (3, 0), (3, 0)),
                },
            ],
            "requirements": [],
            "assumptions": [],
        }
    )

    t3 = Tiling.from_dict(
        {
            "class_module": "tilings.tiling",
            "comb_class": "Tiling",
            "obstructions": [
                {"patt": [1, 0], "pos": [[2, 0], [2, 0]]},
                {"patt": [2, 1, 0], "pos": [[2, 0], [3, 0], [3, 0]]},
                {"patt": [2, 1, 0], "pos": [[3, 0], [3, 0], [3, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[1, 0], [1, 0], [1, 0], [1, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[1, 0], [1, 0], [1, 0], [2, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[1, 0], [1, 0], [1, 0], [3, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[1, 0], [1, 0], [1, 0], [4, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[1, 0], [1, 0], [2, 0], [3, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[1, 0], [1, 0], [2, 0], [4, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[1, 0], [1, 0], [3, 0], [3, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[1, 0], [1, 0], [3, 0], [4, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[1, 0], [1, 0], [4, 0], [4, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[1, 0], [2, 0], [3, 0], [4, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[1, 0], [2, 0], [4, 0], [4, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[1, 0], [3, 0], [3, 0], [4, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[1, 0], [3, 0], [4, 0], [4, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[1, 0], [4, 0], [4, 0], [4, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[2, 0], [3, 0], [4, 0], [4, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[2, 0], [4, 0], [4, 0], [4, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[3, 0], [3, 0], [4, 0], [4, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[3, 0], [4, 0], [4, 0], [4, 0]]},
                {"patt": [3, 2, 1, 0], "pos": [[4, 0], [4, 0], [4, 0], [4, 0]]},
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [0, 0], [0, 0], [1, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [0, 0], [0, 0], [2, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [0, 0], [0, 0], [3, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [0, 0], [0, 0], [4, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [0, 0], [1, 0], [1, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [0, 0], [1, 0], [2, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [0, 0], [1, 0], [3, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [0, 0], [1, 0], [4, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [0, 0], [2, 0], [3, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [0, 0], [2, 0], [4, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [0, 0], [3, 0], [3, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [0, 0], [3, 0], [4, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [0, 0], [4, 0], [4, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [1, 0], [1, 0], [1, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [1, 0], [1, 0], [2, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [1, 0], [1, 0], [3, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [1, 0], [1, 0], [4, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [1, 0], [2, 0], [3, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [1, 0], [2, 0], [4, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [1, 0], [3, 0], [3, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [1, 0], [3, 0], [4, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [1, 0], [4, 0], [4, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [2, 0], [3, 0], [4, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [2, 0], [4, 0], [4, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [3, 0], [3, 0], [4, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [3, 0], [4, 0], [4, 0]],
                },
                {
                    "patt": [0, 4, 3, 2, 1],
                    "pos": [[0, 0], [0, 0], [4, 0], [4, 0], [4, 0]],
                },
            ],
            "requirements": [],
            "assumptions": [],
        }
    )
    from tilings.strategies import FusionFactory

    # t2 = t2.empty_cell((2, 0))
    # strat = SlidingFactory()
    # for s in strat(t3):
    #     rule = s(t3)
    #     print(rule)
    #     for r2 in strat(rule.children[0]):
    #         print(r2(rule.children[0]))
    # for i in range(7):
    #     print(rule.sanity_check(i))

    rule = SlidingStrategy(1)(t3)
    print(rule)

    rule = SlidingStrategy(2)(rule.children[0])
    print(rule)
    # for i in range(6):
    #     print(rule.sanity_check(i))

    # for i in range(10):
    #     print(
    #         len(list(t3.objects_of_size(i))),
    #         len(list(rule.children[0].objects_of_size(i))),
    #     )

    for rule in FusionFactory()(rule.children[0]):
        print(rule)

    # from tilings.tilescope import TileScopePack, TrackedSearcher

    # pack = TileScopePack.row_and_col_placements(row_only=True).make_fusion(
    #     tracked=False
    # )
    # pack.expansion_strats[0][0].dirs = (3,)
    # from comb_spec_searcher.rule_db import RuleDBForest
    # from tilings.strategies import SlidingFactory as OldSlidingFactory

    # pack = pack.add_initial(SlidingFactory())
    # scope = TrackedSearcher("15432", pack, 5, ruledb=RuleDBForest())
    # spec = scope.auto_search(status_update=10)
    # spec.show()
    # for i in range(10):
    #     print(spec.count_objects_of_size(i), end=", ")
