from itertools import chain

from tilings.algorithms import ComponentFusion, Fusion, RequirementPlacement


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


def all_placements(tiling, **kwargs):
    req_placements = (RequirementPlacement(tiling),
                      RequirementPlacement(tiling, own_row=False),
                      RequirementPlacement(tiling, own_col=False))
    for req_placement in req_placements:
        yield from req_placement.all_point_placement_rules()
        yield from req_placement.all_requirement_placement_rules()
        yield from req_placement.all_col_placement_rules()
        yield from req_placement.all_row_placement_rules()


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


# -------------------------------------
#   Fusion strategies                 |
# -------------------------------------
def general_fusion_iterator(tiling, fusion_class):
    """
    Generator over rules found by fusing rows or columns of `tiling` using
    the fusion defined by `fusion_class`.
    """
    assert issubclass(fusion_class, Fusion)
    ncol = tiling.dimensions[0]
    nrow = tiling.dimensions[1]
    possible_fusion = chain(
        (fusion_class(tiling, row_idx=r) for r in range(nrow-1)),
        (fusion_class(tiling, col_idx=c) for c in range(ncol-1))
    )
    return (fusion.rule() for fusion in possible_fusion if fusion.fusable())


def fusion(tiling, **kwargs):
    """Generator over rules found by fusing rows or columns of `tiling`."""
    return general_fusion_iterator(tiling, fusion_class=Fusion)


def component_fusion(tiling, **kwargs):
    """
    Yield rules found by fusing rows and columns of a tiling, where the
    unfused tiling obtained by drawing a line through certain heights/indices
    of the row/column.
    """
    if tiling.requirements:
        return
    yield from general_fusion_iterator(tiling, ComponentFusion)
