from permuta import Perm
from tilings import Obstruction, Requirement, Tiling
from tilings.strategies.batch import (all_cell_insertions, all_col_insertions,
                                      all_factor_insertions,
                                      all_requirement_extensions,
                                      all_requirement_insertions,
                                      all_row_insertions,
                                      requirement_corroboration)

pytest_plugins = [
    'tests.fixtures.obstructions_requirements',
    'tests.fixtures.simple_tiling'
]


def test_all_cell_insertions_points(simple_tiling):
    strats = set([tuple(s.comb_classes)
                  for s in all_cell_insertions(simple_tiling, maxreqlen=1)])
    assert all(len(s) == 2 for s in strats)
    actual = set()
    actual.add((Tiling(
        obstructions=[Obstruction(Perm((0,)), [(0, 1)])],
        requirements=[[Requirement(Perm((0, 1)), [(0, 0), (1, 0)]),
                       Requirement(Perm((0, 1)), [(0, 0), (1, 1)])]]),
                Tiling(
        obstructions=[Obstruction(Perm((0,)), [(1, 0)])],
        requirements=[[Requirement(Perm((0,)), [(0, 1)])],
                      [Requirement(Perm((0, 1)), [(0, 0), (1, 1)])]])))

    actual.add((Tiling(
        obstructions=[Obstruction(Perm((0,)), ((0, 1),)),
                      Obstruction(Perm((0,)), ((1, 0),))],
        requirements=[[Requirement(Perm((0, 1)), ((0, 0), (1, 1)))]]),
        Tiling(
        obstructions=[Obstruction(Perm((0,)), ((0, 1),))],
        requirements=[[Requirement(Perm((0,)), ((1, 0),))],
                      [Requirement(Perm((0, 1)), ((0, 0), (1, 0))),
                       Requirement(Perm((0, 1)), ((0, 0), (1, 1)))]])))

    actual.add((Tiling(obstructions=[Obstruction(Perm(tuple()), tuple())]),
                Tiling(
        obstructions=[Obstruction(Perm((1, 0)), ((0, 1), (1, 0)))],
        requirements=[[Requirement(Perm((0,)), ((0, 0),))],
                      [Requirement(Perm((0, 1)), ((0, 0), (1, 0))),
                       Requirement(Perm((0, 1)), ((0, 0), (1, 1)))]])))

    actual.add((Tiling(
        requirements=[[Requirement(Perm((0, 1)), ((0, 0), (1, 0)))]]),
        Tiling(
        obstructions=[Obstruction(Perm((1, 0)), ((0, 1), (1, 0)))],
        requirements=[[Requirement(Perm((0,)), ((1, 1),))],
                      [Requirement(Perm((0, 1)), ((0, 0), (1, 0))),
                       Requirement(Perm((0, 1)), ((0, 0), (1, 1)))]])))
    print(simple_tiling)
    assert strats == actual


def test_all_cell_insertions(typical_redundant_requirements,
                             typical_redundant_obstructions):
    tiling = Tiling(obstructions=typical_redundant_obstructions,
                    requirements=typical_redundant_requirements)
    strats = set([tuple(s.comb_classes)
                  for s in all_cell_insertions(tiling, maxreqlen=3)])
    assert all(len(s) == 2 for s in strats)
    assert ((Tiling(
        obstructions=typical_redundant_obstructions + [
            Obstruction(Perm((0, 1, 2)), [(0, 1), (0, 1), (0, 1)])],
        requirements=typical_redundant_requirements),
        Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements + [
            [Requirement(Perm((0, 1, 2)), [(0, 1), (0, 1), (0, 1)])]])
    ) in strats)


def test_all_requirement_extension():
    t = Tiling.from_string('123_132').add_single_cell_requirement(
        Perm((0, 1)), (0, 0))
    strats = set([tuple(s.comb_classes)
                  for s in all_requirement_extensions(t, maxreqlen=3)])
    actual = set([
        (t.add_single_cell_obstruction(Perm((2, 0, 1)), (0, 0)),
         t.add_single_cell_requirement(Perm((2, 0, 1)), (0, 0))),
        (t.add_single_cell_obstruction(Perm((1, 0, 2)), (0, 0)),
         t.add_single_cell_requirement(Perm((1, 0, 2)), (0, 0))),
        (t.add_single_cell_obstruction(Perm((1, 2, 0)), (0, 0)),
         t.add_single_cell_requirement(Perm((1, 2, 0)), (0, 0))),
    ])
    assert actual == strats


def test_all_row_insertion():
    t = Tiling(obstructions=[
        Obstruction(Perm((0, 1)), ((0, 0),)*2),
        Obstruction(Perm((0, 1)), ((1, 0),)*2),
        Obstruction(Perm((0, 1, 2)), ((0, 1),)*3),
    ], requirements=[
        [Requirement(Perm((0, 1)), ((0, 1),)*2)]
    ])
    strats = set([tuple(s.comb_classes)
                  for s in all_row_insertions(t)])
    actual = set([
        (Tiling(obstructions=[Obstruction(Perm((0, 1, 2)), ((0, 0),)*3)],
                requirements=[[Requirement(Perm((0, 1)), ((0, 0),)*2)]]),
         t.add_list_requirement([Requirement(Perm((0,)), ((0, 0),)),
                                 Requirement(Perm((0,)), ((1, 0),)), ])), ])
    assert actual == strats
    assert (next(all_row_insertions(t)).formal_step ==
            'Either row 0 is empty or not.')


def test_all_col_insertion():
    t = Tiling(obstructions=[
        Obstruction(Perm((0, 1)), ((0, 0),)*2),
        Obstruction(Perm((0, 1)), ((1, 0),)*2),
        Obstruction(Perm((0, 1, 2)), ((0, 1),)*3),
    ], requirements=[
        [Requirement(Perm((0, 1)), ((0, 1),)*2)]
    ])
    strats = set([tuple(s.comb_classes)
                  for s in all_col_insertions(t)])
    actual = set([
        (t.add_single_cell_obstruction(Perm((0,)), (1, 0)),
         t.add_single_cell_requirement(Perm((0,)), (1, 0)),)
    ])
    assert actual == strats
    assert (next(all_col_insertions(t)).formal_step ==
            'Either column 1 is empty or not.')


def test_all_requirement_insertion():
    t = Tiling(obstructions=[
        Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
        Obstruction(Perm((0, 1)), ((1, 0), (1, 0))),
        Obstruction(Perm((0, 1)), ((0, 0), (1, 0))),
    ])
    strats = set(tuple(s.comb_classes)
                 for s in all_requirement_insertions(t, 2))
    assert len(strats) == 5
    strat_formal_steps = (
        set(s.formal_step for s in all_requirement_insertions(t, 2)))
    assert 'Insert 0 in cell (1, 0).' in strat_formal_steps
    assert 'Insert 10: (0, 0), (1, 0).' in strat_formal_steps


def test_all_factor_insertions():
    t = Tiling(obstructions=[
        Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
        Obstruction(Perm((0, 1)), ((1, 0), (1, 0))),
        Obstruction(Perm((1, 0)), ((1, 1), (1, 1))),
        Obstruction(Perm((1, 0)), ((1, 2), (1, 2))),
        Obstruction(Perm((0, 1, 2)), ((0, 0), (1, 1), (1, 2))),
        Obstruction(Perm((0, 1)), ((0, 0), (1, 0))),
    ])
    strats = set(tuple(s.comb_classes)
                 for s in all_factor_insertions(t))
    assert len(strats) == 2
    strat_formal_steps = (
        set(s.formal_step for s in all_factor_insertions(t)))
    assert 'Insert 0 in cell (0, 0).' in strat_formal_steps
    assert 'Insert 01: (1, 1), (1, 2).' in strat_formal_steps


def test_requirement_corroboration(typical_redundant_requirements,
                                   typical_redundant_obstructions):
    tiling = Tiling(
        obstructions=[Obstruction(Perm((1, 0)), [(0, 1), (1, 0)])],
        requirements=[[Requirement(Perm((0, 1)), [(0, 0), (1, 0)]),
                       Requirement(Perm((0, 1)), [(0, 0), (1, 1)])]])
    reqins = list(strat.comb_classes
                  for strat in requirement_corroboration(tiling, None))
    assert len(reqins) == 2
    strat1, strat2 = reqins

    assert len(strat1) == 2
    til1, til2 = strat1
    assert til1 == Tiling(
        obstructions=[Obstruction(Perm((0, 1)), [(0, 0), (1, 0)]),
                      Obstruction(Perm((1, 0)), [(0, 1), (1, 0)])],
        requirements=[[Requirement(Perm((0,)), [(0, 0)])],
                      [Requirement(Perm((0,)), [(1, 1)])]])
    assert til2 == Tiling(
        obstructions=[],
        requirements=[[Requirement(Perm((0, 1)), [(0, 0), (1, 0)])]])

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements)
    reqins = list(strat.comb_classes
                  for strat in requirement_corroboration(tiling, None))
    assert len(reqins) == sum(len(reqs) for reqs in tiling.requirements
                              if len(reqs) > 1)
    til1, til2 = reqins[0]
    assert (set([til1, til2]) == set([
        Tiling(requirements=[
            [Requirement(Perm((0, 1)), ((2, 0), (3, 1)))],
            [Requirement(Perm((1, 0)), ((3, 2), (3, 1)))],
            [Requirement(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 2)))],
            [Requirement(Perm((0, 1, 2)), ((2, 2), (2, 2), (2, 2))),
             Requirement(Perm((1, 0, 2)), ((0, 0), (0, 0), (0, 0)))]],
            obstructions=typical_redundant_obstructions),
        Tiling(requirements=[
            [Requirement(Perm((0, 1)), ((2, 0), (3, 1)))],
            [Requirement(Perm((1, 0)), ((3, 2), (3, 1)))],
            [Requirement(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 3))),
             Requirement(Perm((1, 0, 2)), ((0, 0), (1, 0), (2, 2))),
             Requirement(Perm((1, 0, 2)), ((0, 1), (1, 0), (2, 2)))],
            [Requirement(Perm((0, 1, 2)), ((2, 2), (2, 2), (2, 2))),
             Requirement(Perm((1, 0, 2)), ((0, 0), (0, 0), (0, 0)))]],
            obstructions=(typical_redundant_obstructions +
                          [Obstruction(Perm((0, 1, 2)),
                                       ((0, 0), (1, 0), (2, 2)))]))]))


def test_requirement_extensions(typical_obstructions_with_local,
                                typical_requirements_with_local):
    tiling = Tiling(obstructions=typical_obstructions_with_local,
                    requirements=typical_requirements_with_local)
    strats = set([frozenset(s.comb_classes)
                  for s in all_requirement_extensions(tiling, maxreqlen=3)])

    actual = set([
        frozenset([
            tiling.add_single_cell_obstruction(Perm((0, 1)), (0, 0)),
            tiling.add_single_cell_requirement(Perm((0, 1)), (0, 0))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((1, 0)), (0, 0)),
            tiling.add_single_cell_requirement(Perm((1, 0)), (0, 0))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((0, 1, 2)), (0, 0)),
            tiling.add_single_cell_requirement(Perm((0, 1, 2)), (0, 0))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((0, 2, 1)), (0, 0)),
            tiling.add_single_cell_requirement(Perm((0, 2, 1)), (0, 0))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((1, 0, 2)), (0, 0)),
            tiling.add_single_cell_requirement(Perm((1, 0, 2)), (0, 0))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((1, 2, 0)), (0, 0)),
            tiling.add_single_cell_requirement(Perm((1, 2, 0)), (0, 0))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((2, 0, 1)), (0, 0)),
            tiling.add_single_cell_requirement(Perm((2, 0, 1)), (0, 0))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((2, 1, 0)), (0, 0)),
            tiling.add_single_cell_requirement(Perm((2, 1, 0)), (0, 0))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((1, 0)), (3, 1)),
            tiling.add_single_cell_requirement(Perm((1, 0)), (3, 1))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((2, 1, 0)), (3, 1)),
            tiling.add_single_cell_requirement(Perm((2, 1, 0)), (3, 1))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((2, 1, 0)), (2, 0)),
            tiling.add_single_cell_requirement(Perm((2, 1, 0)), (2, 0))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((0, 2, 1)), (2, 2)),
            tiling.add_single_cell_requirement(Perm((0, 2, 1)), (2, 2))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((1, 0, 2)), (2, 2)),
            tiling.add_single_cell_requirement(Perm((1, 0, 2)), (2, 2))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((1, 2, 0)), (2, 2)),
            tiling.add_single_cell_requirement(Perm((1, 2, 0)), (2, 2))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((2, 0, 1)), (2, 2)),
            tiling.add_single_cell_requirement(Perm((2, 0, 1)), (2, 2))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((2, 1, 0)), (2, 2)),
            tiling.add_single_cell_requirement(Perm((2, 1, 0)), (2, 2))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((0, 1)), (3, 0)),
            tiling.add_single_cell_requirement(Perm((0, 1)), (3, 0))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((1, 0)), (3, 0)),
            tiling.add_single_cell_requirement(Perm((1, 0)), (3, 0))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((0, 1, 2)), (3, 0)),
            tiling.add_single_cell_requirement(Perm((0, 1, 2)), (3, 0))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((1, 0, 2)), (3, 0)),
            tiling.add_single_cell_requirement(Perm((1, 0, 2)), (3, 0))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((1, 2, 0)), (3, 0)),
            tiling.add_single_cell_requirement(Perm((1, 2, 0)), (3, 0))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((2, 0, 1)), (3, 0)),
            tiling.add_single_cell_requirement(Perm((2, 0, 1)), (3, 0))
        ]),
        frozenset([
            tiling.add_single_cell_obstruction(Perm((2, 1, 0)), (3, 0)),
            tiling.add_single_cell_requirement(Perm((2, 1, 0)), (3, 0))
        ])])
    assert strats == actual
