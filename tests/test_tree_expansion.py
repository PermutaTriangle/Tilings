import pytest

from tilings.strategy_pack import TileScopePack
from tilings.tilescope import TileScope


@pytest.mark.timeout(20)
def test_expansion():
    css = TileScope(
        "012_0321_1320_2103_2301_2310_3102_3201", TileScopePack.point_placements()
    )
    tree = css.auto_search()
    expansion_pack = TileScopePack.point_placements().expansion_pack()
    expanded_tree = tree.expand_tree(expansion_pack, css=TileScope)
    assert expanded_tree is not None
