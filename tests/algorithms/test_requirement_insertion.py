from permuta import Perm
from tilings import Obstruction, Requirement, Tiling
from tilings.algorithms import CellInsertion, CrossingInsertion


def test_cell_insertion():
    t1 = Tiling.from_string('123')
    ci1 = CellInsertion(t1, maxreqlen=3)
    assert set(ci1.req_lists_to_insert()) == set([
        (Requirement.single_cell(Perm((0,)), (0, 0)),),
        (Requirement.single_cell(Perm((0, 1)), (0, 0)),),
        (Requirement.single_cell(Perm((1, 0)), (0, 0)),),
        (Requirement.single_cell(Perm((0, 2, 1)), (0, 0)),),
        (Requirement.single_cell(Perm((1, 0, 2)), (0, 0)),),
        (Requirement.single_cell(Perm((1, 2, 0)), (0, 0)),),
        (Requirement.single_cell(Perm((2, 0, 1)), (0, 0)),),
        (Requirement.single_cell(Perm((2, 1, 0)), (0, 0)),),
    ])
    assert len(list(ci1.rules())) == 8
    t2 = t1.add_single_cell_requirement(Perm((2, 1, 0)), (0, 0))
    ci2 = CellInsertion(t2, maxreqlen=3)
    assert set(ci2.req_lists_to_insert()) == set([
        (Requirement.single_cell(Perm((0, 1)), (0, 0)),),
        (Requirement.single_cell(Perm((0, 2, 1)), (0, 0)),),
        (Requirement.single_cell(Perm((1, 0, 2)), (0, 0)),),
        (Requirement.single_cell(Perm((1, 2, 0)), (0, 0)),),
        (Requirement.single_cell(Perm((2, 0, 1)), (0, 0)),),
    ])
    assert len(list(ci2.rules())) == 5
    ci3 = CellInsertion(t1, maxreqlen=3, extra_basis=[Perm((0, 2, 1))])
    assert set(ci3.req_lists_to_insert()) == set([
        (Requirement.single_cell(Perm((0,)), (0, 0)),),
        (Requirement.single_cell(Perm((0, 1)), (0, 0)),),
        (Requirement.single_cell(Perm((1, 0)), (0, 0)),),
        (Requirement.single_cell(Perm((1, 0, 2)), (0, 0)),),
        (Requirement.single_cell(Perm((1, 2, 0)), (0, 0)),),
        (Requirement.single_cell(Perm((2, 0, 1)), (0, 0)),),
        (Requirement.single_cell(Perm((2, 1, 0)), (0, 0)),),
    ])
    assert len(list(ci3.rules())) == 7


def test_crossing_insertion():
    t = Tiling(obstructions=[
        Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
        Obstruction(Perm((0, 1)), ((0, 0), (1, 0))),
        Obstruction(Perm((0, 1)), ((1, 0), (1, 0))),
    ], requirements=[
        [Requirement(Perm((0,)), ((0, 0),))],
    ])
    ci = CrossingInsertion(t, maxreqlen=2)
    assert set(ci.req_lists_to_insert()) == set([
        (Requirement(Perm((0,)), ((0, 0),)),),
        (Requirement(Perm((0,)), ((1, 0),)),),
        (Requirement(Perm((1, 0)), ((0, 0), (0, 0))),),
        (Requirement(Perm((1, 0)), ((1, 0), (1, 0))),),
        (Requirement(Perm((1, 0)), ((0, 0), (1, 0))),),
    ])
    assert len(list(ci.rules())) == 5
    ci2 = CrossingInsertion(t, maxreqlen=3)
    assert len(list(ci2.rules())) == 9
    ci3 = CrossingInsertion(t, maxreqlen=3, extra_basis=[Perm((2, 1, 0))])
    assert len(list(ci3.rules())) == 5
