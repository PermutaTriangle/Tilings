# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- `fusion` method for tilings based on the `Fusion` class.
- `row_and_column_separation` method for tilings based on the
  `RowColSeperation` class.
- Adding `Factor`, `FactorWithInterleaving` and
  `FactorWithMonotoneInterleaving` algorithm. They are available by setting the
  right `interleaving` flag in the `find_factors` method of tilings
- Added `GriddedPermsOnTiling` algorithm, that is now used
  for `Tiling.gridded_perms`.
- Added `GriddedPerm.get_gridded_perm_at_indices` method.
- Added `MinimalGriddedPerms` algorithm used by the new
  `Tiling.minimal_gridded_perms` method.

### Changed
- Update permuta to 1.2.1
- Update comb_spec_searcher to 0.2.2

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
