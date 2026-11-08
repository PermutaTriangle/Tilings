import json
from itertools import product

import pytest

from permuta import Perm
from permuta.misc import DIRS
from tilings import GriddedPerm, Tiling
from tilings import strategies as strat
from tilings.strategies import AssumptionAndPointJumpingFactory, SlidingFactory
from tilings.strategy_pack import TileScopePack


def assert_same_pack(sp1, sp2):
    """Check that two strategy pack are the same."""
    __tracebackhide__ = True
    assert sp1.__dict__ == sp2.__dict__, "The attributes differ"


def json_encode_decode(sp):
    """Take a strategy, encode it as json and build it back as a strategy."""
    __tracebackhide__ = True
    d = sp.to_jsonable()
    if not isinstance(d, dict):
        pytest.fail("to_jsonable does not return a dict. \n" "Returned: {}".format(d))
    try:
        json_str = json.dumps(d)
    except TypeError as e:
        pytest.fail(
            "The to_jsonable method returns a dictionnary that can "
            "not be encoded as json string\n"
            "Got error: {}".format(e)
        )
    sp_new = TileScopePack.from_dict(json.loads(json_str))
    return sp_new


def length(pack):
    return [pack(length=length) for length in (1, 2, 3)]


def length_maxnumreq_partial(pack):
    return [
        pack(length=length, max_num_req=max_num_req, partial=partial)
        for length, max_num_req, partial in product((1, 2, 3), (1, 2, 3), (True, False))
    ]


def length_partial(pack):
    return [
        pack(length=length, partial=partial)
        for length, partial in product((1, 2, 3), (True, False))
    ]


def partial(pack):
    return [pack(partial=partial) for partial in (True, False)]


def directions(pack):
    return [pack(direction=direction) for direction in DIRS]


def row_col_partial(pack):
    return [
        pack(row_only=row_only, col_only=col_only, partial=partial)
        for row_only, col_only, partial in product(
            (True, False), (True, False), (True, False)
        )
        if not row_only or not col_only
    ]


def length_row_col_partial(pack):
    return [
        pack(length=length, row_only=row_only, col_only=col_only, partial=partial)
        for row_only, col_only, partial in product(
            (True, False), (True, False), (True, False)
        )
        if not row_only or not col_only
        for length in (1, 2, 3)
    ]


packs = (
    length(TileScopePack.all_the_strategies)
    + partial(TileScopePack.insertion_point_placements)
    + partial(TileScopePack.subobstruction_placements)
    + partial(TileScopePack.basis_pattern_insertions)
    + row_col_partial(TileScopePack.insertion_row_and_col_placements)
    + row_col_partial(TileScopePack.insertion_point_row_and_col_placements)
    + length_maxnumreq_partial(TileScopePack.only_root_placements)
    + [
        TileScopePack.only_root_placements(
            length=3, max_num_req=2, max_placement_rules_per_req=100
        )
    ]
    + length_partial(TileScopePack.pattern_placements)
    + length_partial(TileScopePack.point_placements)
    + directions(TileScopePack.regular_insertion_encoding)
    + length_partial(TileScopePack.requirement_placements)
    + row_col_partial(TileScopePack.row_and_col_placements)
    + length(TileScopePack.cell_insertions)
    + length_row_col_partial(TileScopePack.point_and_row_and_col_placements)
    + length_row_col_partial(TileScopePack.requirement_and_row_and_col_placements)
)

packs.extend(
    [pack.make_elementary() for pack in packs]
    + [pack.make_fusion() for pack in packs]
    + [pack.add_all_symmetry() for pack in packs]
    + [pack.make_interleaving() for pack in packs]
    + [pack.make_fusion().add_all_symmetry() for pack in packs]
    + [pack.make_interleaving() for pack in packs]
    + [pack.add_initial(SlidingFactory()) for pack in packs]
    + [pack.add_initial(SlidingFactory(use_symmetries=True)) for pack in packs]
    + [pack.add_initial(AssumptionAndPointJumpingFactory()) for pack in packs]
    + [
        pack.kitchen_sinkify(
            short_obs_len=4, obs_inferral_len=2, tracked=True, level=level
        )
        for pack in packs
        for level in (1, 2, 3, 4, 5)
    ]
)


@pytest.mark.parametrize("strategy_pack", packs)
def test_json_encoding(strategy_pack):
    strategy_pack_new = json_encode_decode(strategy_pack)
    assert_same_pack(strategy_pack, strategy_pack_new)


def test_inject_basis():
    pack = TileScopePack.point_placements()
    assert not pack.ver_strats[2].basis
    fixed_pack = pack.add_basis([Perm((0, 1, 2, 3))])
    assert isinstance(pack.ver_strats[2], strat.OneByOneVerificationStrategy)
    assert not pack.ver_strats[2].basis
    assert isinstance(fixed_pack, TileScopePack)
    assert isinstance(fixed_pack.ver_strats[2], strat.OneByOneVerificationStrategy)
    assert fixed_pack.ver_strats[2].basis == (Perm((0, 1, 2, 3)),)


AV_012_BESIDE_AV_021 = Tiling(
    obstructions=(
        GriddedPerm.single_cell(Perm((0, 1, 2)), (0, 0)),
        GriddedPerm.single_cell(Perm((0, 2, 1)), (1, 0)),
    )
)


def subclass_verification_factories(pack):
    """Return the pack's subclass verification factories, in order."""
    return [
        strategy
        for strategy in pack.ver_strats
        if isinstance(strategy, strat.SubclassVerificationFactory)
    ]


@pytest.mark.parametrize(
    "start_tiling",
    [Tiling.from_string("012"), AV_012_BESIDE_AV_021],
    ids=["1x1", "2x1"],
)
def test_setup_subclass_verification_sets_up_the_perms(start_tiling):
    """A factory with no perms to check gets the nonempty perms shorter than 3 that
    avoid a cell's basis, here all of them, whether the start tiling is 1x1 or 2x1."""
    pack = TileScopePack.point_placements().add_verification(
        strat.SubclassVerificationFactory()
    )
    (factory,) = subclass_verification_factories(
        pack.setup_subclass_verification(start_tiling)
    )
    assert factory.perms_to_check == {Perm((0,)), Perm((0, 1)), Perm((1, 0))}


@pytest.mark.parametrize(
    "start_tiling",
    [Tiling.from_string("012"), AV_012_BESIDE_AV_021],
    ids=["1x1", "2x1"],
)
def test_setup_subclass_verification_keeps_given_perms(start_tiling):
    """A factory whose perms to check are given stays in the pack as it is."""
    factory = strat.SubclassVerificationFactory([Perm((0, 1))])
    pack = TileScopePack.point_placements().add_verification(factory)
    new_pack = pack.setup_subclass_verification(start_tiling)
    assert subclass_verification_factories(new_pack) == [factory]
