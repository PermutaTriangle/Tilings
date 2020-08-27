import json
from itertools import product

import pytest

from permuta import Perm
from permuta.misc import DIRS
from tilings import strategies as strat
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


packs = (
    length(TileScopePack.all_the_strategies)
    + partial(TileScopePack.insertion_point_placements)
    + row_col_partial(TileScopePack.insertion_row_and_col_placements)
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
)

packs.extend(
    [pack.make_database() for pack in packs]
    + [pack.make_elementary() for pack in packs]
    + [pack.make_fusion() for pack in packs]
    + [pack.add_all_symmetry() for pack in packs]
    + [pack.make_interleaving() for pack in packs]
    + [pack.make_database().add_all_symmetry() for pack in packs]
    + [pack.make_fusion().add_all_symmetry() for pack in packs]
    + [pack.make_interleaving().make_tracked() for pack in packs]
)


@pytest.mark.parametrize("strategy_pack", packs)
def test_json_encoding(strategy_pack):
    strategy_pack_new = json_encode_decode(strategy_pack)
    assert_same_pack(strategy_pack, strategy_pack_new)


def test_fix_one_by_one():
    pack = TileScopePack.point_placements()
    assert not pack.ver_strats[2].basis
    fixed_pack = pack.fix_one_by_one([Perm((0, 1, 2, 3))])
    assert isinstance(pack.ver_strats[2], strat.OneByOneVerificationStrategy)
    assert not pack.ver_strats[2].basis
    assert isinstance(fixed_pack, TileScopePack)
    assert isinstance(fixed_pack.ver_strats[2], strat.OneByOneVerificationStrategy)
    assert fixed_pack.ver_strats[2].basis == (Perm((0, 1, 2, 3)),)
