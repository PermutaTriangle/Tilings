import abc

import pytest
import sympy

from comb_spec_searcher.utils import taylor_expand
from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.algorithms import (
    DatabaseEnumeration,
    LocalEnumeration,
    MonotoneTreeEnumeration,
)
from tilings.exception import InvalidOperationError


class CommonTest(abc.ABC):
    @abc.abstractmethod
    @pytest.fixture
    def enum_verified(self):
        raise NotImplementedError

    @abc.abstractmethod
    @pytest.fixture
    def enum_not_verified(self):
        raise NotImplementedError

    def test_verified(self, enum_verified, enum_not_verified):
        assert enum_verified.verified()
        assert not enum_not_verified.verified()

    @abc.abstractmethod
    def test_get_genf(self, enum_verified):
        raise NotImplementedError

    def test_get_genf_not_verified(self, enum_not_verified):
        with pytest.raises(InvalidOperationError):
            enum_not_verified.get_genf()


class TestLocalEnumeration(CommonTest):
    @pytest.fixture
    def enum_verified(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
                GriddedPerm(Perm((0, 2, 1)), ((1, 0),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
                GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
            ],
            requirements=[
                [
                    GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                    GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
                ]
            ],
        )
        return LocalEnumeration(t)

    @pytest.fixture
    def enum_not_verified(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
                GriddedPerm(Perm((0, 2, 1)), ((1, 0),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
                GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 0), (1, 1))),
            ],
            requirements=[
                [
                    GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                    GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
                ]
            ],
        )
        return LocalEnumeration(t)

    @pytest.fixture
    def onebyone_enum(self):
        return LocalEnumeration(Tiling.from_string("123"))

    @pytest.fixture
    def enum_no_req(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1, 2)), ((0, 0),) * 3),
                GriddedPerm(Perm((0, 2, 1)), ((1, 0),) * 3),
                GriddedPerm(Perm((0, 1, 2)), ((1, 0),) * 3),
                GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
            ],
            requirements=[
                [
                    GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                    GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
                ]
            ],
        )
        return LocalEnumeration(t, no_req=True)

    def test_verified(self, enum_verified, enum_not_verified):
        assert enum_verified.verified()
        assert not enum_not_verified.verified()

    def test_get_genf(self, enum_verified):
        with pytest.raises(NotImplementedError):
            enum_verified.get_genf()

    def test_get_genf_not_verified(self, enum_not_verified):
        with pytest.raises(InvalidOperationError):
            enum_not_verified.get_genf()

    def test_1x1_verified(self, onebyone_enum):
        assert onebyone_enum.verified()

    def test_no_req_option(self, enum_no_req):
        assert not enum_no_req.verified()


class TestMonotoneTreeEnumeration(CommonTest):
    @pytest.fixture
    def enum_verified(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 2),) * 2),
                GriddedPerm(Perm((0, 1)), ((2, 0),) * 2),
                GriddedPerm(Perm((0, 1, 2)), ((1, 1),) * 3),
            ]
        )
        return MonotoneTreeEnumeration(t)

    @pytest.fixture
    def enum_not_verified(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 2),) * 2),
                GriddedPerm(Perm((0, 1)), ((2, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((2, 2),) * 2),
                GriddedPerm(Perm((0, 1, 2)), ((1, 1),) * 3),
            ]
        )
        return MonotoneTreeEnumeration(t)

    @pytest.fixture
    def enum_with_list_req(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
                GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
            ],
            requirements=[
                [
                    GriddedPerm(Perm((0,)), ((0, 0),)),
                    GriddedPerm(Perm((0,)), ((1, 0),)),
                ]
            ],
        )
        return MonotoneTreeEnumeration(t)

    @pytest.fixture
    def onebyone_enum(self):
        return MonotoneTreeEnumeration(Tiling.from_string("123"))

    @pytest.fixture
    def enum_with_crossing(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 2),) * 2),
                GriddedPerm(Perm((0, 1)), ((2, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 0), (0, 1))),
                GriddedPerm(Perm((0, 1, 2)), ((1, 1),) * 3),
            ]
        )
        return MonotoneTreeEnumeration(t)

    def test_visited_cells_aligned(self, enum_verified):
        visited = {(1, 1), (0, 1)}
        assert sorted(enum_verified._visted_cells_aligned((0, 2), visited)) == [(0, 1)]

    def test_cell_tree_traversal(self, enum_verified):
        order = list(enum_verified._cell_tree_traversal((1, 1)))
        assert len(order) == 4
        assert (1, 1) not in order
        assert order[0] == (0, 1)
        assert order[3] == (2, 0)
        assert set(order[1:3]) == {(0, 0), (0, 2)}

    def test_not_verified(self, enum_with_list_req, onebyone_enum, enum_with_crossing):
        assert not enum_with_crossing.verified()
        assert not enum_with_list_req.verified()
        assert not onebyone_enum.verified()
        forest_tiling = Tiling(
            obstructions=[
                GriddedPerm(Perm((0,)), ((0, 0),)),
                GriddedPerm(Perm((0,)), ((1, 1),)),
                GriddedPerm(Perm((0,)), ((2, 1),)),
                GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
                GriddedPerm(Perm((0, 1)), ((2, 0), (2, 0))),
                GriddedPerm(Perm((0, 1, 2)), ((0, 1), (0, 1), (0, 1))),
            ],
            requirements=[[GriddedPerm(Perm((0,)), ((0, 1),))]],
        )
        assert not MonotoneTreeEnumeration(forest_tiling).verified()

    @pytest.mark.xfail(reason="No database setup")
    def test_get_genf(self, enum_verified):
        x = sympy.Symbol("x")
        expected_gf = -(
            sympy.sqrt(
                -(4 * x ** 3 - 14 * x ** 2 + 8 * x - 1) / (2 * x ** 2 - 4 * x + 1)
            )
            - 1
        ) / (2 * x * (x ** 2 - 3 * x + 1))
        assert sympy.simplify(enum_verified.get_genf() - expected_gf) == 0
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
            ]
        )
        enum_no_start = MonotoneTreeEnumeration(t)
        expected_gf = -1 / ((x - 1) * (x / (x - 1) + 1))
        assert sympy.simplify(enum_no_start.get_genf() - expected_gf) == 0

    def test_get_genf_simple(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((1, 0)), ((1, 0),) * 2),
            ]
        )
        enum = MonotoneTreeEnumeration(t)
        print(t)
        assert enum.verified()
        assert sympy.simplify(enum.get_genf() - sympy.sympify("1/(1-2*x)")) == 0

    def test_with_finite_monotone_cell(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((1, 0)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
                GriddedPerm(Perm((1, 0)), ((1, 0),) * 2),
            ]
        )
        enum = MonotoneTreeEnumeration(t)
        print(t)
        assert enum.verified()
        assert enum.get_genf().expand() == sympy.sympify("1+2*x+2*x**2")

    def test_with_finite_monotone_cell2(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((1, 0)), ((0, 1),) * 2),
                GriddedPerm(Perm((0, 1)), ((0, 1),) * 2),
                GriddedPerm(Perm((1, 0)), ((1, 1),) * 2),
            ]
        )
        enum = MonotoneTreeEnumeration(t)
        print(t)
        assert enum.verified()
        assert (
            sympy.sympify("x/(1-x)**4 + 1/(1-x)**2") - enum.get_genf()
        ).simplify() == 0

    def test_interleave_fixed_length(self, enum_verified):
        track_var = MonotoneTreeEnumeration._tracking_var
        cell_var = enum_verified._cell_variable((1, 0))
        dummy_var = enum_verified._cell_variable((0, 0))
        x = sympy.var("x")
        F = x ** 8 * track_var ** 3 * dummy_var ** 3
        assert (
            enum_verified._interleave_fixed_length(F, (1, 0), 1)
            == 4 * x ** 9 * dummy_var ** 3 * cell_var ** 1
        )
        assert (
            enum_verified._interleave_fixed_length(F, (1, 0), 3)
            == 20 * x ** 11 * dummy_var ** 3 * cell_var ** 3
        )
        assert (
            enum_verified._interleave_fixed_length(F, (1, 0), 0)
            == x ** 8 * dummy_var ** 3
        )

    def test_interleave_fixed_lengths(self, enum_verified):
        track_var = MonotoneTreeEnumeration._tracking_var
        cell_var = enum_verified._cell_variable((1, 0))
        dummy_var = enum_verified._cell_variable((0, 0))
        x = sympy.var("x")
        F = x ** 8 * track_var ** 3 * dummy_var ** 3
        assert (
            enum_verified._interleave_fixed_lengths(F, (1, 0), 1, 1)
            == 4 * x ** 9 * dummy_var ** 3 * cell_var ** 1
        )
        assert (
            enum_verified._interleave_fixed_lengths(F, (1, 0), 3, 3)
            == 20 * x ** 11 * dummy_var ** 3 * cell_var ** 3
        )
        assert (
            enum_verified._interleave_fixed_lengths(F, (1, 0), 0, 0)
            == x ** 8 * dummy_var ** 3
        )
        assert (
            enum_verified._interleave_fixed_lengths(F, (1, 0), 0, 2)
            == x ** 8 * dummy_var ** 3
            + 4 * x ** 9 * dummy_var ** 3 * cell_var ** 1
            + 10 * x ** 10 * dummy_var ** 3 * cell_var ** 2
        )
        assert (
            enum_verified._interleave_fixed_lengths(F, (1, 0), 1, 3)
            == 4 * x ** 9 * dummy_var ** 3 * cell_var ** 1
            + 10 * x ** 10 * dummy_var ** 3 * cell_var ** 2
            + 20 * x ** 11 * dummy_var ** 3 * cell_var ** 3
        )

    def test_genf_with_req(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
            ],
            requirements=[
                [GriddedPerm(Perm((1, 0)), ((0, 0),) * 2)],
                [GriddedPerm(Perm((0,)), ((1, 0),))],
            ],
        )
        enum = MonotoneTreeEnumeration(t)
        print(t)
        assert enum.verified()
        genf = enum.get_genf().expand()
        terms = [0, 0, 0, 3, 10, 25, 56, 119, 246, 501, 1012]
        assert taylor_expand(genf) == terms

    def test_genf_with_big_finite_cell(self):
        t = Tiling(
            obstructions=[
                GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
                GriddedPerm(Perm((0, 1)), ((1, 0),) * 2),
                GriddedPerm(Perm((3, 2, 1, 0)), ((0, 0),) * 4),
                GriddedPerm(Perm((3, 2, 1, 0)), ((1, 0),) * 4),
            ]
        )
        enum = MonotoneTreeEnumeration(t)
        print(t)
        assert enum.verified()
        genf = enum.get_genf().expand()
        x = sympy.var("x")
        assert (
            genf
            == 1
            + 2 * x
            + 4 * x ** 2
            + 8 * x ** 3
            + 14 * x ** 4
            + 20 * x ** 5
            + 20 * x ** 6
        )

    def test_with_two_reqs(self):
        t = Tiling(
            obstructions=(
                GriddedPerm(Perm((0,)), ((1, 1),)),
                GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
                GriddedPerm(Perm((0, 1)), ((0, 1), (0, 1))),
                GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
                GriddedPerm(Perm((1, 0)), ((0, 1), (0, 1))),
            ),
            requirements=(
                (GriddedPerm(Perm((0,)), ((0, 0),)),),
                (GriddedPerm(Perm((0,)), ((0, 1),)),),
            ),
        )
        enum = MonotoneTreeEnumeration(t)
        expected_enum = [0, 0, 2, 7, 19, 47, 111, 255, 575, 1279, 2815]
        assert enum.verified()
        assert taylor_expand(enum.get_genf()) == expected_enum

    def test_corner(self):
        t = Tiling(
            obstructions=(
                GriddedPerm(Perm((0,)), ((1, 1),)),
                GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
                GriddedPerm(Perm((0, 1)), ((0, 1), (0, 1))),
                GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
            ),
            requirements=((GriddedPerm(Perm((0,)), ((0, 0),)),),),
        )
        enum = MonotoneTreeEnumeration(t)
        expected_enum = [0, 1, 5, 17, 50, 138, 370, 979, 2575, 6755, 17700]
        assert enum.verified()
        assert taylor_expand(enum.get_genf()) == expected_enum


class TestDatabaseEnumeration(CommonTest):
    @pytest.fixture
    def enum_verified(self):
        t = Tiling.from_string("123_132_231")
        return DatabaseEnumeration(t)

    @pytest.fixture
    def enum_not_verified(self):
        t = Tiling.from_string("1324")
        return DatabaseEnumeration(t)

    def test_get_genf(self, enum_verified):
        assert enum_verified.get_genf() == sympy.sympify(
            "(x**2 - x + 1)/(x**2 - 2*x + 1)"
        )

    @pytest.mark.slow
    def test_load_verified_tilings(self):
        assert not DatabaseEnumeration.all_verified_tilings
        DatabaseEnumeration.load_verified_tiling()
        assert DatabaseEnumeration.all_verified_tilings
        sample = next(iter(DatabaseEnumeration.all_verified_tilings))
        Tiling.from_bytes(sample)

    def test_verification_with_cache(self):
        t = Tiling.from_string("123_132_231")
        DatabaseEnumeration.all_verified_tilings = frozenset()
        assert DatabaseEnumeration(t).verified()
        DatabaseEnumeration.all_verified_tilings = frozenset([1, 2, 3, 4])
        assert not DatabaseEnumeration(t).verified()
        DatabaseEnumeration.all_verified_tilings = frozenset([t.to_bytes()])
        assert DatabaseEnumeration(t).verified()
