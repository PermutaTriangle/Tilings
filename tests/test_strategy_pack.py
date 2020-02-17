import json

import pytest

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
        pytest.fail('to_jsonable does not return a dict. \n'
                    'Returned: {}'.format(d))
    try:
        json_str = json.dumps(d)
    except TypeError as e:
        pytest.fail('The to_jsonable method returns a dictionnary that can '
                    'not be encoded as json string\n'
                    'Got error: {}'.format(e))
    sp_new = TileScopePack.from_dict(json.loads(json_str))
    return sp_new


pack = [
    TileScopePack.all_the_strategies(),
    TileScopePack.all_the_strategies().make_fusion(),
    TileScopePack.all_the_strategies().make_database(),
    TileScopePack.all_the_strategies().make_elementary(),
    TileScopePack.all_the_strategies().add_symmetry(),
    (TileScopePack.all_the_strategies().make_fusion().add_symmetry()
     .make_database()),
    TileScopePack.point_placements(),
    TileScopePack.pattern_placements(3),
    TileScopePack.insertion_point_placements(),
    TileScopePack.regular_insertion_encoding(3),
    TileScopePack.row_and_col_placements(),
    TileScopePack.row_and_col_placements(row_only=True),
    TileScopePack.insertion_row_and_col_placements(),
    TileScopePack.only_root_placements(3),
    TileScopePack.only_root_placements(3),
    TileScopePack.requirement_placements(2),
]


@pytest.mark.parametrize("strategy_pack", pack)
def test_json_encoding(strategy_pack):
    strategy_pack_new = json_encode_decode(strategy_pack)
    assert_same_pack(strategy_pack, strategy_pack_new)
