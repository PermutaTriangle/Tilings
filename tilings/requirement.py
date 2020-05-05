import warnings

from tilings.griddedperm import GriddedPerm

warnings.warn(
    "Requirement is deprecated, just use GriddedPerm", category=DeprecationWarning
)
Requirement = GriddedPerm
