import argparse
import inspect
from functools import partial
from typing import Callable, Dict

from logzero import logger

from permuta import Perm
from permuta.misc import DIR_SOUTH, DIR_WEST
from permuta.permutils import (
    is_insertion_encodable_maximum,
    is_insertion_encodable_rightmost,
)
from tilings import Tiling
from tilings.strategy_pack import TileScopePack
from tilings.tilescope import TileScope

PackBuilder = Callable[..., TileScopePack]

BASE_PACK: Dict[str, PackBuilder] = {
    "all_the_strategies": TileScopePack.all_the_strategies,
    "pattern_placements": TileScopePack.pattern_placements,
    "point_placements": TileScopePack.point_placements,
    "insertion_point_placements": TileScopePack.insertion_point_placements,
    "row_and_col_placements": TileScopePack.row_and_col_placements,
    "col_placements": partial(TileScopePack.row_and_col_placements, col_only=True),
    "row_placements": partial(TileScopePack.row_and_col_placements, row_only=True),
    "insertion_row_and_col_placements": TileScopePack.insertion_row_and_col_placements,
    "insertion_row_placements": partial(
        TileScopePack.insertion_row_and_col_placements, row_only=True
    ),
    "insertion_col_placements": partial(
        TileScopePack.insertion_row_and_col_placements, col_only=True
    ),
    "only_root_placements": TileScopePack.only_root_placements,
    "regular_insertion_encoding": TileScopePack.regular_insertion_encoding,
    "requirement_placements": TileScopePack.requirement_placements,
}


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
            "Invalid strategy pack. Use 'tilescope list' to see available packs. "
            "Perhaps you got the order wrong? A valid command should be of "
            "the form 'tilescope spec {basis} {pack}'."
        )

    pack_builder: PackBuilder = BASE_PACK[args.strategy_pack]
    kwargs = dict()
    if args.length is not None:
        valid_kwarg_or_error(pack_builder, "length", args.strategy_pack)
        kwargs["length"] = args.length
    if args.strategy_pack == "regular_insertion_encoding":
        basis = [Perm.to_standard(p) for p in args.basis.split("_")]
        if is_insertion_encodable_maximum(basis):
            kwargs["direction"] = DIR_SOUTH
        elif is_insertion_encodable_rightmost(basis):
            kwargs["direction"] = DIR_WEST
        else:
            parser.error(
                "The basis does not have regular insertion encoding, "
                "so try another pack. Note: the extra args of the 'tilescope' "
                "command don't work with this pack, use instead the packs "
                "insertion_row_and_col_placements which expands in a similar "
                "fashion, but has more powerful strategies."
            )
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


def search_spec(args):
    """
    Search for a specification.
    """
    pack = build_pack(args)
    start_class = Tiling.from_string(args.basis)
    css = TileScope(start_class, pack)
    spec = css.auto_search(status_update=30)
    logger.info("The generating function is %s", spec.get_genf())
    return 0


parser = argparse.ArgumentParser(
    description="A command line tool for the TileScope algorithm."
)
subparsers = parser.add_subparsers(title="subcommands")

# List command
helpstr = "List all the strategy packs available"
parser_list = subparsers.add_parser("list", help=helpstr, description=helpstr)
parser_list.set_defaults(func=list_stratpacks)

# Spec command
helpstr = (
    "Search for a specification for a given permutation class with a given "
    "strategy pack."
)
parser_tree = subparsers.add_parser("spec", help=helpstr, description=helpstr)
parser_tree.add_argument(
    "basis",
    type=str,
    help="The basis of the permutation class. This can be 1- or 0-based and patterns"
    " should be separated by an underscore, e.g. 012_021.",
)
parser_tree.add_argument(
    "strategy_pack",
    type=str,
    help="The strategy pack to run. The strategy pack defines the set of "
    "strategies that will be used when searching for a specification. The "
    "command 'tilescope list' will show you the available packs.",
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
parser_tree.set_defaults(func=search_spec)


def main():
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.error("Invalid command")
    return args.func(args)


if __name__ == "__main__":
    main()
