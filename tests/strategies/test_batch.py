from permuta import Perm
from tilings import Obstruction, Requirement, Tiling
from tilings.strategies.batch import (AllCellInsertionStrategy,
                                      AllColInsertionStrategy,
                                      AllFactorInsertionStrategy,
                                      AllPlacementsStrategy,
                                      AllPointInsertionStrategy,
                                      AllRequirementExtensionStrategy,
                                      AllRequirementInsertionStrategy,
                                      AllRowInsertionStrategy,
                                      RequirementCorroborationStrategy,
                                      RowAndColumnPlacementStrategy)

pytest_plugins = [
    'tests.fixtures.obstructions_requirements',
    'tests.fixtures.simple_tiling',
]


def test_all_cell_insertions_points(simple_tiling):
    strats = set([tuple(s.comb_classes)
                  for s in AllPointInsertionStrategy()(simple_tiling)])
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
                  for s in AllCellInsertionStrategy(maxreqlen=3)(tiling)])
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


def test_requirement_extensions(typical_obstructions_with_local,
                                typical_requirements_with_local):
    t = Tiling.from_string('123_132').add_single_cell_requirement(
        Perm((0, 1)), (0, 0))
    strats = set([tuple(s.comb_classes)
                  for s in AllRequirementExtensionStrategy(maxreqlen=3)(t)])
    actual = set([
        (t.add_single_cell_obstruction(Perm((2, 0, 1)), (0, 0)),
         t.add_single_cell_requirement(Perm((2, 0, 1)), (0, 0))),
        (t.add_single_cell_obstruction(Perm((1, 0, 2)), (0, 0)),
         t.add_single_cell_requirement(Perm((1, 0, 2)), (0, 0))),
        (t.add_single_cell_obstruction(Perm((1, 2, 0)), (0, 0)),
         t.add_single_cell_requirement(Perm((1, 2, 0)), (0, 0))),
    ])
    assert actual == strats

    tiling = Tiling(obstructions=typical_obstructions_with_local,
                    requirements=typical_requirements_with_local)
    strats = set([
        frozenset(s.comb_classes) for s in
        AllRequirementExtensionStrategy(maxreqlen=3)(tiling)
    ])
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


def test_all_row_insertion():
    t = Tiling(obstructions=[
        Obstruction(Perm((0, 1)), ((0, 0),)*2),
        Obstruction(Perm((0, 1)), ((1, 0),)*2),
        Obstruction(Perm((0, 1, 2)), ((0, 1),)*3),
    ], requirements=[
        [Requirement(Perm((0, 1)), ((0, 1),)*2)]
    ])
    strats = set([tuple(s.comb_classes)
                  for s in AllRowInsertionStrategy()(t)])
    actual = set([
        (Tiling(obstructions=[Obstruction(Perm((0, 1, 2)), ((0, 0),)*3)],
                requirements=[[Requirement(Perm((0, 1)), ((0, 0),)*2)]]),
         t.add_list_requirement([Requirement(Perm((0,)), ((0, 0),)),
                                 Requirement(Perm((0,)), ((1, 0),)), ])), ])
    assert actual == strats
    assert (next(AllRowInsertionStrategy()(t)).formal_step ==
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
                  for s in AllColInsertionStrategy()(t)])
    actual = set([
        (t.add_single_cell_obstruction(Perm((0,)), (1, 0)),
         t.add_single_cell_requirement(Perm((0,)), (1, 0)),)
    ])
    assert actual == strats
    assert (next(AllColInsertionStrategy()(t)).formal_step ==
            'Either column 1 is empty or not.')


def test_all_requirement_insertion():
    t = Tiling(obstructions=[
        Obstruction(Perm((0, 1)), ((0, 0), (0, 0))),
        Obstruction(Perm((0, 1)), ((1, 0), (1, 0))),
        Obstruction(Perm((0, 1)), ((0, 0), (1, 0))),
    ])
    strats = set(tuple(s.comb_classes)
                 for s in AllRequirementInsertionStrategy(2)(t))
    assert len(strats) == 5
    strat_formal_steps = (
        set(s.formal_step for s in AllRequirementInsertionStrategy(2)(t)))
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
                 for s in AllFactorInsertionStrategy()(t))
    assert len(strats) == 2
    strat_formal_steps = (
        set(s.formal_step for s in AllFactorInsertionStrategy()(t)))
    assert 'Insert 0 in cell (0, 0).' in strat_formal_steps
    assert 'Insert 01: (1, 1), (1, 2).' in strat_formal_steps


def test_requirement_corroboration(typical_redundant_requirements,
                                   typical_redundant_obstructions):
    tiling = Tiling(
        obstructions=[Obstruction(Perm((1, 0)), [(0, 1), (1, 0)])],
        requirements=[[Requirement(Perm((0, 1)), [(0, 0), (1, 0)]),
                       Requirement(Perm((0, 1)), [(0, 0), (1, 1)])]])
    reqins = list(strat.comb_classes for strat in
                  RequirementCorroborationStrategy()(tiling))
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
    reqins = list(strat.comb_classes for strat in
                  RequirementCorroborationStrategy()(tiling))
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


def test_row_placement():
    t = Tiling.from_string('132')
    row_placement = RowAndColumnPlacementStrategy(place_col=False,
                                                  place_row=True,
                                                  partial=False)
    partial_row_placement = RowAndColumnPlacementStrategy(place_col=False,
                                                          place_row=True,
                                                          partial=True)
    assert len(list(row_placement(t))) == 2
    assert len(list(partial_row_placement(t))) == 2


def test_col_placement():
    t = Tiling.from_string('132')
    col_placement = RowAndColumnPlacementStrategy(place_col=True,
                                                  place_row=False,
                                                  partial=False)
    partial_col_placement = RowAndColumnPlacementStrategy(place_col=True,
                                                          place_row=False,
                                                          partial=True)
    assert len(list(col_placement(t))) == 2
    assert len(list(partial_col_placement(t))) == 2


def test_row_col_placement():
    t = Tiling.from_string('132')
    cr_placement = RowAndColumnPlacementStrategy(place_col=True,
                                                 place_row=True,
                                                 partial=False)
    partial_cr_placement = RowAndColumnPlacementStrategy(place_col=True,
                                                         place_row=True,
                                                         partial=True)
    assert len(list(cr_placement(t))) == 4
    assert len(list(partial_cr_placement(t))) == 4


def test_all_placements():
    t = Tiling(obstructions=[
        Obstruction(Perm((0, 1)), ((0, 0),)*2),
    ], requirements=[
        [Requirement(Perm((0,)), ((0, 0),))]
    ])
    rules = list(AllPlacementsStrategy()(t))
    assert len(rules) == 24
