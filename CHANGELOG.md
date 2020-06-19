# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
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
