from collections import defaultdict
from itertools import chain, product
from typing import (
    TYPE_CHECKING,
    DefaultDict,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
)

from tilings import GriddedPerm, TrackingAssumption

if TYPE_CHECKING:
    # pylint: disable=cyclic-import
    from tilings import Tiling

COL_INFO = DefaultDict[int, DefaultDict[int, Dict[GriddedPerm, List[int]]]]


def slidable_pairs(tiling: "Tiling", col_info: COL_INFO) -> Iterable[Tuple[int, int]]:
    """Yield the column pairs possible to slide."""
    for av_12, av_123 in product(*_fast_filter(tiling, col_info)):
        if _slide_check_for_pair(tiling, av_12, av_123, col_info):
            yield av_12, av_123


def get_col_info(tiling: "Tiling") -> COL_INFO:
    """Gather data about columns needed for sliding."""
    # {
    #    column: {
    #        points_in_column_or_0_for_local: {
    #            gridded_perm: [indices in column],
    #        },
    #    },
    # }
    col_info: COL_INFO = defaultdict(lambda: defaultdict(dict))
    for obstruction in tiling.obstructions:
        lst, indices = obstruction.pos[0][0], []
        for i, (_, (x, _)) in enumerate(obstruction):
            if x == lst:
                indices.append(i)
            else:
                col_info[lst][len(indices)][obstruction] = indices
                indices = [i]
            lst = x
        cnt = 0 if len(indices) == len(obstruction) else len(indices)
        col_info[lst][cnt][obstruction] = indices
    return col_info


def slide_column(
    tiling: "Tiling", av_12: int, av_123: int, col_info: COL_INFO
) -> "Tiling":
    """Slide the columns av_12 and av_123 and return the resulting tiling. This
    assumes all checks have been performed and we are allowed to slide these columns.
    """
    n = len(next(iter(col_info[av_123][0])))
    to_change = set(
        chain(
            col_info[av_12][0],
            col_info[av_12][1],
            col_info[av_123][0],
            col_info[av_123][1],
            col_info[av_123][2],
            col_info[av_123][n - 1],
        )
    )
    obstructions = {obs for obs in tiling.obstructions if obs not in to_change}
    obstructions.update(_slide_obstructions(n, to_change, av_12, av_123, col_info))

    return type(tiling)(
        requirements=tiling.requirements,
        obstructions=obstructions,
        assumptions=_swap_assumptions(tiling.assumptions, av_12, av_123),
    )


# Private helpers


def _swap_assumptions(
    assumptions: Iterable[TrackingAssumption], c1: int, c2: int
) -> Iterable[TrackingAssumption]:
    for assumption in assumptions:
        assert all(len(gp) == 1 for gp in assumption.gps)
        yield TrackingAssumption(
            (
                GriddedPerm(
                    gp.patt,
                    (
                        (
                            c2
                            if gp.pos[0][0] == c1
                            else (c1 if gp.pos[0][0] == c2 else gp.pos[0][0]),
                            0,
                        ),
                    ),
                )
                for gp in assumption.gps
            )
        )


def _slide_obstructions(
    n: int, to_change: Set[GriddedPerm], av_12: int, av_123: int, col_info: COL_INFO
) -> Iterable[GriddedPerm]:
    """Generate all obstructions in the new tiling that belong to av_12 or av_123."""
    # Local patterns swap places
    yield GriddedPerm(range(n), ((av_12, 0),) * n)
    yield GriddedPerm(range(2), ((av_123, 0), (av_123, 0)))
    for gp in chain(col_info[av_12][0], col_info[av_123][0]):
        to_change.remove(gp)

    while to_change:
        gp = to_change.pop()
        if gp in col_info[av_12][1] and gp in col_info[av_123][n - 1]:
            # The 12...n obstrudtion that connects av12 and av123
            yield GriddedPerm(
                range(n),
                ((av_12, 0),) * (n - 1) + ((av_123, 0),)
                if av_12 < av_123
                else ((av_123, 0),) + ((av_12, 0),) * (n - 1),
            )
        elif gp in col_info[av_123][2]:
            # The one with two points in av_123 are altered so that the two occurrences
            # in av_123 now happen in av_12
            indices: List[int] = col_info[av_123][2][gp]
            vals = [gp.patt[idx] for idx in indices]
            pre: Tuple[List[int], List[Tuple[int, int]]] = ([], [])
            post: Tuple[List[int], List[Tuple[int, int]]] = ([], [])
            for v, (x, _) in gp:
                if x == av_123:
                    continue
                if x < av_12:
                    pre[0].append(v)
                    pre[1].append((x, 0))
                else:
                    post[0].append(v)
                    post[1].append((x, 0))
            yield GriddedPerm(
                chain(pre[0], vals, post[0]),
                chain(pre[1], ((av_12, 0), (av_12, 0)), post[1]),
            )
        else:
            # The other ones (one point each, one point av_12, one_point av_123) remain
            yield gp


def _av12_one_point(
    gp: GriddedPerm,
    idx: int,
    av_12: int,
    check_list: Set[GriddedPerm],
    col_info: COL_INFO,
) -> bool:
    """Check if gp exists but with point that is in av_123 in av_12. Returns true if
    that is the case and removes it from the checklist. Otherwise false is returned.
    """
    k = len(gp)
    val = gp.patt[idx]
    positions = list(gp.pos)
    pattern = list(gp.patt)
    positions[idx] = (av_12, 0)
    # Move val and coordinate to the correct place in a new gp.
    while True:
        if idx != 0 and positions[idx][0] < positions[idx - 1][0]:
            positions[idx] = positions[idx - 1]
            positions[idx - 1] = (av_12, 0)
            pattern[idx] = pattern[idx - 1]
            pattern[idx - 1] = val
            idx -= 1
        elif idx != k - 1 and positions[idx][0] > positions[idx + 1][0]:
            positions[idx] = positions[idx + 1]
            positions[idx + 1] = (av_12, 0)
            pattern[idx] = pattern[idx + 1]
            pattern[idx + 1] = val
            idx += 1
        else:
            break
    expected_gp = GriddedPerm(pattern, positions)
    if expected_gp not in col_info[av_12][1]:
        return False
    check_list.remove(expected_gp)
    return True


def _av123_two_points(
    gp: GriddedPerm,
    idx: int,
    av_12_av_123: Tuple[int, int],
    check_list: Set[GriddedPerm],
    col_info: COL_INFO,
) -> bool:
    """Check if gp exists but with point that is in av_12 in av_123. Returns true if
    that is the case and removes it from the checklist. Otherwise false is returned.
    """
    idx2 = col_info[av_12_av_123[0]][1][gp][0]
    a, b = sorted((idx, idx2))
    if gp.patt[a] + 1 != gp.patt[b]:
        return False
    positions = []
    pattern = []
    for i, (v, (x, _)) in enumerate(gp):
        if i == idx:
            positions.append((x, 0))
            positions.append((x, 0))
            pattern.append(gp.patt[a])
            pattern.append(gp.patt[b])
        elif i != idx2:
            positions.append((x, 0))
            pattern.append(v)
    expected_gp = GriddedPerm(pattern, positions)
    if expected_gp not in col_info[av_12_av_123[1]][2]:
        return False
    check_list.remove(expected_gp)
    return True


def _check_av12_av123_connection(
    tiling: "Tiling", av_12: int, av_123: int, col_info: COL_INFO
) -> Optional[Set[GriddedPerm]]:
    """Check if there is a 123...n obstruction connecting the two columns and if so,
    generate the other obstructions that must be in place for them to be slidable."""
    n = len(next(iter(col_info[av_123][0])))
    pos = ((av_123, 0),) * (n - 1)
    pos = pos + ((av_12, 0),) if av_12 > av_123 else ((av_12, 0),) + pos
    conn = GriddedPerm(range(n), pos)
    if conn not in col_info[av_12][1] or conn not in col_info[av_123][n - 1]:
        return None
    check_list: Set[GriddedPerm] = set(
        chain(col_info[av_123][1], col_info[av_123][2], col_info[av_12][1])
    )
    check_list.remove(conn)
    return check_list


def _slide_check_for_pair(
    tiling: "Tiling", av_12: int, av_123: int, col_info: COL_INFO
):
    """Check if slide can be applied to columns av_12 and av_123. We except them to have
    been passed to the fast filter before checking here.
    """
    check_list = _check_av12_av123_connection(tiling, av_12, av_123, col_info)
    if check_list is None:
        return False

    for gp, indices in col_info[av_123][1].items():
        check_list.remove(gp)
        idx = indices[0]
        if gp in col_info[av_12][1]:
            # If the gp is also in the av_12 column, then there should be a
            # similar gp with two points in av_123
            if not _av123_two_points(gp, idx, (av_12, av_123), check_list, col_info):
                return False
        else:
            # If the gp is not in av_12 column, than there should be a similar
            # gp but with one point in the av_12 column
            if not _av12_one_point(gp, idx, av_12, check_list, col_info):
                return False
    return len(check_list) == 0


def _fast_check_all_columns(
    c: int, av_12: Set[int], av_123: Set[int], col_info: COL_INFO
):
    for col in range(c):
        col_perms = col_info[col]
        # All gp with points in column have the same number of points in column
        if len(col_perms) < 2:
            continue
        local = col_perms[0]
        # If there are no or more than one local obstructions
        if len(local) != 1:
            continue
        loc_patt = next(iter(local))
        # If the local obstructions is Av(0)
        # If the local obstruction is not increasing
        # If there are more than 4 types of gps number of points within column
        if (
            len(loc_patt) == 1
            or not loc_patt.patt.is_increasing()
            or len(col_perms) > 4
        ):
            continue
        cnts = sorted(col_perms.keys())
        # If the second most number of points from a gp within the column is more than 2
        # Note that all local patterns are stored at col_perms[0].
        if cnts[-2] > 2:
            continue
        n = len(loc_patt)
        if n == 2:
            # If the size of the local obstruction is 2 and the largest number of
            # points from a crossing obstruction is less than 3, then this can possibly
            # be a av_12 column in sliding but not a av_123.
            if cnts[-1] < 3:
                av_12.add(col)
            continue
        if cnts[-1] == n - 1:
            largest_crossings = col_perms[cnts[-1]]
            # If the largest number of points from a crossing obsturction is n-1
            # this could potentially be a av_123 column. It is not if
            # * there are multipe crossing gp of length n-1 (exception if n=3)
            # * There are no increasing patterns of length n-1
            if (n != 3 and len(largest_crossings) > 1) or all(
                not p.patt.is_increasing() for p in largest_crossings
            ):
                continue
            av_123.add(col)


def _fast_filter(tiling: "Tiling", col_info: COL_INFO) -> Tuple[Set[int], Set[int]]:
    """Fast initial filter to eliminate as much as possible quickly."""
    c, r = tiling.dimensions
    if r > 1:
        return set(), set()
    av_12: Set[int] = set()
    av_123: Set[int] = set()
    _fast_check_all_columns(c, av_12, av_123, col_info)
    reqs = {x for req in chain(*tiling.requirements) for x, _ in req.pos}
    return av_12 - reqs, av_123 - reqs
