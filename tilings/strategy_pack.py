from copy import copy
from itertools import chain
from typing import Optional

from comb_spec_searcher import StrategyPack
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIRS
from tilings import strategies as strat
from tilings.strategies.abstract_strategy import Strategy


class TileScopePack(StrategyPack):

    def __contains__(self, strategy: Strategy) -> bool:
        """
        Check if the pack contains a strategy.

        Two strategy from the same Strategy class are consider the same even if
        they have different parameter.
        """
        strats_in_pack = chain(
            self.initial_strats,
            self.ver_strats,
            self.inferral_strats,
            *self.expansion_strats
        )
        return any(
            strat.__class__ == strategy.__class__ for strat in strats_in_pack
        )

    def __repr__(self) -> str:
        s = '{}(\n'.format(self.__class__.__name__)
        s += '    initial_strats=[\n'
        for st in self.initial_strats:
            s += '        {!r},\n'.format(st)
        s += '    ], ver_strats=[\n'
        for st in self.ver_strats:
            s += '        {!r},\n'.format(st)
        s += '    ], inferral_strats=[\n'
        for st in self.inferral_strats:
            s += '        {!r},\n'.format(st)
        s += '    ], expansion_strats=[\n'
        for sl in self.expansion_strats:
            s += '        [\n'
            for st in sl:
                s += '            {!r},\n'.format(st)
            s += '        ],\n'
        s += '    ],\n'
        s += '    name={!r},\n'.format(self.name)
        s += '    symmetries={!r},\n'.format(self.symmetries)
        s += '    forward_equivalence={!r},\n'.format(self.forward_equivalence)
        s += '    iterative={!r},\n'.format(self.iterative)
        s += ')'
        return s

    def __str__(self) -> str:
        # Redefine to use the Strategy __str__
        super().__str__(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TileScopePack):
            return NotImplemented
        raise NotImplementedError

    def __copy__(self) -> 'TileScopePack':
        return TileScopePack(
            name=self.name,
            initial_strats=copy(self.initial_strats),
            ver_strats=copy(self.ver_strats),
            inferral_strats=copy(self.inferral_strats),
            expansion_strats=[
                copy(strat_list) for strat_list in self.expansion_strats
            ],
            symmetries=copy(self.symmetries),
            forward_equivalence=self.forward_equivalence,
            iterative=self.iterative,
        )

    # JSON methods
    def to_jsonable(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, d: dict) -> 'TileScopePack':
        raise NotImplementedError

    # Method to add power to a pack
    # Pack are immutable, these methods return a new pack.
    def make_fusion(self) -> 'TileScopePack':
        """Create a new pack by adding fusion to the current pack."""
        raise NotImplementedError

    def make_elementary(self) -> 'TileScopePack':
        """
        Create a new pack by using only one by one and elementary
        verification.
        """
        raise NotImplementedError

    def make_database(self) -> 'TileScopePack':
        """
        Create a new pack by adding database verification to the current pack.
        """
        raise NotImplementedError

    def add_symmetry(self) -> 'TileScopePack':
        """Create a new pack by turning on symmetry on the current pack."""
        raise NotImplementedError

    # Creation of the base pack
    @classmethod
    def all_the_strategies(cls, length: int = 1) -> 'TileScopePack':
        return TileScopePack(
            initial_strats=[
                strat.FactorStrategy(union=True),
                strat.RequirementCorroborationStrategy(),
            ], ver_strats=[
                strat.LocalVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
                strat.OneByOneVerificationStrategy(),
            ], inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityStrategy(),
            ], expansion_strats=[
                [
                    strat.AllCellInsertionStrategy(maxreqlen=length),
                    strat.AllRequirementInsertionStrategy(),
                ],
                [
                    strat.AllPlacementsStrategy(),
                ]
            ],
            name="all_the_strategies")

    @classmethod
    def pattern_placements(cls, length: int = 1,
                           partial_placements: bool = False,
                           ) -> 'TileScopePack':
        name = "{}{}{}_placements".format(
            "length_{}_".format(length) if length > 1 else "",
            "partial_" if partial_placements else "",
            "pattern" if length > 1 else "point")
        return TileScopePack(
            initial_strats=[
                strat.RequirementPlacementStrategy(partial=partial_placements)
            ], ver_strats=[
                strat.OneByOneVerificationStrategy(),
                strat.LocalVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ], inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityStrategy(),
            ], expansion_strats=[
                [
                    strat.FactorStrategy(union=True),
                    strat.AllCellInsertionStrategy(maxreqlen=length),
                ],
                [
                    strat.RequirementCorroborationStrategy(),
                ]
            ],
            name=name)

    @classmethod
    def point_placements(cls, length: int = 1,
                         partial_placements: bool = False
                         ) -> 'TileScopePack':
        name = "{}{}point_placements".format(
            "length_{}_".format(length) if length > 1 else "",
            "partial_" if partial_placements else "")
        return TileScopePack(
            initial_strats=[
                strat.FactorStrategy(),
                strat.RequirementCorroborationStrategy(),
            ], ver_strats=[
                strat.OneByOneVerificationStrategy(),
                strat.LocalVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ], inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityStrategy(),
            ], expansion_strats=[
                [
                    strat.AllCellInsertionStrategy(maxreqlen=length),
                ],
                [
                    strat.RequirementPlacementStrategy(),
                ]
            ],
            name=name)

    @classmethod
    def insertion_point_placements(cls, length: int = 1) -> 'TileScopePack':
        name = 'insertion_'
        if length > 1:
            name += "length_{}_".format(length)
        name += 'point_placements'
        return TileScopePack(
            initial_strats=[
                strat.FactorStrategy(),
                strat.RequirementCorroborationStrategy(),
                strat.AllCellInsertionStrategy(maxreqlen=length,
                                               ignore_parent=True),
            ], ver_strats=[
                strat.OneByOneVerificationStrategy(),
                strat.LocalVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ], inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityStrategy(),
            ], expansion_strats=[[
                strat.RequirementPlacementStrategy(),
            ]],
            name=name)

    @classmethod
    def regular_insertion_encoding(cls,
                                   direction: Optional[int] = None
                                   ) -> 'TileScopePack':
        """This pack finds insertion encodings."""
        if direction not in DIRS:
            raise ValueError("Must be direction in {}.".format(DIRS))
        place_row = direction in (DIR_NORTH, DIR_SOUTH)
        place_col = not place_row
        name = "regular_insertion_encoding_{}".format(
            {DIR_EAST: 'left', DIR_WEST: 'right',
             DIR_NORTH: 'bottom', DIR_SOUTH: 'top'}[direction]
        )
        return TileScopePack(
            initial_strats=[
                strat.FactorStrategy(),
                strat.RequirementCorroborationStrategy(),
                strat.AllCellInsertionStrategy(ignore_parent=True),
            ], ver_strats=[
                strat.BasicVerificationStrategy(),
            ],
            inferral_strats=[],
            expansion_strats=[[
                strat.RowAndColumnPlacementStrategy(place_col=place_col,
                                                    place_row=place_row)
            ]],
            name=name)

    @classmethod
    def row_and_col_placements(cls, row_only: bool = False,
                               col_only: bool = False) -> 'TileScopePack':
        if row_only and col_only:
            raise ValueError("Can't be row and col only.")
        place_row = not col_only
        place_col = not row_only
        both = place_col and place_row
        name = "{}{}{}_placements".format("row" if not col_only else "",
                                          "_and_" if both else "",
                                          "col" if not row_only else "")
        expansion_strats = [
            strat.RowAndColumnPlacementStrategy(place_row=place_row,
                                                place_col=place_col),
        ]
        return TileScopePack(
            initial_strats=[
                strat.FactorStrategy(),
                strat.RequirementCorroborationStrategy(),
            ], ver_strats=[
                strat.OneByOneVerificationStrategy(),
                strat.LocalVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy()
            ], inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityStrategy(),
            ], expansion_strats=[
                expansion_strats
            ],
            name=name)

    @classmethod
    def insertion_row_and_col_placements(cls, row_only=False,
                                         col_only=False) -> 'TileScopePack':
        pack = cls.row_and_col_placements(row_only, col_only)
        pack.initial_strats.append(
            strat.AllCellInsertionStrategy(maxreqlen=1, ignore_parent=True)
        )
        pack.name = 'insertion_' + pack.name
        return pack

    @classmethod
    def only_root_placements(cls, length: int = 1) -> 'TileScopePack':
        name = "only_length_{}_root_placements".format(length)
        return TileScopePack(
            initial_strats=[
                strat.RequirementPlacementStrategy(),
                strat.FactorStrategy(),
            ], ver_strats=[
                strat.BasicVerificationStrategy(),
                strat.OneByOneVerificationStrategy(),
                strat.LocalVerificationStrategy(),
            ], inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityStrategy(),
            ], expansion_strats=[[
                strat.RootInsertionStrategy(maxreqlen=length),
            ]],
            name=name)

    @classmethod
    def requirement_placements(cls,
                               length: int = 2,
                               partial_placements: bool = False
                               ) -> 'TileScopePack':
        name = "{}{}requirement_placements".format(
            "length_{}_".format(length) if length != 2 else "",
            "partial_" if partial_placements else ""
        )
        return TileScopePack(
            initial_strats=[
                strat.FactorStrategy(),
                strat.RequirementCorroborationStrategy(),
            ], ver_strats=[
                strat.OneByOneVerificationStrategy(),
                strat.LocalVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ], inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityStrategy(),
            ], expansion_strats=[[
                strat.AllRequirementInsertionStrategy(maxreqlen=length)
            ], [
                strat.RequirementPlacementStrategy(partial=partial_placements)
            ]], name=name)
