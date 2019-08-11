# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Remove factors from requirements if already implied by other requirement
list.
- Added tiling method `is_empty_cell` and `is_monotone_cell`
### Fixed
- Infinite recursion issue in get_genf.
- Close mongo when finished.

## [0.0.1] - 2019-06-02
### Added
- This changelog.
