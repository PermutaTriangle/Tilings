from tilings.algorithms import RequirementPlacement


# -------------------------------------
#   Placement                         |
# -------------------------------------
def requirement_placement(tiling, **kwargs):
    """
    Strategy that places a single forced point of a requirement.

    The requirement_placement strategy considers every requirement list of
    length exactly 1. For each of these requirements, it considers all the
    points of the requirement. The strategy then returns all tilings where the
    point has been placed with a force.
    """
    yield from RequirementPlacement(tiling).all_requirement_placement_rules()


def point_placement(tiling, **kwargs):
    """
    Strategy that place a single forced point of a point requirement.

    The point placement strategy considers all point requirements in their own
    requirement lists. For each of them, it returns a new tiling where the
    point has been placed with a force.
    """
    yield from RequirementPlacement(tiling).all_point_placement_rules()


# -------------------------------------
#   Partial Placement                 |
# -------------------------------------
def partial_requirement_placement(tiling, **kwargs):
    """
    Strategy that places a single forced point of a requirement onto it own row
    or onto its own column.

    The partial_requirement_placement strategy considers every requirement list
    of length exactly 1. For each of these requirements, it considers all the
    points of the requirement. The strategy then returns all tilings where the
    point has been partially placed with a force.
    """
    req_placements = (RequirementPlacement(tiling, own_row=False),
                      RequirementPlacement(tiling, own_col=False))
    for req_placement in req_placements:
        yield from req_placement.all_requirement_placement_rules()


def partial_point_placement(tiling, **kwargs):
    """
    Strategy that place a single forced point of a point requirement.

    The point placement strategy considers all point requirements in their own
    requirement lists. For each of them, it returns a new tiling where the
    point has been placed with a force.
    """
    yield from partial_requirement_placement(tiling, point_only=True)
