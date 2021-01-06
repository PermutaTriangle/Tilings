# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Rearrange assumption strategy

### Changed
- Updated to use comb_spec_searcher 3.0.0

## [2.5.0] - 2020-11-11
### Added
- Added sliding strategy
- 'GuidedSearcher' class which will search for specification with a specific set of 
  underlying tilings. Includes methods 'from_spec' and 'from_uri' which creates a 
  'GuidedSearcher' instance.
- Creates a new `LimitedAssumptionTileScope` that allows you to set a maximum number
    of assumptions allowable on any tiling

### Changed
- Updated comb_spec_searcher version for faster counting
- Added a point placement strategy to partial row and col placement packs.
- `TileScopePack.make_tracked` return a new pack with tracked fusion instead of
  only adding the `AddAssumptionFactory` to the pack
- `make_fusion` and `make_interleaving` make the pack name a little more descriptive
- Updated short obstruction verification to take a length argument

## [2.4.1] - 2020-10-28
### Added
- `to_tex` for gridded perms.
- `to_tikz` for gridded perms.
- `to_svg` for gridded perms.
- `to_gui` for tilings.
- Mappings for gridded perms: `column_reverse`, `row_complement`,
   `permute_columns`, `permute_rows` and `apply_perm_map_to_cell`.
- Mappings for tilings: `column_reverse`, `row_complement`,
   `permute_columns`, `permute_rows`, `apply_perm_map_to_cell`.
- `guess_from_gridded_perms` to guess tiling T from gridded perms in Grid(T).
- `enmerate_gp_up_to` counts gridded perms of length 0, 1, 2, ... up to a max length.
- Can sample and generate objects from fusion specifications.

### Fixed
- Anti-diagonal symmetry backward map was fixed.

## [2.3.1] - 2020-09-11
### Fixed
- Dependency issue when installing

## [2.3.0] - 2020-09-10
### Added
- introduced isolation levels to the fusion strategy
- added the `one_cell_only` option to `CellInsertionFactory`
- `remove_components_from_assumptions` method to `Tiling`
- `DetectComponentsStrategy` which removes cells from assumptions
   which are actual components. This replaces the need for the
   `SplittingStrategy` in component fusion packs.
- added equation generators to `FusionStrategy` for the case where one or both
   sides are positive
- added a `to_html_representation` method to `Tiling`
- `SubclassVerificationFactory` and the corresponding strategy
- `is_subclass` method to `Tiling`
- added `point_and_row_and_col_placements` strategy
- `ShortObstructionVerificationStrategy`
- using Github Actions for testing and deployment

### Changed
- insertion packs now use the `one_cell_only` option, and no longer use
  `RequirementCorroborationFactory`
- the `get_eq_symbol` and `get_op_symbol` are moved to `Strategy` rather than
  `Constructor`
- the `GriddedPermsOnTiling` algorithm was changed to build from minimal
  gridded perms in a breadth first manner. This is also include an option to
  limit the number of points placed on the minimal gridded perms.
- new default behavior of `RequirementInsertionFactory` is to only insert requirements
  on tilings that don't already have any
- converted the expansion strategies in several strategy packs to be a single set
- requirement corroboration is only enabled when requirements of length > 1 are placed
- A gridded permutation can now be built from any iterable of integer, not only
  from permutation.

### Fixed
- untracked constructors raise `NotImplementedError`
- forbid fusing a region containing a `TrackingAssumption` and a
  `ComponentAssumption`
- a tiling factors if a `ComponentAssumption` if the components of the region
  split into the factors
- only fuse non-empty regions to avoid creating unintentional rules a -> b
  where a and b are equivalent
- remove duplicate assumptions in the `AddAssumptionsStrategy`
- `Tiling.from_dict` will make a `Tiling` with no assumptions if the
  `assumptions` key is not in the dictionary.
- a factor with interleaving strategy has `inferrable=True`
- a factor with interleaving strategy return a normal factor strategy when
  there's no interleaving going on.
- removed the length argument to the `insertion_point_placements` pack which
  was not implemented, and thus raising an error.
- Bug that occurred when factoring the empty tiling
- fixed that the `partial` flag was ignored in `point_placements`
- isolation levels were not being passed to component fusion
- expanding a symmetry of 132 with both length 2 requirements


## [2.2.0] - 2020-07-08
### Added
- add the `can_be_equivalent` methods to `AddAssumptionsStrategy`,
  `SplittingStrategy`, and `FusionStrategy`.
- added a `get_assumption` method to `Tiling`

### Changed
- the `Factor` algorithm will now factor `TrackingAssumptions` if they span
  multiple factors of the tiling. This means that the `SplittingStrategy` is
  removed from the tracked `StrategyPack`. It does not factor
  `ComponentAssumptions`, so using this strategy still requires the
  `SplittingStrategy`.

### Fixed
- remove empty assumptions when creating extra parameters in `FusionStrategy`
- the method `Tiling.get_genf` returns the Catalan generating function for Av(123).
- correct the generating function equations for `SplittingStrategy`

### Removed
- Removed optional arguments from the `from_bytes` method on `Tiling`

## [2.1.0] - 2020-06-29
### Added
- add a new `AddAssumptionStrategy` which adds an assumption to a tiling.
  In practice, when expanding a class, we actually remove an assumption to
  determine which rules to add.
- the `get_equations` method is now implemented for the strategies
  `AddAssumptionStrategy`, `SplittingStrategy`, and `FusionStrategy`.
- the `extra_paramters` method was implemented for symmetry strategies,
  allowing these to be used when enumerating tracked trees.
- Add the `InsertionEncodingVerificationStrategy` which verifies n x 1 and
  1 x n tilings which have a regular topmost or bottommost insertion encoding.
- Added the `SumComponentAssumption` and `SkewComponentAssumption` giving the
  ability to track specifications using component fusion.
- add partial flag to `insertion_point_placements` and
  `insertion_row_and_col_placements`
- Allow fusing rows and columns which are positive on either or both sides.
- The tracking of interleaving factors is implemented, including the poly time
  algorithm. This includes the new strategy `AddInterleavingAssumptionFactory`
  which adds the assumptions required in order to enumerate when performing
  an interleaving factor strategy.
- The `TileScopePack` has a new method `make_interleaving` which by will change
  any factor strategy in the pack to allow interleaving. The default setting is
  for tracked, and so the assumption strategies are also added. This can be
  turned off with the flag `tracked=False`.
- The `possible_parameters` method on `Tiling` allowing for sanity checking
  specifications with multiple variables.
- `InsertionEncodingVerificationStrategy` was added to verification expansion
  packs.
- `forward_map_assumption` method on `Tiling`.

### Changed
- The definition of a local `TrackingAssumption` in `LocalEnumeration` now says
  it is local if every gp in it is local (before it was they all used the same
  single cell).
- the default in `LocalVerificationStrategy` is now `no_factors=False`.

### Fixed
- untracked fusion packs don't add assumption strategies
- the length parameter for `all_the_strategies` is passed correctly to the
  requirement insertion strategy.
- use fusion on positive `Av(123)` when expanding 1x1 verified classes
- fix bug that prevented applying all eight symmetries
- fix assumption mapping bug in `FusionStrategy`
- fix `__repr__` in `FusionStrategy`

## [2.0.0] - 2020-06-17
### Added
All the necessary strategies for combinatorial exploration.

### Changed
Refactoring and speed up of many algorithm most notably the is empty check.

### Removed
- Support for Python 3.5 and earlier

## [1.0.2] - 2019-03-30
### Changed
- Update dependency versions

## [1.0.1] - 2019-08-26
### Changed
- Update comb_spec_searcher to 0.2.1

## [1.0.0] - 2019-08-26
### Added
- Remove factors from requirements if already implied by other requirement
list.
- Added tiling method `is_empty_cell` and `is_monotone_cell`
### Changed
- The `cell_basis` method of the tilings has an 1 obstruction for empty cell.
  The basis of a cell that is outside of the tiling is no longer defined.
- The requirement list in `cell_basis` method now finds intersections of
  requirement lists
- New `add_list_requirement` method to `Tiling`.
### Fixed
- Infinite recursion issue in get_genf.
- Close mongo when finished.

## [0.0.1] - 2019-06-02
### Added
- This changelog.
