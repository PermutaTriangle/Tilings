import argparse
import inspect
from typing import Callable, Dict

from tilings import Tiling
from tilings.strategy_pack import TileScopePack
from tilings.tilescope import TileScope

PackBuilder = Callable[..., TileScopePack]

BASE_PACK = {
    "all_the_strategies": TileScopePack.all_the_strategies,
    "pattern_placements": TileScopePack.pattern_placements,
    "point_placements": TileScopePack.point_placements,
    "insertion_point_placements": TileScopePack.insertion_point_placements,
    "row_and_col_placements": TileScopePack.row_and_col_placements,
    "insertion_row_and_col_placements": TileScopePack.insertion_row_and_col_placements,
    "only_root_placements": TileScopePack.only_root_placements,
    "requirement_placements": TileScopePack.requirement_placements,
}  # type: Dict[str, PackBuilder]


def list_stratpacks(args: argparse.Namespace) -> int:
    """
    Prints out every strategy pack available.
    """
    for pack in BASE_PACK:
        print(pack)
    return 0


def valid_kwarg_or_error(func, kwarg_name, pack_name):
    if kwarg_name not in inspect.signature(func).parameters:
        parser.error("Invalid argument {} for {}".format(kwarg_name, pack_name))


def build_pack(args: argparse.Namespace) -> TileScopePack:
    if args.strategy_pack not in BASE_PACK:
        parser.error(
            "Invalid strategy pack. Use 'tilescope list' to see" " available pack"
        )
    pack_builder = BASE_PACK[args.strategy_pack]  # type: PackBuilder
    kwargs = dict()
    if args.length is not None:
        valid_kwarg_or_error(pack_builder, "length", args.strategy_pack)
        kwargs["length"] = args.length
    pack = pack_builder(**kwargs)
    if args.fusion:
        pack = pack.make_fusion()
    if args.database:
        pack = pack.make_database()
    if args.symmetries:
        pack = pack.add_all_symmetry()
    if args.elementary:
        pack = pack.make_elementary()
    return pack


def search_tree(args):
    """
    Search for a tree.
    """
    pack = build_pack(args)
    start_class = Tiling.from_string(args.basis)
    css = TileScope(start_class, pack)
    css.auto_search(status_update=30)
    return 0


parser = argparse.ArgumentParser(
    description="A command line tool for the TileScope algorithm."
)
subparsers = parser.add_subparsers(title="subcommands")

# List command
helpstr = "List all the strategy pack available"
parser_list = subparsers.add_parser("list", help=helpstr, description=helpstr)
parser_list.set_defaults(func=list_stratpacks)

# Tree command
helpstr = (
    "Search for a tree with for a given permutation class with a "
    "given strategy pack."
)
parser_tree = subparsers.add_parser("tree", help=helpstr, description=helpstr)
parser_tree.add_argument(
    "basis",
    type=str,
    help="The basis of the "
    "permutation class. The permutation can be 1 or "
    "0-based and are separated by an underscore",
)
parser_tree.add_argument(
    "strategy_pack",
    type=str,
    help="The strategy "
    "pack to run. The strategy defines the set of "
    "strategy that will be used to  expand the "
    "universe of combinatorial classes.",
)
parser_tree.add_argument(
    "-l", "--length", type=int, help="Change the length parameter of the pack."
)
parser_tree.add_argument(
    "-f", "--fusion", action="store_true", help="Adds fusion to the pack."
)
parser_tree.add_argument(
    "-d",
    "--database",
    action="store_true",
    help="Adds database verification to the pack.",
)
parser_tree.add_argument(
    "-s", "--symmetries", action="store_true", help="Adds symmetries to the pack"
)
parser_tree.add_argument(
    "-e", "--elementary", action="store_true", help="Makes the pack elementary."
)
parser_tree.set_defaults(func=search_tree)


def main():
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.error("Invalid command")
    return args.func(args)


if __name__ == "__main__":
    main()