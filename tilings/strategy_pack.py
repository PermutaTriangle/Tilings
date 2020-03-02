from copy import copy
from itertools import chain
from typing import List

from comb_spec_searcher import StrategyPack
from comb_spec_searcher.utils import get_func_name
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIRS
from tilings import Tiling
from tilings import strategies as strat
from tilings.strategies.abstract_strategy import Strategy


class TileScopePack(StrategyPack):

    ALL_SYMMETRIES_FUNCTIONS = (Tiling.inverse, Tiling.reverse,
                                Tiling.complement, Tiling.antidiagonal,
                                Tiling.rotate90, Tiling.rotate180,
                                Tiling.rotate270)

    def __init__(self, initial_strats: List[Strategy],
                 inferral_strats: List[Strategy],
                 expansion_strats: List[List[Strategy]],
                 ver_strats: List[Strategy],
                 name: str, **kwargs):
        if 'symmetries' in kwargs:
            assert all(sym in TileScopePack.ALL_SYMMETRIES_FUNCTIONS
                       for sym in kwargs['symmetries']), 'Invalid symmetry'
        super().__init__(initial_strats, inferral_strats, expansion_strats,
                         ver_strats, name, **kwargs)

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
        string = ("Looking for {} combinatorial specification"
                  " with the strategies:\n").format(
            'iterative' if self.iterative else 'recursive')
        initial_strats = ", ".join(map(str, self.initial_strats))
        infer_strats = ", ".join(map(str, self.inferral_strats))
        verif_strats = ", ".join(map(str, self.ver_strats))
        string += "Inferral: {}\n".format(infer_strats)
        string += "Initial: {}\n".format(initial_strats)
        string += "Verification: {}\n".format(verif_strats)
        if self.forward_equivalence:
            string += "Using forward equivalence only.\n"
        if self.symmetries:
            symme_strats = ", ".join(get_func_name(f)
                                     for f in self.symmetries)
            string += "Symmetries: {}\n".format(symme_strats)
        for i, strategies in enumerate(self.expansion_strats):
            strats = ", ".join(map(str, strategies))
            string += "Set {}: {}\n".format(i+1, strats)
        return string

    def __eq__(self, other: object):
        if not isinstance(other, StrategyPack):
            return NotImplemented
        return self.__dict__ == other.__dict__

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
        sym = [sym in self.symmetries for sym in
               TileScopePack.ALL_SYMMETRIES_FUNCTIONS]
        assert sum(sym) == len(self.symmetries), "Can't save all symmetries"
        return {
            'name': self.name,
            'initial_strats': [s.to_jsonable() for s in self.initial_strats],
            'inferral_strats': [s.to_jsonable() for s in self.inferral_strats],
            'ver_strats': [s.to_jsonable() for s in self.ver_strats],
            'expansion_strats': [[s.to_jsonable() for s in strat_list]
                                 for strat_list in self.expansion_strats],
            'symmetries': sym,
            'forward_equivalence': self.forward_equivalence,
            'iterative': self.iterative,
        }

    @classmethod
    def from_dict(cls, d: dict) -> 'TileScopePack':
        name = d.pop('name')
        initial_strats = [Strategy.from_dict(strat_dict) for strat_dict in
                          d.pop('initial_strats')]
        inferral_strats = [Strategy.from_dict(strat_dict) for strat_dict in
                           d.pop('inferral_strats')]
        ver_strats = [Strategy.from_dict(strat_dict) for strat_dict in
                      d.pop('ver_strats')]
        expansion_strats = [[Strategy.from_dict(strat_dict) for strat_dict in
                             strat_list] for strat_list in
                            d.pop('expansion_strats')]
        symmetries = list(
            sym for sym, included in
            zip(TileScopePack.ALL_SYMMETRIES_FUNCTIONS, d.pop('symmetries'))
            if included
        )
        d['symmetries'] = symmetries
        return cls(initial_strats, inferral_strats, expansion_strats,
                   ver_strats, name, **d)

    # Method to add power to a pack
    # Pack are immutable, these methods return a new pack.
    def add_initial(self, strategy: Strategy,
                    name_ext: str = '') -> 'TileScopePack':
        """
        Create a new pack with an additional initial strategy and append
        name_ext to the name of the pack.
        """
        if strategy in self:
            raise ValueError(("The strategy {!r} is already in pack."
                              "".format(strategy)))
        new_pack = copy(self)
        new_pack.initial_strats.append(strategy)
        if name_ext:
            new_pack.name = '_'.join([self.name, name_ext])
        return new_pack

    def add_inferral(self, strategy: Strategy,
                     name_ext: str = '') -> 'TileScopePack':
        """
        Create a new pack with an additional inferral strategy and append
        name_ext to the name of the pack.
        """
        if strategy in self:
            raise ValueError(("The strategy {!r} is already in pack."
                              "".format(strategy)))
        new_pack = copy(self)
        new_pack.inferral_strats.append(strategy)
        if name_ext:
            new_pack.name = '_'.join([self.name, name_ext])
        return new_pack

    def add_verification(self, strategy: Strategy,
                         name_ext: str = '') -> 'TileScopePack':
        """
        Create a new pack with an additional verification strategy and append
        name_ext to the name of the pack.
        """
        if strategy in self:
            raise ValueError(("The strategy {!r} is already in pack."
                              "".format(strategy)))
        new_pack = copy(self)
        new_pack.ver_strats.append(strategy)
        if name_ext:
            new_pack.name = '_'.join([self.name, name_ext])
        return new_pack

    def make_fusion(self, component: bool = False) -> 'TileScopePack':
        """Create a new pack by adding fusion to the current pack."""
        if component:
            return self.add_initial(strat.ComponentFusionStrategy(),
                                    'component_fusion')
        return self.add_initial(strat.FusionStrategy(), 'fusion')

    def make_elementary(self) -> 'TileScopePack':
        """
        Create a new pack by using only one by one and elementary
        verification.
        """
        if (strat.ElementaryVerificationStrategy() in self and
            strat.OneByOneVerificationStrategy() in self and
            len(self.ver_strats) == 2 and
                self.forward_equivalence and self.iterative):
            raise ValueError("The pack is already elementary.")
        new_pack = copy(self)
        new_pack.ver_strats = [strat.ElementaryVerificationStrategy(),
                               strat.OneByOneVerificationStrategy()]
        new_pack.name = '_'.join(['elementary', self.name])
        new_pack.forward_equivalence = True
        new_pack.iterative = True
        return new_pack

    def make_database(self) -> 'TileScopePack':
        """
        Create a new pack by adding database verification to the current pack.
        """
        return self.add_verification(strat.DatabaseVerificationStrategy(),
                                     'database')

    def add_symmetry(self) -> 'TileScopePack':
        """Create a new pack by turning on symmetry on the current pack."""
        if self.symmetries:
            raise ValueError("Symmetries already turned on.")
        new_pack = copy(self)
        new_pack.name = '_'.join(['symmetries', self.name])
        new_pack.symmetries = list(TileScopePack.ALL_SYMMETRIES_FUNCTIONS)
        return new_pack

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
    def regular_insertion_encoding(cls, direction: int) -> 'TileScopePack':
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
        rowcol_strat = strat.RowAndColumnPlacementStrategy(place_row=place_row,
                                                           place_col=place_col)
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
                [rowcol_strat]
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
                strat.RequirementPlacementStrategy(ignore_parent=True),
                strat.FactorStrategy(union=True),
            ], ver_strats=[
                strat.BasicVerificationStrategy(),
                strat.OneByOneVerificationStrategy(),
                strat.LocalVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
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
