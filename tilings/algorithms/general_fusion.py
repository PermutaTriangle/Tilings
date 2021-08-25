from collections import defaultdict
from itertools import chain, product
from typing import Counter, DefaultDict, Dict, Iterable, Iterator, List, Optional, Tuple

from tilings.algorithms.fusion import Fusion
from tilings.assumptions import TrackingAssumption
from tilings.griddedperm import Cell, GriddedPerm
from tilings.misc import union_reduce
from tilings.tiling import Tiling


class GeneralFusion(Fusion):
    def __init__(self, *args, **kwargs):
        self._extra_obs: Optional[List[GriddedPerm]] = None
        self._extra_reqs: Optional[List[List[GriddedPerm]]] = None
        super().__init__(*args, **kwargs)

    def is_crossing(self, gp: GriddedPerm) -> bool:
        """
        Return True if the gridded permutation `gp` is
        crossing between the fused rows or cols.
        """
        return bool(
            self._fuse_row
            and any(y == self._row_idx for _, y in gp.pos)
            and any(y == self._row_idx for _, y in gp.pos)
        ) or bool(
            not self._fuse_row
            and any(x == self._col_idx for x, _ in gp.pos)
            and any(x == self._col_idx for x, _ in gp.pos)
        )

    @property
    def obstruction_fuse_counter(self) -> Counter[GriddedPerm]:
        """
        Counter of multiplicities of fused obstructions.

        Crossing obstructions between first cell and second cell
        are ignored.
        """
        if self._obstruction_fuse_counter is not None:
            return self._obstruction_fuse_counter
        obs = (ob for ob in self._tiling.obstructions if not self.is_crossing(ob))
        fuse_counter = self._fuse_counter(obs)
        self._obstruction_fuse_counter = fuse_counter
        return self._obstruction_fuse_counter

    @property
    def requirements_fuse_counters(self) -> List[Counter[GriddedPerm]]:
        """
        List of fuse counters for each of the requirements list of the tiling.
        """
        if self._requirements_fuse_counters is not None:
            return self._requirements_fuse_counters
        counters = [
            self._fuse_counter(req_list)
            for req_list in self._tiling.requirements
            # if not self.is_positive_left_or_right_requirement(req_list)
            # TODO: don't check for positive cells
        ]
        self._requirements_fuse_counters = counters
        return self._requirements_fuse_counters

    def obstructions_to_add(self) -> Iterator[GriddedPerm]:
        """
        Iterator over all the obstructions obtained by fusing obstructions of
        the tiling and then unfusing it in all possible ways. Crossing
        obstructions between first cell and second cell are not processed.
        """
        return chain.from_iterable(
            self.unfuse_gridded_perm(ob) for ob in self.obstruction_fuse_counter
        )

    def requirements_to_add(self) -> Iterator[Iterator[GriddedPerm]]:
        for req in self.requirements_fuse_counters:
            yield chain.from_iterable(self.unfuse_gridded_perm(gp) for gp in req)

    def _can_fuse_set_of_gridded_perms(
        self, fuse_counter: Counter[GriddedPerm]
    ) -> bool:
        raise NotImplementedError

    def _is_valid_count(self, count: int, gp: GriddedPerm) -> bool:
        raise NotImplementedError

    def fusable(self) -> bool:
        split_obs = tuple(self.obstructions_to_add())
        split_reqs = tuple(tuple(req) for req in self.requirements_to_add())
        new_tiling = self._tiling.add_obstructions_and_requirements(
            split_obs, split_reqs, remove_empty_rows_and_cols=False
        )
        self._extra_obs = [
            gp for gp in self._tiling.obstructions if gp not in split_obs
        ]
        extra_reqs = [
            [gp for gp in split_req if gp in req]
            for req, split_req in zip(self._tiling.requirements, split_reqs)
        ]
        self._extra_reqs = [req for req in extra_reqs if req]
        return (
            self._tiling == new_tiling
            and not extra_reqs
            and all(len(gp) <= 2 for gp in self._extra_obs)
            # and len(self._extra_obs) <= 1
            and self._check_isolation_level()
            and not any(
                ass.is_active_in_cells(self.active_cells())
                and ass.fuse(
                    self._row_idx if self._fuse_row else self._col_idx, self._fuse_row
                )
                != self.new_assumption()
                for ass in self._tiling.assumptions
            )
            # and self.new_assumption().tiling.dimensions
            # in ((2, 1), (1, 2))  # TODO: this is perhaps too restrictive?
        )

    def active_cells(self):
        if self._fuse_row:
            return self._tiling.cells_in_row(self._row_idx).union(
                self._tiling.cells_in_row(self._row_idx + 1)
            )
        else:
            return self._tiling.cells_in_col(self._col_idx).union(
                self._tiling.cells_in_col(self._col_idx + 1)
            )

    def new_assumption(self) -> TrackingAssumption:
        """
        Return the assumption that needs to be counted in order to enumerate.
        """
        # if not self.fusable():
        #     raise ValueError("Tiling is not fusable")
        if self._extra_obs is None:
            assert self.fusable()
        assert self._extra_obs is not None
        assert self._extra_reqs is not None
        tiling = self._tiling
        col_map: Dict[int, int] = dict()
        row_map: Dict[int, int] = dict()
        for x in range(self._tiling.dimensions[0]):
            if not self._fuse_row and x > self._col_idx:
                col_map[x] = x - 1
            if not self._fuse_row and x <= self._col_idx:
                col_map[x] = x
            if self._fuse_row:
                col_map[x] = x
        for y in range(self._tiling.dimensions[1]):
            if self._fuse_row and y > self._row_idx:
                row_map[y] = y - 1
            if self._fuse_row and y <= self._row_idx:
                row_map[y] = y
            if not self._fuse_row:
                row_map[y] = y
        return TrackingAssumption(tiling, col_map, row_map)


def test_ass_map(tiling, original_tiling, verbose=False):
    return
    if verbose:
        print("=" * 10)
        print("TESTING ASS MAP")
        print(tiling)
        print(original_tiling)
    ass = tiling.assumptions[0]
    original_obs, original_reqs = ass.obstructions_and_requirements()
    new_obs = []
    for ob in tiling.obstructions:
        if verbose:
            print(ob)
        for gp in ass.reverse_map(ob):
            if gp.avoids(*original_obs):
                if verbose:
                    print("   ", gp)
                new_obs.append(gp)
    new_reqs = []
    for req in tiling.requirements:
        new_req = []
        for r in req:
            if verbose:
                print(r)
            for gp in ass.reverse_map(r):
                if any(gp.contains(*gps) for gps in original_reqs):
                    if verbose:
                        print("   ", gp)
                    new_req.append(gp)
        new_reqs.append(new_req)
    unfused = Tiling(
        new_obs + original_obs,
        new_reqs + original_reqs,
    )
    if verbose:
        # print(original_tiling)
        print(unfused)
        print("=" * 10)
    assert unfused == original_tiling.remove_assumptions()
    for i in range(6):  # these counts should match!
        terms = tiling.get_terms(i)
        actual = len(list(original_tiling.remove_assumptions().objects_of_size(i)))
        computed = sum(k[0] * v for k, v in terms.items())
        assert actual == computed, (i, actual, computed, terms, tiling, original_tiling)


if __name__ == "__main__":

    tiling = Tiling.from_dict(
        {
            "class_module": "tilings.tiling",
            "comb_class": "Tiling",
            "obstructions": [
                {"patt": [0, 1], "pos": [[0, 0], [1, 0]]},
                {"patt": [0, 1], "pos": [[0, 0], [3, 0]]},
                {"patt": [0, 1], "pos": [[1, 0], [3, 0]]},
                {"patt": [0, 1], "pos": [[2, 0], [3, 0]]},
                {"patt": [0, 2, 1], "pos": [[0, 0], [0, 0], [0, 0]]},
                {"patt": [0, 2, 1], "pos": [[0, 0], [0, 0], [2, 0]]},
                {"patt": [0, 2, 1], "pos": [[0, 0], [2, 0], [2, 0]]},
                {"patt": [0, 2, 1], "pos": [[1, 0], [1, 0], [1, 0]]},
                {"patt": [0, 2, 1], "pos": [[1, 0], [1, 0], [2, 0]]},
                {"patt": [0, 2, 1], "pos": [[1, 0], [2, 0], [2, 0]]},
                {"patt": [0, 2, 1], "pos": [[2, 0], [2, 0], [2, 0]]},
                {"patt": [0, 2, 1], "pos": [[3, 0], [3, 0], [3, 0]]},
                {"patt": [0, 2, 1, 3], "pos": [[0, 0], [0, 0], [4, 0], [4, 0]]},
                {"patt": [0, 2, 1, 3], "pos": [[0, 0], [2, 0], [4, 0], [4, 0]]},
                {"patt": [0, 2, 1, 3], "pos": [[0, 0], [4, 0], [4, 0], [4, 0]]},
                {"patt": [0, 2, 1, 3], "pos": [[1, 0], [1, 0], [4, 0], [4, 0]]},
                {"patt": [0, 2, 1, 3], "pos": [[1, 0], [2, 0], [4, 0], [4, 0]]},
                {"patt": [0, 2, 1, 3], "pos": [[1, 0], [4, 0], [4, 0], [4, 0]]},
                {"patt": [0, 2, 1, 3], "pos": [[2, 0], [2, 0], [4, 0], [4, 0]]},
                {"patt": [0, 2, 1, 3], "pos": [[2, 0], [4, 0], [4, 0], [4, 0]]},
                {"patt": [0, 2, 1, 3], "pos": [[3, 0], [3, 0], [4, 0], [4, 0]]},
                {"patt": [0, 2, 1, 3], "pos": [[3, 0], [4, 0], [4, 0], [4, 0]]},
                {"patt": [0, 2, 1, 3], "pos": [[4, 0], [4, 0], [4, 0], [4, 0]]},
            ],
            "requirements": [],
            "assumptions": [],
        }
    )

    gf = GeneralFusion(tiling, col_idx=0, tracked=True)
    print(gf.fusable())
    print(gf.fused_tiling())
    test_ass_map(gf.fused_tiling(), tiling)

    fusable = Tiling(
        [
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (1, 0))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 0), (2, 0))),
            GriddedPerm((0, 1), ((1, 0), (1, 0))),
            GriddedPerm((0, 1), ((1, 0), (2, 0))),
            GriddedPerm((0, 1), ((2, 0), (2, 0))),
        ]
    )

    gf = GeneralFusion(tiling=fusable, col_idx=1, tracked=True)

    print(gf.fusable())
    print(gf.fused_tiling())

    test_ass_map(gf.fused_tiling(), fusable)

    for i in range(5):
        terms = gf.fused_tiling().get_terms(i)
        print(i, terms)
        print("actual:", len(list(gf._tiling.objects_of_size(i))))
        print("computed:", sum(k[0] * v for k, v in terms.items()))

    comp_fusable = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 0), (0, 1))),
            GriddedPerm((0, 1, 2), ((0, 0), (0, 2), (0, 2))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 2), (0, 2))),
            GriddedPerm((0, 2, 1), ((0, 0), (0, 2), (0, 0))),
            GriddedPerm((0, 2, 1), ((0, 1), (0, 2), (0, 1))),
            GriddedPerm((0, 2, 3, 1), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 2, 3, 1), ((0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 2, 3, 1), ((0, 2), (0, 2), (0, 2), (0, 2))),
            GriddedPerm((0, 3, 1, 2), ((0, 0), (0, 0), (0, 0), (0, 0))),
            GriddedPerm((0, 3, 1, 2), ((0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 3, 1, 2), ((0, 2), (0, 2), (0, 2), (0, 2))),
        ),
        requirements=(),
        assumptions=(),
    )  # 3 without assumption

    gf = GeneralFusion(comp_fusable, row_idx=0, tracked=True)
    fused_tiling = gf.fused_tiling()  # 2 with assumption

    test_ass_map(fused_tiling, comp_fusable)

    ass = fused_tiling.assumptions[0]
    print("===== component fusable tiling =====")
    print(comp_fusable)
    print("==== end ====")

    print("===== the fused tiling =====")
    print(fused_tiling)
    print("==== end ====")

    for i in range(6):
        terms = fused_tiling.get_terms(i)
        print(i, terms)
        print("actual:", len(list(gf._tiling.objects_of_size(i))))
        print("computed:", sum(k[0] * v for k, v in terms.items()))

    unfused_positive_tiling = comp_fusable.insert_cell((0, 2))

    positive_fused_tiling = fused_tiling.insert_cell((0, 1))

    test_ass_map(positive_fused_tiling, unfused_positive_tiling)

    print("===== the positive tiling =====")
    print(positive_fused_tiling)  # 5 with assumption?
    print("==== end ====")

    unfused_placed_tiling = unfused_positive_tiling.place_point_in_cell((0, 2), 0)

    placed_fused_tiling = positive_fused_tiling.place_point_in_cell((0, 1), 0)

    test_ass_map(placed_fused_tiling, unfused_placed_tiling, verbose=False)

    print("===== the placed tiling =====")
    print(placed_fused_tiling)  # 5.5, i.e. the one in the middle of the eqv path 5 -> 6
    print("==== end ====")
    separated_tiling = placed_fused_tiling.row_and_column_separation()
    unfused_separated_tiling = Tiling(
        obstructions=(
            GriddedPerm((0, 1), ((0, 1), (0, 3))),
            GriddedPerm((0, 1), ((0, 1), (0, 4))),
            GriddedPerm((0, 1), ((0, 1), (2, 2))),
            GriddedPerm((0, 1), ((0, 3), (0, 4))),
            GriddedPerm((0, 1), ((1, 5), (1, 5))),
            GriddedPerm((0, 1), ((2, 0), (2, 2))),
            GriddedPerm((1, 0), ((1, 5), (1, 5))),
            GriddedPerm((0, 1, 2), ((0, 1), (0, 6), (0, 6))),
            GriddedPerm((0, 1, 2), ((0, 3), (0, 6), (0, 6))),
            GriddedPerm((0, 1, 2), ((0, 4), (0, 6), (0, 6))),
            GriddedPerm((0, 2, 1), ((0, 1), (0, 6), (0, 1))),
            GriddedPerm((0, 2, 1), ((0, 3), (0, 6), (0, 3))),
            GriddedPerm((0, 2, 1), ((0, 4), (0, 6), (0, 4))),
            GriddedPerm((0, 2, 3, 1), ((0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 2, 3, 1), ((0, 3), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((0, 2, 3, 1), ((0, 4), (0, 4), (0, 4), (0, 4))),
            GriddedPerm((0, 2, 3, 1), ((0, 6), (0, 6), (0, 6), (0, 6))),
            GriddedPerm((0, 2, 3, 1), ((2, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 2, 3, 1), ((2, 2), (2, 2), (2, 2), (2, 2))),
            GriddedPerm((0, 3, 1, 2), ((0, 1), (0, 1), (0, 1), (0, 1))),
            GriddedPerm((0, 3, 1, 2), ((0, 3), (0, 3), (0, 3), (0, 3))),
            GriddedPerm((0, 3, 1, 2), ((0, 4), (0, 4), (0, 4), (0, 4))),
            GriddedPerm((0, 3, 1, 2), ((0, 6), (0, 6), (0, 6), (0, 6))),
            GriddedPerm((0, 3, 1, 2), ((2, 0), (2, 0), (2, 0), (2, 0))),
            GriddedPerm((0, 3, 1, 2), ((2, 2), (2, 2), (2, 2), (2, 2))),
        ),
        requirements=((GriddedPerm((0,), ((1, 5),)),),),
        assumptions=(),
    )  # only separating rows, so can't use row_column_separation method

    print(repr(unfused_separated_tiling))
    print(separated_tiling)
    test_ass_map(separated_tiling, unfused_separated_tiling, verbose=True)

    # separated_assless_tiling = (
    #     placed_fused_tiling.remove_assumptions().row_and_column_separation()
    # )
    # print(separated_assless_tiling)
    # separated_comp_fusable = Tiling(
    #     [
    #         GriddedPerm((0, 1), ((0, 1), (2, 2))),
    #         GriddedPerm((0, 1), ((2, 0), (2, 2))),
    #         GriddedPerm((0, 1), ((0, 1), (0, 3))),
    #     ],
    #     remove_empty_rows_and_cols=False,
    # )
    # print(separated_comp_fusable)
    # separable_map = {
    #     (0, 1): (0, 1),
    #     (0, 3): (0, 1),
    #     (1, 0): (1, 0),
    #     (2, 2): (2, 0),
    #     (2, 0): (2, 0),
    # }

    # separable_ass = TrackingAssumption(separated_comp_fusable, separable_map)
    # unfused_separated_tiling = unfused_placed_tiling.row_and_column_separation()
    # separated_tiling = separated_assless_tiling.add_assumption(separable_ass)
    print("===== the separated tiling =====")
    print(separated_tiling)  # 6, i.e. the one in the middle of the eqv path 5 -> 6
    print("==== end ====")

    # TODO: unfused tiling should not separate last column
    # test_ass_map(separated_tiling, unfused_separated_tiling)

    for i in range(6):  # these counts should match!
        print("====placed====")
        terms = placed_fused_tiling.get_terms(i)
        print(i, terms)
        print(
            "actual:",
            len(list(unfused_placed_tiling.objects_of_size(i))),
        )
        print("computed:", sum(k[0] * v for k, v in terms.items()))
        print("====positive====")
        terms = positive_fused_tiling.get_terms(i)
        print(i, terms)
        print(
            "actual:",
            len(list(unfused_positive_tiling.objects_of_size(i))),
        )
        print("computed:", sum(k[0] * v for k, v in terms.items()))
        print("====separated====")
        terms = separated_tiling.get_terms(i)
        print(i, terms)
        print(
            "actual:",
            len(list(unfused_separated_tiling.objects_of_size(i))),
        )
        print("computed:", sum(k[0] * v for k, v in terms.items()))
        print()
