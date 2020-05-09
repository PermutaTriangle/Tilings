from itertools import chain
from typing import Iterable, Optional, List

from logzero import logger

from comb_spec_searcher import StrategyPack, Strategy
from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIRS
from tilings import Tiling
from tilings import strategies as strat


class TileScopePack(StrategyPack):
    # Method to add power to a pack
    # Pack are immutable, these methods return a new pack.

    def fix_one_by_one(self, basis: Iterable[Perm]) -> "TileScopePack":
        basis = tuple(basis)

        def replace_list(strats):
            """Return a new list with the replaced 1x1 strat."""
            res = []
            for strategy in strats:
                if isinstance(strategy, strat.OneByOneVerificationStrategy):
                    if strategy.basis:
                        logger.warn("Basis changed in OneByOneVerificationStrategy")
                    res.append(strategy.change_basis(basis))
                else:
                    res.append(strategy)
            return res

        return self.__class__(
            ver_strats=replace_list(self.ver_strats),
            inferral_strats=replace_list(self.inferral_strats),
            initial_strats=replace_list(self.initial_strats),
            expansion_strats=list(map(replace_list, self.expansion_strats)),
            name=self.name,
            symmetries=self.symmetries,
            iterative=self.iterative,
        )

    def make_fusion(self, component: bool = False) -> "TileScopePack":
        """Create a new pack by adding fusion to the current pack."""
        if component:
            return self.add_initial(
                strat.ComponentFusionStrategyGenerator(), "component_fusion"
            )
        return self.add_initial(strat.FusionStrategyGenerator(), "fusion")

    def make_elementary(self) -> "TileScopePack":
        """
        Create a new pack by using only one by one and elementary
        verification.
        """
        if (
            strat.ElementaryVerificationStrategy() in self
            and strat.OneByOneVerificationStrategy() in self
            and len(self.ver_strats) == 2
            and self.iterative
        ):
            raise ValueError("The pack is already elementary.")
        pack = self.make_iterative()
        pack = pack.add_verification(strat.OneByOneVerificationStrategy(), replace=True)
        return pack.add_verification(
            strat.ElementaryVerificationStrategy(), "elementary"
        )

    def make_database(self) -> "TileScopePack":
        """
        Create a new pack by adding database verification to the current pack.
        """
        return self.add_verification(strat.DatabaseVerificationStrategy(), "database")

    def add_all_symmetry(self) -> "TileScopePack":
        """Create a new pack by turning on symmetry on the current pack."""
        if self.symmetries:
            raise ValueError("Symmetries already turned on.")
        return super().add_symmetry(strat.AllSymmetriesStrategy(), "symmetries")

    # Creation of the base pack
    @classmethod
    def all_the_strategies(cls, length: int = 1) -> "TileScopePack":
        return TileScopePack(
            initial_strats=[
                strat.AllFactorStrategy(unions=True),
                strat.RequirementCorroborationStrategy(),
            ],
            ver_strats=[
                strat.OneByOneVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ],
            inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityStrategy(),
            ],
            expansion_strats=[
                [
                    strat.AllCellInsertionStrategy(maxreqlen=length),
                    strat.AllRequirementInsertionStrategy(),
                ],
                [strat.AllPlacementsStrategy()],
            ],
            name="all_the_strategies",
        )

    @classmethod
    def pattern_placements(
        cls, length: int = 1, partial: bool = False,
    ) -> "TileScopePack":
        name = "{}{}{}_placements".format(
            "length_{}_".format(length) if length > 1 else "",
            "partial_" if partial else "",
            "pattern" if length > 1 else "point",
        )
        return TileScopePack(
            initial_strats=[strat.PatternPlacementStrategy(partial=partial)],
            ver_strats=[
                strat.OneByOneVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ],
            inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityStrategy(),
            ],
            expansion_strats=[
                [
                    strat.AllFactorStrategy(unions=True),
                    strat.AllCellInsertionStrategy(maxreqlen=length),
                ],
                [strat.RequirementCorroborationStrategy()],
            ],
            name=name,
        )

    @classmethod
    def point_placements(
        cls, length: int = 1, partial: bool = False
    ) -> "TileScopePack":
        name = "{}{}point_placements".format(
            "length_{}_".format(length) if length > 1 else "",
            "partial_" if partial else "",
        )
        return TileScopePack(
            initial_strats=[
                strat.AllFactorStrategy(),
                strat.RequirementCorroborationStrategy(),
            ],
            ver_strats=[
                strat.OneByOneVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ],
            inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityStrategy(),
            ],
            expansion_strats=[
                [strat.AllCellInsertionStrategy(maxreqlen=length)],
                [strat.PatternPlacementStrategy()],
            ],
            name=name,
        )

    @classmethod
    def insertion_point_placements(cls, length: int = 1) -> "TileScopePack":
        name = "insertion_"
        if length > 1:
            name += "length_{}_".format(length)
        name += "point_placements"
        return TileScopePack(
            initial_strats=[
                strat.AllFactorStrategy(),
                strat.RequirementCorroborationStrategy(),
                strat.AllCellInsertionStrategy(maxreqlen=length, ignore_parent=True),
            ],
            ver_strats=[
                strat.OneByOneVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ],
            inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityStrategy(),
            ],
            expansion_strats=[[strat.PatternPlacementStrategy()]],
            name=name,
        )

    @classmethod
    def regular_insertion_encoding(cls, direction: int) -> "TileScopePack":
        """This pack finds insertion encodings."""
        if direction not in DIRS:
            raise ValueError("Must be direction in {}.".format(DIRS))
        place_row = direction in (DIR_NORTH, DIR_SOUTH)
        place_col = not place_row
        name = "regular_insertion_encoding_{}".format(
            {
                DIR_EAST: "left",
                DIR_WEST: "right",
                DIR_NORTH: "bottom",
                DIR_SOUTH: "top",
            }[direction]
        )
        return TileScopePack(
            initial_strats=[
                strat.AllFactorStrategy(),
                strat.RequirementCorroborationStrategy(),
                strat.AllCellInsertionStrategy(ignore_parent=True),
            ],
            ver_strats=[strat.BasicVerificationStrategy()],
            inferral_strats=[],
            expansion_strats=[
                [
                    strat.RowAndColumnPlacementStrategy(
                        place_col=place_col, place_row=place_row
                    )
                ]
            ],
            name=name,
        )

    @classmethod
    def row_and_col_placements(
        cls, row_only: bool = False, col_only: bool = False, partial: bool = False
    ) -> "TileScopePack":
        if row_only and col_only:
            raise ValueError("Can't be row and col only.")
        place_row = not col_only
        place_col = not row_only
        both = place_col and place_row
        name = "{}{}{}{}_placements".format(
            "partial_" if partial else "",
            "row" if not col_only else "",
            "_and_" if both else "",
            "col" if not row_only else "",
        )
        rowcol_strat = strat.RowAndColumnPlacementStrategy(
            place_row=place_row, place_col=place_col, partial=partial
        )
        return TileScopePack(
            initial_strats=[
                strat.AllFactorStrategy(),
                strat.RequirementCorroborationStrategy(),
            ],
            ver_strats=[
                strat.OneByOneVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ],
            inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityStrategy(),
            ],
            expansion_strats=[[rowcol_strat]],
            name=name,
        )

    @classmethod
    def insertion_row_and_col_placements(
        cls, row_only=False, col_only=False
    ) -> "TileScopePack":
        pack = cls.row_and_col_placements(row_only, col_only)
        pack.name = "insertion_" + pack.name
        pack = pack.add_initial(
            strat.AllCellInsertionStrategy(maxreqlen=1, ignore_parent=True)
        )
        return pack

    @classmethod
    def only_root_placements(
        cls, length: int = 3, max_num_req: Optional[int] = 1,
    ) -> "TileScopePack":
        name = "only_length_{}_root_placements".format(length)
        return TileScopePack(
            initial_strats=[
                strat.RootInsertionStrategy(maxreqlen=length, max_num_req=max_num_req),
                strat.AllFactorStrategy(
                    unions=True, ignore_parent=False, workable=False
                ),
            ],
            ver_strats=[
                strat.OneByOneVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ],
            inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityStrategy(),
            ],
            expansion_strats=[
                [strat.PatternPlacementStrategy()],
                [strat.RequirementCorroborationStrategy()],
            ],
            name=name,
        )

    @classmethod
    def requirement_placements(
        cls, length: int = 2, partial: bool = False
    ) -> "TileScopePack":
        name = "{}{}requirement_placements".format(
            "length_{}_".format(length) if length != 2 else "",
            "partial_" if partial else "",
        )
        return TileScopePack(
            initial_strats=[
                strat.AllFactorStrategy(),
                strat.RequirementCorroborationStrategy(),
            ],
            ver_strats=[
                strat.OneByOneVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ],
            inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityStrategy(),
            ],
            expansion_strats=[
                [strat.AllRequirementInsertionStrategy(maxreqlen=length)],
                [strat.PatternPlacementStrategy(partial=partial)],
            ],
            name=name,
        )
