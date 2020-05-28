from permuta import Perm
from tilings import GriddedPerm, Tiling
from tilings.strategies import (
    CellInsertionFactory,
    FactorInsertionFactory,
    RequirementCorroborationFactory,
    RequirementExtensionFactory,
    RequirementInsertionFactory,
    RootInsertionFactory,
)

pytest_plugins = [
    "tests.fixtures.obstructions_requirements",
    "tests.fixtures.simple_tiling",
]


def test_all_cell_insertions_points(simple_tiling):
    point_insertion = CellInsertionFactory(maxreqlen=1)
    assert str(point_insertion) == "point insertion"
    rules = set(
        [tuple(s(simple_tiling).children) for s in point_insertion(simple_tiling)]
    )
    assert all(len(s) == 2 for s in rules)
    actual = set()
    actual.add(
        (
            Tiling(
                obstructions=[GriddedPerm(Perm((0,)), [(0, 1)])],
                requirements=[
                    [
                        GriddedPerm(Perm((0, 1)), [(0, 0), (1, 0)]),
                        GriddedPerm(Perm((0, 1)), [(0, 0), (1, 1)]),
                    ]
                ],
            ),
            Tiling(
                obstructions=[GriddedPerm(Perm((0,)), [(1, 0)])],
                requirements=[
                    [GriddedPerm(Perm((0,)), [(0, 1)])],
                    [GriddedPerm(Perm((0, 1)), [(0, 0), (1, 1)])],
                ],
            ),
        )
    )

    actual.add(
        (
            Tiling(
                obstructions=[
                    GriddedPerm(Perm((0,)), ((0, 1),)),
                    GriddedPerm(Perm((0,)), ((1, 0),)),
                ],
                requirements=[[GriddedPerm(Perm((0, 1)), ((0, 0), (1, 1)))]],
            ),
            Tiling(
                obstructions=[GriddedPerm(Perm((0,)), ((0, 1),))],
                requirements=[
                    [GriddedPerm(Perm((0,)), ((1, 0),))],
                    [
                        GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
                        GriddedPerm(Perm((0, 1)), ((0, 0), (1, 1))),
                    ],
                ],
            ),
        )
    )

    actual.add(
        (
            Tiling(obstructions=[GriddedPerm.empty_perm()]),
            Tiling(
                obstructions=[GriddedPerm(Perm((1, 0)), ((0, 1), (1, 0)))],
                requirements=[
                    [GriddedPerm(Perm((0,)), ((0, 0),))],
                    [
                        GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
                        GriddedPerm(Perm((0, 1)), ((0, 0), (1, 1))),
                    ],
                ],
            ),
        )
    )

    actual.add(
        (
            Tiling(requirements=[[GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0)))]]),
            Tiling(
                obstructions=[GriddedPerm(Perm((1, 0)), ((0, 1), (1, 0)))],
                requirements=[
                    [GriddedPerm(Perm((0,)), ((1, 1),))],
                    [
                        GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
                        GriddedPerm(Perm((0, 1)), ((0, 0), (1, 1))),
                    ],
                ],
            ),
        )
    )
    assert rules == actual


def test_all_cell_insertions(
    typical_redundant_requirements, typical_redundant_obstructions
):
    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
    )
    rules = set(
        [tuple(s(tiling).children) for s in CellInsertionFactory(maxreqlen=3)(tiling)]
    )
    assert all(len(s) == 2 for s in rules)
    assert (
        Tiling(
            obstructions=typical_redundant_obstructions
            + [GriddedPerm(Perm((0, 1, 2)), [(0, 1), (0, 1), (0, 1)])],
            requirements=typical_redundant_requirements,
        ),
        Tiling(
            obstructions=typical_redundant_obstructions,
            requirements=typical_redundant_requirements
            + [[GriddedPerm(Perm((0, 1, 2)), [(0, 1), (0, 1), (0, 1)])]],
        ),
    ) in rules


def test_requirement_extensions(
    typical_obstructions_with_local, typical_requirements_with_local
):
    t = Tiling.from_string("123_132").add_single_cell_requirement(Perm((0, 1)), (0, 0))
    strats = set(
        [tuple(s(t).children) for s in RequirementExtensionFactory(maxreqlen=3)(t)]
    )
    actual = set(
        [
            (
                t.add_single_cell_obstruction(Perm((2, 0, 1)), (0, 0)),
                t.add_single_cell_requirement(Perm((2, 0, 1)), (0, 0)),
            ),
            (
                t.add_single_cell_obstruction(Perm((1, 0, 2)), (0, 0)),
                t.add_single_cell_requirement(Perm((1, 0, 2)), (0, 0)),
            ),
            (
                t.add_single_cell_obstruction(Perm((1, 2, 0)), (0, 0)),
                t.add_single_cell_requirement(Perm((1, 2, 0)), (0, 0)),
            ),
        ]
    )
    assert actual == strats

    tiling = Tiling(
        obstructions=typical_obstructions_with_local,
        requirements=typical_requirements_with_local,
    )
    strats = set(
        [
            frozenset(s(tiling).children)
            for s in RequirementExtensionFactory(maxreqlen=3)(tiling)
        ]
    )
    actual = set(
        [
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((0, 1)), (0, 0)),
                    tiling.add_single_cell_requirement(Perm((0, 1)), (0, 0)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((1, 0)), (0, 0)),
                    tiling.add_single_cell_requirement(Perm((1, 0)), (0, 0)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((0, 1, 2)), (0, 0)),
                    tiling.add_single_cell_requirement(Perm((0, 1, 2)), (0, 0)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((0, 2, 1)), (0, 0)),
                    tiling.add_single_cell_requirement(Perm((0, 2, 1)), (0, 0)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((1, 0, 2)), (0, 0)),
                    tiling.add_single_cell_requirement(Perm((1, 0, 2)), (0, 0)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((1, 2, 0)), (0, 0)),
                    tiling.add_single_cell_requirement(Perm((1, 2, 0)), (0, 0)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((2, 0, 1)), (0, 0)),
                    tiling.add_single_cell_requirement(Perm((2, 0, 1)), (0, 0)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((2, 1, 0)), (0, 0)),
                    tiling.add_single_cell_requirement(Perm((2, 1, 0)), (0, 0)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((1, 0)), (3, 1)),
                    tiling.add_single_cell_requirement(Perm((1, 0)), (3, 1)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((2, 1, 0)), (3, 1)),
                    tiling.add_single_cell_requirement(Perm((2, 1, 0)), (3, 1)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((2, 1, 0)), (2, 0)),
                    tiling.add_single_cell_requirement(Perm((2, 1, 0)), (2, 0)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((0, 2, 1)), (2, 2)),
                    tiling.add_single_cell_requirement(Perm((0, 2, 1)), (2, 2)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((1, 0, 2)), (2, 2)),
                    tiling.add_single_cell_requirement(Perm((1, 0, 2)), (2, 2)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((1, 2, 0)), (2, 2)),
                    tiling.add_single_cell_requirement(Perm((1, 2, 0)), (2, 2)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((2, 0, 1)), (2, 2)),
                    tiling.add_single_cell_requirement(Perm((2, 0, 1)), (2, 2)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((2, 1, 0)), (2, 2)),
                    tiling.add_single_cell_requirement(Perm((2, 1, 0)), (2, 2)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((0, 1)), (3, 0)),
                    tiling.add_single_cell_requirement(Perm((0, 1)), (3, 0)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((1, 0)), (3, 0)),
                    tiling.add_single_cell_requirement(Perm((1, 0)), (3, 0)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((0, 1, 2)), (3, 0)),
                    tiling.add_single_cell_requirement(Perm((0, 1, 2)), (3, 0)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((1, 0, 2)), (3, 0)),
                    tiling.add_single_cell_requirement(Perm((1, 0, 2)), (3, 0)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((1, 2, 0)), (3, 0)),
                    tiling.add_single_cell_requirement(Perm((1, 2, 0)), (3, 0)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((2, 0, 1)), (3, 0)),
                    tiling.add_single_cell_requirement(Perm((2, 0, 1)), (3, 0)),
                ]
            ),
            frozenset(
                [
                    tiling.add_single_cell_obstruction(Perm((2, 1, 0)), (3, 0)),
                    tiling.add_single_cell_requirement(Perm((2, 1, 0)), (3, 0)),
                ]
            ),
        ]
    )
    assert strats == actual


def test_all_requirement_insertion():
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
        ]
    )
    strats = set(tuple(s(t).children) for s in RequirementInsertionFactory(2)(t))
    assert len(strats) == 5
    strat_formal_steps = set(
        s(t).formal_step for s in RequirementInsertionFactory(2)(t)
    )
    assert "insert 0 in cell (1, 0)" in strat_formal_steps
    assert "insert 10: (0, 0), (1, 0)" in strat_formal_steps


def test_all_factor_insertions():
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
            GriddedPerm(Perm((1, 0)), ((1, 1), (1, 1))),
            GriddedPerm(Perm((1, 0)), ((1, 2), (1, 2))),
            GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 1), (1, 2))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
        ]
    )
    strats = set(tuple(s(t).children) for s in FactorInsertionFactory()(t))
    assert len(strats) == 2
    strat_formal_steps = set(s(t).formal_step for s in FactorInsertionFactory()(t))
    assert "insert 0 in cell (0, 0)" in strat_formal_steps
    assert "insert 01: (1, 1), (1, 2)" in strat_formal_steps


def test_requirement_corroboration(
    typical_redundant_requirements, typical_redundant_obstructions
):
    tiling = Tiling(
        obstructions=[GriddedPerm(Perm((1, 0)), [(0, 1), (1, 0)])],
        requirements=[
            [
                GriddedPerm(Perm((0, 1)), [(0, 0), (1, 0)]),
                GriddedPerm(Perm((0, 1)), [(0, 0), (1, 1)]),
            ]
        ],
    )
    reqins = list(
        strat(tiling).children for strat in RequirementCorroborationFactory()(tiling)
    )
    assert len(reqins) == 2
    strat1, strat2 = reqins

    assert len(strat1) == 2
    til1, til2 = strat1
    assert til1 == Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), [(0, 0), (1, 0)]),
            GriddedPerm(Perm((1, 0)), [(0, 1), (1, 0)]),
        ],
        requirements=[
            [GriddedPerm(Perm((0,)), [(0, 0)])],
            [GriddedPerm(Perm((0,)), [(1, 1)])],
        ],
    )
    assert til2 == Tiling(
        obstructions=[], requirements=[[GriddedPerm(Perm((0, 1)), [(0, 0), (1, 0)])]]
    )

    tiling = Tiling(
        obstructions=typical_redundant_obstructions,
        requirements=typical_redundant_requirements,
    )
    reqins = list(
        strat(tiling).children for strat in RequirementCorroborationFactory()(tiling)
    )
    assert len(reqins) == sum(
        len(reqs) for reqs in tiling.requirements if len(reqs) > 1
    )
    til1, til2 = reqins[0]
    assert set([til1, til2]) == set(
        [
            Tiling(
                requirements=[
                    [GriddedPerm(Perm((0, 1)), ((2, 0), (3, 1)))],
                    [GriddedPerm(Perm((1, 0)), ((3, 2), (3, 1)))],
                    [GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 2)))],
                    [
                        GriddedPerm(Perm((0, 1, 2)), ((2, 2), (2, 2), (2, 2))),
                        GriddedPerm(Perm((1, 0, 2)), ((0, 0), (0, 0), (0, 0))),
                    ],
                ],
                obstructions=typical_redundant_obstructions,
            ),
            Tiling(
                requirements=[
                    [GriddedPerm(Perm((0, 1)), ((2, 0), (3, 1)))],
                    [GriddedPerm(Perm((1, 0)), ((3, 2), (3, 1)))],
                    [
                        GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 3))),
                        GriddedPerm(Perm((1, 0, 2)), ((0, 0), (1, 0), (2, 2))),
                        GriddedPerm(Perm((1, 0, 2)), ((0, 1), (1, 0), (2, 2))),
                    ],
                    [
                        GriddedPerm(Perm((0, 1, 2)), ((2, 2), (2, 2), (2, 2))),
                        GriddedPerm(Perm((1, 0, 2)), ((0, 0), (0, 0), (0, 0))),
                    ],
                ],
                obstructions=(
                    typical_redundant_obstructions
                    + [GriddedPerm(Perm((0, 1, 2)), ((0, 0), (1, 0), (2, 2)))]
                ),
            ),
        ]
    )


def test_root_insertion():
    t_2x2 = Tiling(
        obstructions=(
            GriddedPerm(Perm((0, 1)), ((0, 0),) * 2),
            GriddedPerm(Perm((0, 1)), ((1, 1),) * 2),
        )
    )
    t = Tiling.from_string("1234")
    assert list(RootInsertionFactory()(t_2x2)) == []
    assert len(list(RootInsertionFactory(maxreqlen=3)(t))) == 9
    t_w_req = t.add_single_cell_requirement(Perm((0, 1)), (0, 0))
    assert len(list(RootInsertionFactory(maxreqlen=3)(t_w_req))) == 7
    rules = list(RootInsertionFactory(maxreqlen=3, max_num_req=1)(t_w_req))
    assert len(rules) == 5
    t_w_req2 = t.add_single_cell_requirement(Perm((0, 1, 2)), (0, 0))
    print("==" * 30)
    rules = list(RootInsertionFactory(maxreqlen=4, max_num_req=1)(t_w_req2))
    assert len(rules) == 9
    rules = list(RootInsertionFactory(maxreqlen=4, max_num_req=2)(t_w_req2))
    for rule in rules:
        rule = rule(t_w_req2)
        print(rule.children[1])
    assert len(rules) == 29


def test_cell_insertion():
    t1 = Tiling.from_string("123")
    ci1 = CellInsertionFactory(maxreqlen=3)
    assert set(ci1.req_lists_to_insert(t1)) == set(
        [
            (GriddedPerm.single_cell(Perm((0,)), (0, 0)),),
            (GriddedPerm.single_cell(Perm((0, 1)), (0, 0)),),
            (GriddedPerm.single_cell(Perm((1, 0)), (0, 0)),),
            (GriddedPerm.single_cell(Perm((0, 2, 1)), (0, 0)),),
            (GriddedPerm.single_cell(Perm((1, 0, 2)), (0, 0)),),
            (GriddedPerm.single_cell(Perm((1, 2, 0)), (0, 0)),),
            (GriddedPerm.single_cell(Perm((2, 0, 1)), (0, 0)),),
            (GriddedPerm.single_cell(Perm((2, 1, 0)), (0, 0)),),
        ]
    )
    assert len(list(ci1(t1))) == 8
    t2 = t1.add_single_cell_requirement(Perm((2, 1, 0)), (0, 0))
    ci2 = CellInsertionFactory(maxreqlen=3)
    assert set(ci2.req_lists_to_insert(t2)) == set(
        [
            (GriddedPerm.single_cell(Perm((0, 1)), (0, 0)),),
            (GriddedPerm.single_cell(Perm((0, 2, 1)), (0, 0)),),
            (GriddedPerm.single_cell(Perm((1, 0, 2)), (0, 0)),),
            (GriddedPerm.single_cell(Perm((1, 2, 0)), (0, 0)),),
            (GriddedPerm.single_cell(Perm((2, 0, 1)), (0, 0)),),
        ]
    )
    assert len(list(ci2(t2))) == 5
    ci3 = CellInsertionFactory(maxreqlen=3, extra_basis=[Perm((0, 2, 1))])
    assert set(ci3.req_lists_to_insert(t1)) == set(
        [
            (GriddedPerm.single_cell(Perm((0,)), (0, 0)),),
            (GriddedPerm.single_cell(Perm((0, 1)), (0, 0)),),
            (GriddedPerm.single_cell(Perm((1, 0)), (0, 0)),),
            (GriddedPerm.single_cell(Perm((1, 0, 2)), (0, 0)),),
            (GriddedPerm.single_cell(Perm((1, 2, 0)), (0, 0)),),
            (GriddedPerm.single_cell(Perm((2, 0, 1)), (0, 0)),),
            (GriddedPerm.single_cell(Perm((2, 1, 0)), (0, 0)),),
        ]
    )
    assert len(list(ci3(t1))) == 7


def test_crossing_insertion():
    t = Tiling(
        obstructions=[
            GriddedPerm(Perm((0, 1)), ((0, 0), (0, 0))),
            GriddedPerm(Perm((0, 1)), ((0, 0), (1, 0))),
            GriddedPerm(Perm((0, 1)), ((1, 0), (1, 0))),
        ],
        requirements=[[GriddedPerm(Perm((0,)), ((0, 0),))]],
    )
    ci = RequirementInsertionFactory(maxreqlen=2)
    assert set(ci.req_lists_to_insert(t)) == set(
        [
            (GriddedPerm(Perm((0,)), ((0, 0),)),),
            (GriddedPerm(Perm((0,)), ((1, 0),)),),
            (GriddedPerm(Perm((1, 0)), ((0, 0), (0, 0))),),
            (GriddedPerm(Perm((1, 0)), ((1, 0), (1, 0))),),
            (GriddedPerm(Perm((1, 0)), ((0, 0), (1, 0))),),
        ]
    )
    assert len(list(ci(t))) == 5
    ci2 = RequirementInsertionFactory(maxreqlen=3)
    assert len(list(ci2(t))) == 9
    ci3 = RequirementInsertionFactory(maxreqlen=3, extra_basis=[Perm((2, 1, 0))])
    assert len(list(ci3(t))) == 5
