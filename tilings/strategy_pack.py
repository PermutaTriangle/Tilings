from typing import TYPE_CHECKING, Iterable, List, Optional, Tuple, Union

from logzero import logger

from comb_spec_searcher import StrategyPack
from comb_spec_searcher.strategies import (
    AbstractStrategy,
    Strategy,
    StrategyFactory,
    VerificationStrategy,
)
from permuta import Perm
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIRS
from tilings import strategies as strat
from tilings.strategies.verification import BasisAwareVerificationStrategy

if TYPE_CHECKING:
    from tilings import Tiling

CSSstrategy = Union[Strategy, StrategyFactory, VerificationStrategy]


class TileScopePack(StrategyPack):
    # Method to add power to a pack
    # Pack are immutable, these methods return a new pack.

    def add_basis(self, basis: Iterable[Perm]) -> "TileScopePack":
        """
        Update the pack to add the basis being run to the verifications strategy
        that needs to be aware of it.
        """
        basis = tuple(basis)
        symmetry = bool(self.symmetries)

        def replace_list(
            strats: Tuple[Union[AbstractStrategy, StrategyFactory], ...]
        ) -> List[Union[AbstractStrategy, StrategyFactory]]:
            """Return a new list with the replaced 1x1 strat."""
            res: List[Union[AbstractStrategy, StrategyFactory]] = []
            for strategy in strats:
                if isinstance(strategy, BasisAwareVerificationStrategy):
                    if strategy.basis:
                        logger.warning("Basis changed in %s", strategy)
                    res.append(strategy.change_basis(basis, symmetry))
                elif isinstance(strategy, strat.SymmetriesFactory):
                    if strategy.basis:
                        logger.warning("Basis changed in %s", strategy)
                    res.append(strategy.change_basis(basis))
                elif hasattr(strategy, "change_basis"):
                    logger.warning("Basis changed in %s", strategy)
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
            symmetries=replace_list(self.symmetries),
            iterative=self.iterative,
        )

    def setup_subclass_verification(self, start_tiling: "Tiling") -> "TileScopePack":
        """
        If the subclass verification strategy already has a list of perms to check,
        we leave it alone. Otherwise we:
         - compute the cell basis for each cell
         - consider the permutations avoiding some cell basis
         - add to the list of perms to check any perm that avoids some cell basis and
           has length strictly smaller than the maximum length cell basis element.
        """

        def replace_list(
            strats: Tuple[Union[AbstractStrategy, StrategyFactory], ...]
        ) -> List[Union[AbstractStrategy, StrategyFactory]]:
            """
            Find subclass verification and alter its perms_to_check variable.
            """
            res: List[Union[AbstractStrategy, StrategyFactory]] = []
            for strategy in strats:
                if isinstance(strategy, strat.SubclassVerificationFactory):
                    printed_log = False
                    if strategy.perms_to_check is None:
                        new_perms_to_check = set()
                        cell_bases = set(
                            tuple(obs) for obs, _ in start_tiling.cell_basis().values()
                        )
                        max_length = (
                            max(max(len(b) for b in basis) for basis in cell_bases) - 1
                        )
                        perm_gen = Perm.up_to_length(max_length)
                        for perm in perm_gen:
                            if len(perm) == 0:
                                continue
                            if any(perm.avoids(*basis) for basis in cell_bases):
                                new_perms_to_check.add(perm)
                        res.append(strategy.change_perms(new_perms_to_check))
                        if start_tiling.dimensions == (1, 1):
                            logger.info(
                                "SubclassVerification set up to check the proper "
                                "principal subclasses of Av(%s)",
                                ", ".join(map(str, cell_bases.pop())),
                            )
                            printed_log = True
                    if not printed_log:
                        assert strategy.perms_to_check is not None
                        logger.info(
                            "SubclassVerification set up to check the subclasses: "
                            "Av(%s)",
                            "), Av(".join(map(str, strategy.perms_to_check)),
                        )
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

    def make_tracked(self):
        """Make a fusion pack tracked."""

        def replace_list(strats):
            """Return a new list with strats tracked."""
            res = []
            for strategy in strats:
                d = strategy.to_jsonable()
                if not d.get("tracked", True):
                    d["tracked"] = True
                    strategy = AbstractStrategy.from_dict(d)
                res.append(strategy)
            return res

        pack = self.__class__(
            ver_strats=replace_list(self.ver_strats),
            inferral_strats=replace_list(self.inferral_strats),
            initial_strats=replace_list(self.initial_strats),
            expansion_strats=list(map(replace_list, self.expansion_strats)),
            name=self.name.replace("untracked", "tracked"),
            symmetries=self.symmetries,
            iterative=self.iterative,
        )
        if all(
            not isinstance(strategy, strat.AddAssumptionFactory) for strategy in pack
        ):
            pack = pack.add_initial(strat.AddAssumptionFactory(), apply_first=True)
        if all(
            not isinstance(strategy, strat.RearrangeAssumptionFactory)
            for strategy in pack
        ):
            pack = pack.add_initial(
                strat.RearrangeAssumptionFactory(), apply_first=True
            )
        if strat.ComponentFusionFactory() in pack:
            if all(
                not isinstance(strategy, strat.DetectComponentsStrategy)
                for strategy in pack
            ):
                pack = pack.add_initial(
                    strat.DetectComponentsStrategy(ignore_parent=True)
                )
            if all(
                not isinstance(strategy, strat.ComponentVerificationStrategy)
                for strategy in pack
            ):
                pack = pack.add_verification(strat.ComponentVerificationStrategy())
        return pack

    def make_fusion(
        self,
        component: bool = False,
        tracked: bool = True,
        apply_first: bool = False,
        isolation_level: Optional[str] = None,
    ) -> "TileScopePack":
        """
        Create a new pack by adding fusion to the current pack.

        If component, it will add component fusion.
        If tracked, it will return the pack for finding a tracked tree.
        If apply_first, it will add fusion to the front of the initial strategies.
        """
        name = "tracked_" if tracked else "untracked_"
        name += "component_fusion" if component else "fusion"
        if isolation_level is not None:
            name += f"_{isolation_level}"
        if component:
            fusion_strat: StrategyFactory = strat.ComponentFusionFactory(
                tracked=tracked, isolation_level=isolation_level
            )
        else:
            fusion_strat = strat.FusionFactory(
                tracked=tracked, isolation_level=isolation_level
            )
        pack = self.add_initial(fusion_strat, name, apply_first=apply_first)
        if tracked:
            pack = pack.add_initial(strat.AddAssumptionFactory(), apply_first=True)
            if component:
                pack = pack.add_initial(
                    strat.DetectComponentsStrategy(ignore_parent=True), apply_first=True
                )
                pack = pack.add_verification(strat.ComponentVerificationStrategy())
            pack = pack.add_initial(
                strat.RearrangeAssumptionFactory(), apply_first=True
            )
        return pack

    def make_interleaving(
        self, tracked: bool = True, unions: bool = False
    ) -> "TileScopePack":
        """
        Return a new pack where the factor strategy is replaced with an
        interleaving factor strategy.

        If unions is set to True it will overwrite unions on the strategy.
        """

        def replace_list(strats):
            """Return a new list with the replaced tracked factor strategy."""
            res = []
            for strategy in strats:
                if isinstance(strategy, strat.FactorFactory):
                    d = strategy.to_jsonable()
                    d["interleaving"] = "all"
                    d["tracked"] = tracked
                    d["unions"] = d["unions"] or unions
                    res.append(AbstractStrategy.from_dict(d))
                else:
                    res.append(strategy)
            return res

        name = f"{self.name}_{'' if tracked else 'un'}tracked_interleaving"
        if unions:
            name += "_unions"

        pack = self.__class__(
            ver_strats=replace_list(self.ver_strats),
            inferral_strats=replace_list(self.inferral_strats),
            initial_strats=replace_list(self.initial_strats),
            expansion_strats=list(map(replace_list, self.expansion_strats)),
            name=name,
            symmetries=self.symmetries,
            iterative=self.iterative,
        )

        if tracked:
            pack = pack.add_initial(strat.AddAssumptionFactory(), apply_first=True)

        return pack

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
        pack = pack.add_verification(strat.BasicVerificationStrategy(), replace=True)
        pack = pack.add_verification(strat.OneByOneVerificationStrategy())
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
        return super().add_symmetry(strat.SymmetriesFactory(), "symmetries")

    def kitchen_sinkify(  # pylint: disable=R0912
        self, short_obs_len: int, obs_inferral_len: int, tracked: bool
    ) -> "TileScopePack":
        """
        Create a new pack with the following added:
            Short Obs verification (unless short_obs_len = 0)
            No Root Cell verification
            Database verification
            Deflation
            Point and/or Assumption Jumping
            Generalized Monotone Sliding
            Free Cell Reduction
            Requirement corroboration
            Obstruction Inferral (unless obs_inferral_len = 0)
            Symmetries
            Point Pointing
            Unfusion
            Targeted Row/Col Placements when fusable
        Will be made tracked or not, depending on preference.
        Note that nothing is done with positive / point corroboration, requirement
        corroboration, or database verification.
        """

        ks_pack = self.__class__(
            ver_strats=self.ver_strats,
            inferral_strats=self.inferral_strats,
            initial_strats=self.initial_strats,
            expansion_strats=self.expansion_strats,
            name=self.name,
            symmetries=self.symmetries,
            iterative=self.iterative,
        )

        if short_obs_len > 0:
            try:
                ks_pack = ks_pack.add_verification(
                    strat.ShortObstructionVerificationStrategy(short_obs_len)
                )
            except ValueError:
                pass

        try:
            ks_pack = ks_pack.add_verification(strat.NoRootCellVerificationStrategy())
        except ValueError:
            pass

        try:
            ks_pack = ks_pack.add_verification(strat.DatabaseVerificationStrategy())
        except ValueError:
            pass

        try:
            ks_pack = ks_pack.add_initial(strat.DeflationFactory(tracked))
        except ValueError:
            pass

        try:
            ks_pack = ks_pack.add_initial(strat.AssumptionAndPointJumpingFactory())
        except ValueError:
            pass

        try:
            ks_pack = ks_pack.add_initial(strat.MonotoneSlidingFactory())
        except ValueError:
            pass

        try:
            ks_pack = ks_pack.add_initial(strat.CellReductionFactory(tracked))
        except ValueError:
            pass

        try:
            ks_pack = ks_pack.add_initial(strat.RequirementCorroborationFactory())
        except ValueError:
            pass

        if obs_inferral_len > 0:
            try:
                ks_pack = ks_pack.add_inferral(
                    strat.ObstructionInferralFactory(obs_inferral_len)
                )
            except ValueError:
                pass

        ks_pack = ks_pack.make_interleaving(tracked=tracked, unions=True)

        try:
            ks_pack = ks_pack.add_all_symmetry()
        except ValueError:
            pass

        if tracked:
            ks_pack = ks_pack.make_tracked()

        ks_pack.expansion_strats = ks_pack.expansion_strats + (
            (
                strat.AssumptionPointingFactory(),
                strat.RequirementPointingFactory(),
                strat.PointingStrategy(),
                strat.UnfusionFactory(),
                strat.FusableRowAndColumnPlacementFactory(),
            ),
        )

        ks_pack.name += "_kitchen_sink"

        return ks_pack

    # Creation of the base pack
    @classmethod
    def all_the_strategies(cls, length: int = 1) -> "TileScopePack":
        initial_strats: List[CSSstrategy] = [
            strat.FactorFactory(),
            strat.PointCorroborationFactory(),
        ]
        if length > 1:
            initial_strats.append(strat.RequirementCorroborationFactory())

        return TileScopePack(
            initial_strats=initial_strats,
            ver_strats=[
                strat.BasicVerificationStrategy(),
                strat.InsertionEncodingVerificationStrategy(),
                strat.OneByOneVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ],
            inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityFactory(),
            ],
            expansion_strats=[
                [
                    strat.RequirementInsertionFactory(maxreqlen=length),
                    strat.AllPlacementsFactory(),
                ],
            ],
            name=f"all_the_strategies_{length}",
        )

    @classmethod
    def pattern_placements(
        cls, length: int = 1, partial: bool = False
    ) -> "TileScopePack":
        name = "".join(
            [
                f"length_{length}_" if length > 1 else "",
                "partial_" if partial else "",
                "pattern" if length > 1 else "pattern_point",
                "_placements",
            ]
        )

        expansion_strats: List[CSSstrategy] = [
            strat.CellInsertionFactory(maxreqlen=length),
        ]
        if length > 1:
            expansion_strats.append(strat.RequirementCorroborationFactory())

        return TileScopePack(
            initial_strats=[
                strat.FactorFactory(unions=True, ignore_parent=False),
                strat.PointCorroborationFactory(),
            ],
            ver_strats=[
                strat.BasicVerificationStrategy(),
                strat.InsertionEncodingVerificationStrategy(),
                strat.OneByOneVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ],
            inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityFactory(),
            ],
            expansion_strats=[
                [strat.PatternPlacementFactory(partial=partial)],
                expansion_strats,
            ],
            name=name,
        )

    @classmethod
    def point_placements(
        cls, length: int = 1, partial: bool = False
    ) -> "TileScopePack":
        name = "".join(
            [
                f"length_{length}_" if length > 1 else "",
                "partial_" if partial else "",
                "point_placements",
            ]
        )

        initial_strats: List[CSSstrategy] = [
            strat.FactorFactory(),
            strat.PointCorroborationFactory(),
        ]
        if length > 1:
            initial_strats.append(strat.RequirementCorroborationFactory())

        return TileScopePack(
            initial_strats=initial_strats,
            ver_strats=[
                strat.BasicVerificationStrategy(),
                strat.InsertionEncodingVerificationStrategy(),
                strat.OneByOneVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ],
            inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityFactory(),
            ],
            expansion_strats=[
                [
                    strat.CellInsertionFactory(maxreqlen=length),
                    strat.PatternPlacementFactory(partial=partial),
                ],
            ],
            name=name,
        )

    @classmethod
    def insertion_point_placements(cls, partial: bool = False) -> "TileScopePack":
        name = "insertion_"
        partial_str = "partial_" if partial else ""
        name += f"{partial_str}point_placements"
        return TileScopePack(
            initial_strats=[
                strat.FactorFactory(),
                strat.CellInsertionFactory(
                    maxreqlen=1, ignore_parent=True, one_cell_only=True
                ),
            ],
            ver_strats=[
                strat.BasicVerificationStrategy(),
                strat.InsertionEncodingVerificationStrategy(),
                strat.OneByOneVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ],
            inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityFactory(),
            ],
            expansion_strats=[[strat.PatternPlacementFactory(partial=partial)]],
            name=name,
        )

    @classmethod
    def regular_insertion_encoding(cls, direction: int) -> "TileScopePack":
        """This pack finds insertion encodings."""
        if direction not in DIRS:
            raise ValueError(f"Must be direction in {DIRS}.")
        place_row = direction in (DIR_NORTH, DIR_SOUTH)
        place_col = not place_row
        direction_str = {
            DIR_EAST: "left",
            DIR_WEST: "right",
            DIR_NORTH: "bottom",
            DIR_SOUTH: "top",
        }
        name = f"regular_insertion_encoding_{direction_str[direction]}"
        return TileScopePack(
            initial_strats=[
                strat.FactorFactory(),
                strat.CellInsertionFactory(ignore_parent=True, one_cell_only=True),
            ],
            ver_strats=[strat.BasicVerificationStrategy()],
            inferral_strats=[],
            expansion_strats=[
                [
                    strat.RowAndColumnPlacementFactory(
                        place_col=place_col, place_row=place_row, dirs=[direction]
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
        name = "".join(
            [
                "partial_" if partial else "",
                "row" if not col_only else "",
                "_and_" if both else "",
                "col" if not row_only else "",
                "_placements",
            ]
        )
        rowcol_strat = strat.RowAndColumnPlacementFactory(
            place_row=place_row, place_col=place_col, partial=partial
        )
        expansion_strats: List[List[CSSstrategy]] = [[rowcol_strat]]
        if partial:
            expansion_strats.append([strat.PatternPlacementFactory(point_only=True)])
        return TileScopePack(
            initial_strats=[
                strat.FactorFactory(),
                strat.PointCorroborationFactory(),
            ],
            ver_strats=[
                strat.BasicVerificationStrategy(),
                strat.InsertionEncodingVerificationStrategy(),
                strat.OneByOneVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ],
            inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityFactory(),
            ],
            expansion_strats=expansion_strats,
            name=name,
        )

    @classmethod
    def insertion_row_and_col_placements(
        cls, row_only: bool = False, col_only: bool = False, partial: bool = False
    ) -> "TileScopePack":
        pack = cls.row_and_col_placements(row_only, col_only, partial)
        pack.name = "insertion_" + pack.name
        pack = pack.add_initial(
            strat.CellInsertionFactory(
                maxreqlen=1, ignore_parent=True, one_cell_only=True
            )
        )
        return pack

    @classmethod
    def insertion_point_row_and_col_placements(
        cls, row_only: bool = False, col_only: bool = False, partial: bool = False
    ) -> "TileScopePack":
        pack = cls.insertion_row_and_col_placements(row_only, col_only, partial)
        if not partial:
            # if partial, then already added pattern placements
            pack.name = pack.name.replace("insertion", "insertion_point")
            pack.expansion_strats = pack.expansion_strats + (
                (strat.PatternPlacementFactory(partial=False),),
            )
        return pack

    @classmethod
    def only_root_placements(
        cls,
        length: int = 3,
        max_num_req: Optional[int] = 1,
        max_placement_rules_per_req: Optional[int] = None,
        partial: bool = False,
    ) -> "TileScopePack":
        partial_str = "partial_" if partial else ""
        if max_num_req is not None:
            name = (
                f"only_length_{length}_{max_num_req}_reqs_root_{partial_str}placements"
            )
        else:
            name = f"only_length_{length}_root_{partial_str}placements"
        placement_factory = strat.RequirementPlacementFactory(
            max_rules_per_req=max_placement_rules_per_req, partial=partial
        )
        return TileScopePack(
            initial_strats=[
                strat.RootInsertionFactory(maxreqlen=length, max_num_req=max_num_req),
                strat.FactorFactory(unions=True, ignore_parent=False, workable=False),
                strat.PointCorroborationFactory(),
            ],
            ver_strats=[
                strat.BasicVerificationStrategy(),
                strat.InsertionEncodingVerificationStrategy(),
                strat.OneByOneVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ],
            inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityFactory(),
            ],
            expansion_strats=[[placement_factory]],
            name=name,
        )

    @classmethod
    def requirement_placements(
        cls, length: int = 2, partial: bool = False
    ) -> "TileScopePack":
        name = "".join(
            [
                f"length_{length}_" if length != 2 else "",
                "partial_" if partial else "",
                "requirement_placements",
            ]
        )

        initial_strats: List[CSSstrategy] = [
            strat.FactorFactory(),
            strat.PointCorroborationFactory(),
        ]
        if length > 1:
            initial_strats.append(strat.RequirementCorroborationFactory())

        return TileScopePack(
            initial_strats=initial_strats,
            ver_strats=[
                strat.BasicVerificationStrategy(),
                strat.InsertionEncodingVerificationStrategy(),
                strat.OneByOneVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ],
            inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityFactory(),
            ],
            expansion_strats=[
                [
                    strat.RequirementInsertionFactory(maxreqlen=length),
                    strat.PatternPlacementFactory(partial=partial),
                ],
            ],
            name=name,
        )

    @classmethod
    def subobstruction_placements(cls, partial: bool = False) -> "TileScopePack":
        name = "partial_" if partial else ""
        name += "subobstruction_placements"
        return TileScopePack(
            initial_strats=[
                strat.FactorFactory(),
                strat.PointCorroborationFactory(),
                strat.RequirementCorroborationFactory(),
            ],
            ver_strats=[
                strat.BasicVerificationStrategy(),
                strat.InsertionEncodingVerificationStrategy(),
                strat.OneByOneVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ],
            inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityFactory(),
            ],
            expansion_strats=[
                [
                    strat.SubobstructionInsertionFactory(),
                    strat.PatternPlacementFactory(partial=partial),
                ],
            ],
            name=name,
        )

    @classmethod
    def basis_pattern_insertions(cls, partial: bool = False) -> "TileScopePack":
        name = "partial_" if partial else ""
        name += "subobstruction_placements"
        return TileScopePack(
            initial_strats=[
                strat.FactorFactory(),
                strat.PointCorroborationFactory(),
                strat.RequirementCorroborationFactory(),
            ],
            ver_strats=[
                strat.BasicVerificationStrategy(),
                strat.InsertionEncodingVerificationStrategy(),
                strat.OneByOneVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ],
            inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityFactory(),
            ],
            expansion_strats=[
                [
                    strat.BasisPatternInsertionFactory(),
                    strat.PatternPlacementFactory(partial=partial),
                ],
            ],
            name=name,
        )

    @classmethod
    def point_and_row_and_col_placements(
        cls,
        length: int = 1,
        row_only: bool = False,
        col_only: bool = False,
        partial: bool = False,
    ) -> "TileScopePack":
        if row_only and col_only:
            raise ValueError("Can't be row and col only.")
        place_row = not col_only
        place_col = not row_only
        both = place_col and place_row
        name = "".join(
            [
                f"length_{length}_" if length > 1 else "",
                "partial_" if partial else "",
                "point_and_",
                "row" if not col_only else "",
                "_and_" if both else "",
                "col" if not row_only else "",
                "_placements",
            ]
        )
        rowcol_strat = strat.RowAndColumnPlacementFactory(
            place_row=place_row, place_col=place_col, partial=partial
        )

        initial_strats: List[CSSstrategy] = [
            strat.FactorFactory(),
            strat.PointCorroborationFactory(),
        ]
        if length > 1:
            initial_strats.append(strat.RequirementCorroborationFactory())

        return TileScopePack(
            initial_strats=initial_strats,
            ver_strats=[
                strat.BasicVerificationStrategy(),
                strat.InsertionEncodingVerificationStrategy(),
                strat.OneByOneVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ],
            inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityFactory(),
            ],
            expansion_strats=[
                [
                    strat.CellInsertionFactory(maxreqlen=length),
                    strat.PatternPlacementFactory(partial=partial),
                    rowcol_strat,
                ],
            ],
            name=name,
        )

    @classmethod
    def requirement_and_row_and_col_placements(
        cls,
        length: int = 1,
        row_only: bool = False,
        col_only: bool = False,
        partial: bool = False,
    ) -> "TileScopePack":
        if row_only and col_only:
            raise ValueError("Can't be row and col only.")
        place_row = not col_only
        place_col = not row_only
        both = place_col and place_row
        name = "".join(
            [
                f"length_{length}_" if length > 1 else "",
                "partial_" if partial else "",
                "requirement_and_",
                "row" if not col_only else "",
                "_and_" if both else "",
                "col" if not row_only else "",
                "_placements",
            ]
        )
        rowcol_strat = strat.RowAndColumnPlacementFactory(
            place_row=place_row, place_col=place_col, partial=partial
        )

        initial_strats: List[CSSstrategy] = [
            strat.FactorFactory(),
            strat.PointCorroborationFactory(),
        ]
        if length > 1:
            initial_strats.append(strat.RequirementCorroborationFactory())

        return TileScopePack(
            initial_strats=initial_strats,
            ver_strats=[
                strat.BasicVerificationStrategy(),
                strat.InsertionEncodingVerificationStrategy(),
                strat.OneByOneVerificationStrategy(),
                strat.LocallyFactorableVerificationStrategy(),
            ],
            inferral_strats=[
                strat.RowColumnSeparationStrategy(),
                strat.ObstructionTransitivityFactory(),
            ],
            expansion_strats=[
                [
                    strat.RequirementInsertionFactory(maxreqlen=length),
                    strat.PatternPlacementFactory(partial=partial),
                    rowcol_strat,
                ],
            ],
            name=name,
        )

    @classmethod
    def cell_insertions(cls, length: int):
        return TileScopePack(
            initial_strats=[],
            ver_strats=[
                strat.BasicVerificationStrategy(),
                strat.InsertionEncodingVerificationStrategy(),
                strat.OneByOneVerificationStrategy(),
            ],
            inferral_strats=[],
            expansion_strats=[[strat.CellInsertionFactory(maxreqlen=length)]],
            name=f"length_{length}_cell_insertions",
        )
