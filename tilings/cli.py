import argparse
import inspect
from functools import partial
from typing import Callable, Dict

from logzero import logger

from comb_spec_searcher.exception import IncorrectGeneratingFunctionError
from permuta import Perm
from permuta.misc import DIR_SOUTH, DIR_WEST
from permuta.permutils import (
    is_insertion_encodable_maximum,
    is_insertion_encodable_rightmost,
)
from tilings import Tiling
from tilings.hints import (
    extension_placement_arguments,
    find_one_point_extension_chain,
    hints_for,
)
from tilings.strategies.requirement_insertion import (
    CellInsertionFactory,
    RequirementInsertionFactory,
    TargetedCellInsertionFactory,
)
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
        parser.error(f"Invalid argument {kwarg_name} for {pack_name}")


def build_pack(args: argparse.Namespace) -> TileScopePack:
    if args.strategy_pack not in BASE_PACK:
        parser.error(
            "Invalid strategy pack. Use 'tilescope list' to see available packs. "
            "Perhaps you got the order wrong? A valid command should be of "
            "the form 'tilescope spec {basis} {pack}'."
        )

    pack_builder: PackBuilder = BASE_PACK[args.strategy_pack]
    kwargs = {}
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
    if args.symmetries:
        pack = pack.add_all_symmetry()
    if args.elementary:
        pack = pack.make_elementary()
    if getattr(args, "rotational_cuts", False):  # callers' own namespaces may lack it
        pack = pack.add_rotational_cuts()
    if getattr(args, "extension_placement", False):
        pack = pack_with_extension_placement(pack, args.basis)
    return pack


# the strategies that insert the point requirements that a partial placement places
POINT_INSERTIONS = (
    CellInsertionFactory,
    RequirementInsertionFactory,
    TargetedCellInsertionFactory,
)


def pack_with_extension_placement(pack: TileScopePack, basis: str) -> TileScopePack:
    """
    Return the pack with the partial placements and obstruction inferral that the
    one-point extension hint for the basis asks for (tilings.hints). Exit with a
    parser error if the basis is no one-point extension of a basis, or if the pack
    has a requirement placement or obstruction inferral already. Warn if the pack
    inserts no point requirements, as the placements then have no point to place.
    """
    chain = find_one_point_extension_chain(
        Perm.to_standard(pattern) for pattern in basis.split("_")
    )
    if not chain:
        parser.error(
            "The basis is not every one-point extension of a basis, so "
            "--extension-placement does not apply."
        )
    try:
        extended = pack.add_extension_placement(*extension_placement_arguments(chain))
    except ValueError:
        parser.error(
            "--extension-placement does not go with this pack: it has a requirement "
            "placement or obstruction inferral already, and a pack holds one of each."
        )
    strategies = [*pack.initial_strats, *pack.inferral_strats]
    strategies += [strategy for level in pack.expansion_strats for strategy in level]
    if not any(isinstance(strategy, POINT_INSERTIONS) for strategy in strategies):
        logger.warning(
            "--extension-placement places the point of a point requirement, and %s "
            "inserts none, so the placement may not apply; point_placements does.",
            pack.name,
        )
    return extended


def search_spec(args):
    """
    Search for a specification.
    """
    pack = build_pack(args)
    start_class = Tiling.from_string(args.basis)
    basis = (obstruction.patt for obstruction in start_class.obstructions)
    for hint in hints_for(basis):
        if not hint.followed_by(pack):
            logger.info("Hint: %s", hint.message)
    css = TileScope(start_class, pack)
    spec = css.auto_search(status_update=30)
    try:
        genf = spec.get_genf()
    except (IncorrectGeneratingFunctionError, NotImplementedError) as error:
        # as for a rotational cut, whose equation has a derivative, or for
        # catalytic variables
        logger.info(
            "The generating function cannot be computed from this specification "
            "(%s: %s)",
            type(error).__name__,
            error,
        )
    else:
        logger.info("The generating function is %s", genf)
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
    "-s", "--symmetries", action="store_true", help="Adds symmetries to the pack"
)
parser_tree.add_argument(
    "-e", "--elementary", action="store_true", help="Makes the pack elementary."
)
parser_tree.add_argument(
    "-r",
    "--rotational-cuts",
    action="store_true",
    help="Adds the rotational cuts to the pack, for classes closed under rotation.",
)
parser_tree.add_argument(
    "-x",
    "--extension-placement",
    action="store_true",
    help="Adds a partial placement and obstruction inferral to the pack, for classes "
    "whose basis is every one-point extension of a basis. The placement places the "
    "points of point requirements, so the pack must insert them, as point_placements "
    "does.",
)
parser_tree.set_defaults(func=search_spec)


def main():
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.error("Invalid command")
    return args.func(args)


if __name__ == "__main__":
    main()
