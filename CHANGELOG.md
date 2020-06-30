# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
