import pytest

from permuta import Perm
from tilings import Obstruction, Requirement, Tiling
from tilings.algorithms import ObstructionTransitivity


@pytest.fixture
def tiling_simple_trans_row():
    return Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
            Obstruction(Perm((0, 1)), [(1, 0), (2, 0)]),
        ],
        requirements=[[Requirement(Perm((0,)), [(1, 0)])]],
    )


@pytest.fixture
def tiling_simple_trans_col():
    return Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), [(0, 0), (0, 1)]),
            Obstruction(Perm((0, 1)), [(0, 1), (0, 2)]),
        ],
        requirements=[[Requirement(Perm((0,)), [(0, 1)])]],
    )


@pytest.fixture
def tiling_simple_trans_row_len2():
    return Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
            Obstruction(Perm((0, 1)), [(1, 0), (2, 0)]),
            Obstruction(Perm((0, 1)), [(2, 0), (3, 0)]),
        ],
        requirements=[
            [Requirement(Perm((0,)), [(1, 0)])],
            [Requirement(Perm((0,)), [(2, 0)])],
        ],
    )


@pytest.fixture
def tiling_simple_trans_row_len3():
    return Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
            Obstruction(Perm((0, 1)), [(1, 0), (2, 0)]),
            Obstruction(Perm((0, 1)), [(2, 0), (3, 0)]),
            Obstruction(Perm((0, 1)), [(3, 0), (4, 0)]),
        ],
        requirements=[
            [Requirement(Perm((0,)), [(1, 0)])],
            [Requirement(Perm((0,)), [(2, 0)])],
            [Requirement(Perm((0,)), [(3, 0)])],
        ],
    )


@pytest.fixture
def tiling_no_trans_row():
    return Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
            Obstruction(Perm((0, 1)), [(1, 0), (2, 0)]),
        ]
    )


@pytest.fixture
def tiling_no_trans_col():
    return Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), [(0, 0), (0, 1)]),
            Obstruction(Perm((0, 1)), [(0, 1), (0, 2)]),
        ]
    )


@pytest.fixture
def tiling_with_empty_inf_cell():
    t = Tiling(
        obstructions=[
            Obstruction(Perm((0, 1)), ((1, 0), (3, 0))),
            Obstruction(Perm((0, 1)), ((2, 0), (2, 0))),
            Obstruction(Perm((0, 1)), ((2, 0), (3, 0))),
            Obstruction(Perm((0, 1)), ((3, 0), (3, 0))),
            Obstruction(Perm((1, 0)), ((1, 0), (1, 0))),
            Obstruction(Perm((1, 0)), ((1, 0), (2, 0))),
            Obstruction(Perm((1, 0)), ((1, 0), (3, 0))),
            Obstruction(Perm((1, 0)), ((2, 0), (2, 0))),
            Obstruction(Perm((1, 0)), ((2, 0), (3, 0))),
            Obstruction(Perm((1, 0)), ((3, 0), (3, 0))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (1, 0))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (2, 0))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (3, 0))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (1, 0), (1, 0))),
            Obstruction(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 0))),
            Obstruction(Perm((0, 1, 2)), ((1, 0), (1, 0), (1, 0))),
            Obstruction(Perm((0, 1, 2)), ((1, 0), (1, 0), (2, 0))),
            Obstruction(Perm((3, 2, 1, 0)), ((0, 0), (0, 0), (0, 0), (0, 0))),
            Obstruction(Perm((3, 2, 1, 0)), ((0, 0), (0, 0), (0, 0), (1, 0))),
            Obstruction(Perm((3, 2, 1, 0)), ((0, 0), (0, 0), (0, 0), (2, 0))),
            Obstruction(Perm((3, 2, 1, 0)), ((0, 0), (0, 0), (0, 0), (3, 0))),
        ],
        requirements=[[Requirement(Perm((0, 1)), ((1, 0), (2, 0)))]],
    )
    return t


class TestObstructionTransitivity:
    @pytest.fixture
    def simple_trans_col(self, tiling_simple_trans_col):
        return ObstructionTransitivity(tiling_simple_trans_col)

    @pytest.fixture
    def simple_trans_row(self, tiling_simple_trans_row):
        return ObstructionTransitivity(tiling_simple_trans_row)

    @pytest.fixture
    def simple_trans_row_len2(self, tiling_simple_trans_row_len2):
        return ObstructionTransitivity(tiling_simple_trans_row_len2)

    @pytest.fixture
    def simple_trans_row_len3(self, tiling_simple_trans_row_len3):
        return ObstructionTransitivity(tiling_simple_trans_row_len3)

    @pytest.fixture
    def no_trans_row(self, tiling_no_trans_row):
        return ObstructionTransitivity(tiling_no_trans_row)

    @pytest.fixture
    def no_trans_col(self, tiling_no_trans_col):
        return ObstructionTransitivity(tiling_no_trans_col)

    @pytest.fixture
    def with_empty_inf_cell(self, tiling_with_empty_inf_cell):
        return ObstructionTransitivity(tiling_with_empty_inf_cell)

    def test_init(self, tiling_simple_trans_col):
        obstrans = ObstructionTransitivity(tiling_simple_trans_col)
        assert isinstance(obstrans._tiling, Tiling)
        assert obstrans._tiling == tiling_simple_trans_col

    def test_positive_cells_row(self, simple_trans_col, simple_trans_row_len3):
        assert simple_trans_col.positive_cells_row(1) == [0]
        assert simple_trans_col.positive_cells_row(0) == []
        assert simple_trans_col.positive_cells_row(2) == []
        assert sorted(simple_trans_row_len3.positive_cells_row(0)) == [1, 2, 3]

    def test_positive_cells_col(self, simple_trans_col, simple_trans_row_len3):
        assert simple_trans_col.positive_cells_col(0) == [1]
        assert simple_trans_row_len3.positive_cells_col(0) == []
        assert simple_trans_row_len3.positive_cells_col(1) == [0]
        assert simple_trans_row_len3.positive_cells_col(2) == [0]
        assert simple_trans_row_len3.positive_cells_col(3) == [0]
        assert simple_trans_row_len3.positive_cells_col(4) == []

    def test_ineq_row(self, simple_trans_col, simple_trans_row_len3, no_trans_row):
        assert simple_trans_col.ineq_row(0) == set()
        assert simple_trans_col.ineq_row(1) == set()
        assert simple_trans_col.ineq_row(1) == set()
        assert simple_trans_row_len3.ineq_row(0) == {(1, 0), (2, 1), (3, 2), (4, 3)}
        assert no_trans_row.ineq_row(0) == {(1, 0), (2, 1)}

    def test_ineq_col(self, simple_trans_col, simple_trans_row_len3, no_trans_row):
        assert simple_trans_col.ineq_col(0) == {(1, 0), (2, 1)}
        assert simple_trans_row_len3.ineq_col(0) == set()
        assert simple_trans_row_len3.ineq_col(1) == set()
        assert simple_trans_row_len3.ineq_col(2) == set()
        assert simple_trans_row_len3.ineq_col(3) == set()

    def test_ineq_ob(self, simple_trans_col):
        assert simple_trans_col.ineq_ob(((0, 0), (0, 0))) == Obstruction(
            Perm((0,)), [(0, 0)]
        )
        assert simple_trans_col.ineq_ob(((0, 0), (1, 0))) == Obstruction(
            Perm((1, 0)), [(0, 0), (1, 0)]
        )
        assert simple_trans_col.ineq_ob(((1, 0), (0, 0))) == Obstruction(
            Perm((0, 1)), [(0, 0), (1, 0)]
        )
        assert simple_trans_col.ineq_ob(((0, 0), (0, 1))) == Obstruction(
            Perm((1, 0)), [(0, 1), (0, 0)]
        )
        assert simple_trans_col.ineq_ob(((0, 1), (0, 0))) == Obstruction(
            Perm((0, 1)), [(0, 0), (0, 1)]
        )
        with pytest.raises(ValueError):
            simple_trans_col.ineq_ob(((0, 0), (1, 1)))

    def test_ineq_closure(self, simple_trans_col):
        assert simple_trans_col.ineq_closure([], []) == set()
        assert simple_trans_col.ineq_closure([1], [(0, 1), (1, 2)]) == {(0, 2)}
        assert simple_trans_col.ineq_closure([], [(0, 1), (1, 2)]) == set()
        assert simple_trans_col.ineq_closure(
            [1, 2], [(1, 2), (2, 3), (3, 2), (1, 3), (3, 1)]
        ) == {(3, 3)}
        assert simple_trans_col.ineq_closure(
            [1, 2], [(0, 1), (1, 2), (2, 3), (3, 4)]
        ) == {(1, 3), (0, 3), (0, 2)}

    def test_new_ineq(self, simple_trans_col, simple_trans_row_len3):
        assert simple_trans_col.new_ineq() == [((0, 2), (0, 0))]
        assert sorted(simple_trans_row_len3.new_ineq()) == [
            ((2, 0), (0, 0)),
            ((3, 0), (0, 0)),
            ((3, 0), (1, 0)),
            ((4, 0), (0, 0)),
            ((4, 0), (1, 0)),
            ((4, 0), (2, 0)),
        ]

    def test_obstruction_transitivity(
        self,
        simple_trans_row,
        simple_trans_col,
        simple_trans_row_len2,
        simple_trans_row_len3,
        no_trans_row,
        tiling_no_trans_row,
        no_trans_col,
        tiling_no_trans_col,
        with_empty_inf_cell,
    ):
        assert simple_trans_row.obstruction_transitivity() == Tiling(
            obstructions=[
                Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
                Obstruction(Perm((0, 1)), [(1, 0), (2, 0)]),
                Obstruction(Perm((0, 1)), [(0, 0), (2, 0)]),
            ],
            requirements=[[Requirement(Perm((0,)), [(1, 0)])]],
        )

        assert simple_trans_col.obstruction_transitivity() == Tiling(
            obstructions=[
                Obstruction(Perm((0, 1)), [(0, 0), (0, 1)]),
                Obstruction(Perm((0, 1)), [(0, 1), (0, 2)]),
                Obstruction(Perm((0, 1)), [(0, 0), (0, 2)]),
            ],
            requirements=[[Requirement(Perm((0,)), [(0, 1)])]],
        )

        assert simple_trans_row_len2.obstruction_transitivity() == Tiling(
            obstructions=[
                Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
                Obstruction(Perm((0, 1)), [(0, 0), (2, 0)]),
                Obstruction(Perm((0, 1)), [(0, 0), (3, 0)]),
                Obstruction(Perm((0, 1)), [(1, 0), (2, 0)]),
                Obstruction(Perm((0, 1)), [(1, 0), (3, 0)]),
                Obstruction(Perm((0, 1)), [(2, 0), (3, 0)]),
            ],
            requirements=[
                [Requirement(Perm((0,)), [(1, 0)])],
                [Requirement(Perm((0,)), [(2, 0)])],
            ],
        )

        assert simple_trans_row_len3.obstruction_transitivity() == Tiling(
            obstructions=[
                Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
                Obstruction(Perm((0, 1)), [(0, 0), (2, 0)]),
                Obstruction(Perm((0, 1)), [(0, 0), (3, 0)]),
                Obstruction(Perm((0, 1)), [(0, 0), (4, 0)]),
                Obstruction(Perm((0, 1)), [(1, 0), (2, 0)]),
                Obstruction(Perm((0, 1)), [(1, 0), (3, 0)]),
                Obstruction(Perm((0, 1)), [(1, 0), (4, 0)]),
                Obstruction(Perm((0, 1)), [(2, 0), (3, 0)]),
                Obstruction(Perm((0, 1)), [(2, 0), (4, 0)]),
                Obstruction(Perm((0, 1)), [(3, 0), (4, 0)]),
            ],
            requirements=[
                [Requirement(Perm((0,)), [(1, 0)])],
                [Requirement(Perm((0,)), [(2, 0)])],
                [Requirement(Perm((0,)), [(3, 0)])],
            ],
        )

        assert no_trans_row.obstruction_transitivity() == tiling_no_trans_row
        assert no_trans_col.obstruction_transitivity() == tiling_no_trans_col
        t = Tiling(
            obstructions=[
                Obstruction(Perm((0, 1)), ((2, 0), (2, 0))),
                Obstruction(Perm((1, 0)), ((1, 0), (1, 0))),
                Obstruction(Perm((1, 0)), ((1, 0), (2, 0))),
                Obstruction(Perm((1, 0)), ((2, 0), (2, 0))),
                Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (0, 0))),
                Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (1, 0))),
                Obstruction(Perm((0, 1, 2)), ((0, 0), (0, 0), (2, 0))),
                Obstruction(Perm((0, 1, 2)), ((0, 0), (1, 0), (1, 0))),
                Obstruction(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 0))),
                Obstruction(Perm((0, 1, 2)), ((1, 0), (1, 0), (1, 0))),
                Obstruction(Perm((0, 1, 2)), ((1, 0), (1, 0), (2, 0))),
                Obstruction(Perm((3, 2, 1, 0)), ((0, 0), (0, 0), (0, 0), (0, 0))),
                Obstruction(Perm((3, 2, 1, 0)), ((0, 0), (0, 0), (0, 0), (1, 0))),
                Obstruction(Perm((3, 2, 1, 0)), ((0, 0), (0, 0), (0, 0), (2, 0))),
            ],
            requirements=[[Requirement(Perm((0, 1)), ((1, 0), (2, 0)))]],
        )
        assert with_empty_inf_cell.obstruction_transitivity() == t

