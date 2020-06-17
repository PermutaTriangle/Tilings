import warnings

from tilings.griddedperm import GriddedPerm

warnings.warn(
    "Obstruction is deprecated, just use GriddedPerm", category=DeprecationWarning
)

Obstruction = GriddedPerm
