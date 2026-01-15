from collections import defaultdict, deque
from itertools import chain, product
from typing import (
    TYPE_CHECKING,
    Callable,
    DefaultDict,
    Deque,
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


class Sliding:
    def __init__(self, tiling: "Tiling") -> None:
        self.tiling = tiling
        self.col_info: COL_INFO = Sliding._get_col_info(self.tiling)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.tiling == other.tiling

    def slidable_pairs(self) -> Iterable[Tuple[int, int]]:
        """Yield the column pairs possible to slide."""
        for av_12, av_123 in product(*self._fast_filter()):
            if self._slide_check_for_pair(av_12, av_123):
                yield av_12, av_123

    def slide_column(self, av_12: int, av_123: int) -> "Tiling":
        """Slide the columns av_12 and av_123 and return the resulting tiling. This
        assumes all checks have been performed and we are allowed to slide these
        columns.
        """
        n = len(next(iter(self.col_info[av_123][0])))
        to_change = set(
            chain(
                self.col_info[av_12][0],
                self.col_info[av_12][1],
                self.col_info[av_123][0],
                self.col_info[av_123][1],
                self.col_info[av_123][2],
                self.col_info[av_123][n - 1],
            )
        )
        obstructions = {obs for obs in self.tiling.obstructions if obs not in to_change}
        obstructions.update(self._slide_obstructions(n, to_change, av_12, av_123))

        return type(self.tiling)(
            requirements=self.tiling.requirements,
            obstructions=obstructions,
            assumptions=self._swap_assumptions(av_12, av_123),
            derive_empty=False,
            remove_empty_rows_and_cols=False,
            simplify=False,
        )

    @staticmethod
    def slide_assumption(
        assumption: TrackingAssumption,
        c1: int,
        c2: int,
        g_map: Optional[Callable[[GriddedPerm], GriddedPerm]] = None,
        g_inv: Optional[Callable[[GriddedPerm], GriddedPerm]] = None,
    ):
        """Swap (c1,c2) if column is either one."""
        if g_map is None or g_inv is None:
            return TrackingAssumption(
                (
                    GriddedPerm(
                        gp.patt,
                        (
                            (
                                (
                                    c2
                                    if gp.pos[0][0] == c1
                                    else (c1 if gp.pos[0][0] == c2 else gp.pos[0][0])
                                ),
                                0,
                            ),
                        ),
                    )
                    for gp in assumption.gps
                )
            )
        return TrackingAssumption(
            (
                g_inv(
                    GriddedPerm(
                        gp.patt,
                        (
                            (
                                (
                                    c2
                                    if gp.pos[0][0] == c1
                                    else (c1 if gp.pos[0][0] == c2 else gp.pos[0][0])
                                ),
                                0,
                            ),
                        ),
                    )
                )
                for gp in (g_map(_gp) for _gp in assumption.gps)
            )
        )

    @staticmethod
    def slide_gp(gp: GriddedPerm, c1: int = 0, c2: int = -1) -> "GriddedPerm":
        """Sliding for gridded permutations within a boundary of 1xn."""
        if c2 < 0:
            c2 = c1 + 1
        perms, cols = Sliding._gp_slide_split(gp, c1, c2)

        if not perms[3]:
            return type(gp)(
                chain(perms[0], perms[2], perms[1], perms[5]),
                (
                    (x, 0)
                    for x in chain(cols[0], cols[1], (c2,) * len(perms[1]), cols[2])
                ),
            )

        while perms[1]:
            val = perms[1].pop()
            r_val, idx = min(
                ((r_val, i) for i, r_val in enumerate(perms[3]) if r_val > val),
                default=(-1, -1),
            )
            if idx != -1:
                perms[3][idx] = val
                perms[4].appendleft(r_val)
            else:
                perms[3].appendleft(val)
                perms[4].appendleft(perms[3].pop())

        return type(gp)(
            chain(perms[0], perms[3], perms[2], perms[4], perms[5]),
            (
                (x, 0)
                for x in chain(
                    cols[0],
                    (c1,) * len(perms[3]),
                    cols[1],
                    (c2,) * len(perms[4]),
                    cols[2],
                )
            ),
        )

    @staticmethod
    def slide_gp_inverse(gp: GriddedPerm, c1: int = 0, c2: int = -1) -> "GriddedPerm":
        """Inverse of sliding for gridded permutations within a boundary of 1xn."""
        if c2 < 0:
            c2 = c1 + 1
        perms, cols = Sliding._gp_slide_split(gp, c1, c2)

        if not perms[1]:
            return type(gp)(
                chain(perms[0], perms[3], perms[2], perms[5]),
                (
                    (x, 0)
                    for x in chain(cols[0], (c1,) * len(perms[3]), cols[1], cols[2])
                ),
            )

        while perms[3]:
            val = perms[3].popleft()
            l_val, idx = max(
                ((l_val, i) for i, l_val in enumerate(perms[1]) if l_val < val),
                default=(-1, -1),
            )
            if idx != -1:
                perms[1][idx] = val
                perms[4].append(l_val)
            else:
                perms[1].append(val)
                perms[4].append(perms[1].popleft())

        return type(gp)(
            chain(perms[0], perms[4], perms[2], perms[1], perms[5]),
            (
                (x, 0)
                for x in chain(
                    cols[0],
                    (c1,) * len(perms[4]),
                    cols[1],
                    (c2,) * len(perms[1]),
                    cols[2],
                )
            ),
        )

    @staticmethod
    def _get_col_info(tiling: "Tiling") -> COL_INFO:
        """Gather data about columns needed for sliding."""
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

    def _fast_filter(self) -> Tuple[Set[int], Set[int]]:
        """Fast initial filter to eliminate as much as possible quickly."""
        c, r = self.tiling.dimensions
        if r > 1:
            return set(), set()
        av_12: Set[int] = set()
        av_123: Set[int] = set()
        self._fast_check_all_columns(c, av_12, av_123)
        reqs = {x for req in chain(*self.tiling.requirements) for x, _ in req.pos}
        return av_12 - reqs, av_123 - reqs

    def _fast_check_all_columns(self, c: int, av_12: Set[int], av_123: Set[int]):
        for col in range(c):
            col_perms = self.col_info[col]
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
            # If the 2nd most number of pnts from a gp within the column is more than 2
            # Note that all local patterns are stored at col_perms[0].
            if cnts[-2] > 2:
                continue
            n = len(loc_patt)
            if n == 2:
                # If the size of the local obstruction is 2 and the largest number of
                # points from a crossing obstruction is less than 3, then this can
                # possibly be a av_12 column in sliding but not a av_123.
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

    def _slide_check_for_pair(self, av_12: int, av_123: int):
        """Check if slide can be applied to columns av_12 and av_123. We except them
        to have been passed to the fast filter before checking here.
        """
        check_list = self._check_av12_av123_connection(av_12, av_123)
        if check_list is None:
            return False

        for gp, indices in self.col_info[av_123][1].items():
            check_list.remove(gp)
            idx = indices[0]
            if gp in self.col_info[av_12][1]:
                # If the gp is also in the av_12 column, then there should be a
                # similar gp with two points in av_123
                if not self._av123_two_points(gp, idx, (av_12, av_123), check_list):
                    return False
            else:
                # If the gp is not in av_12 column, than there should be a similar
                # gp but with one point in the av_12 column
                if not self._av12_one_point(gp, idx, av_12, check_list):
                    return False
        return len(check_list) == 0

    def _check_av12_av123_connection(
        self, av_12: int, av_123: int
    ) -> Optional[Set[GriddedPerm]]:
        """Check if there is a 123...n obstruction connecting the two columns and if so,
        generate the other obstructions that must be in place for them to be slidable.
        """
        n = len(next(iter(self.col_info[av_123][0])))
        pos = ((av_123, 0),) * (n - 1)
        pos = pos + ((av_12, 0),) if av_12 > av_123 else ((av_12, 0),) + pos
        conn = GriddedPerm(range(n), pos)
        if (
            conn not in self.col_info[av_12][1]
            or conn not in self.col_info[av_123][n - 1]
        ):
            return None
        check_list: Set[GriddedPerm] = set(
            chain(
                self.col_info[av_123][1],
                self.col_info[av_123][2],
                self.col_info[av_12][1],
            )
        )
        check_list.remove(conn)
        return check_list

    def _av123_two_points(
        self,
        gp: GriddedPerm,
        idx: int,
        av_12_av_123: Tuple[int, int],
        check_list: Set[GriddedPerm],
    ) -> bool:
        """Check if gp exists but with point that is in av_12 in av_123. Returns true if
        that is the case and removes it from the checklist. Otherwise false is returned.
        """
        idx2 = self.col_info[av_12_av_123[0]][1][gp][0]
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
        if expected_gp not in self.col_info[av_12_av_123[1]][2]:
            return False
        check_list.remove(expected_gp)
        return True

    def _av12_one_point(
        self, gp: GriddedPerm, idx: int, av_12: int, check_list: Set[GriddedPerm]
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
        if expected_gp not in self.col_info[av_12][1]:
            return False
        check_list.remove(expected_gp)
        return True

    def _swap_assumptions(self, c1: int, c2: int) -> Iterable[TrackingAssumption]:
        for assumption in self.tiling.assumptions:
            assert all(len(gp) == 1 for gp in assumption.gps)
            yield Sliding.slide_assumption(assumption, c1, c2)

    def _slide_obstructions(
        self, n: int, to_change: Set[GriddedPerm], av_12: int, av_123: int
    ) -> Iterable[GriddedPerm]:
        """Generate all obstructions in the new
        tiling thatbelong to av_12 or av_123.
        """
        # Local patterns swap places
        yield GriddedPerm(range(n), ((av_12, 0),) * n)
        yield GriddedPerm(range(2), ((av_123, 0), (av_123, 0)))
        for gp in chain(self.col_info[av_12][0], self.col_info[av_123][0]):
            to_change.remove(gp)

        while to_change:
            gp = to_change.pop()
            if gp in self.col_info[av_12][1] and gp in self.col_info[av_123][n - 1]:
                # The 12...n obstrudtion that connects av12 and av123
                yield GriddedPerm(
                    range(n),
                    (
                        ((av_12, 0),) * (n - 1) + ((av_123, 0),)
                        if av_12 < av_123
                        else ((av_123, 0),) + ((av_12, 0),) * (n - 1)
                    ),
                )
            elif gp in self.col_info[av_123][2]:
                # The one with two points in av_123 are altered so that the two
                # occurrences in av_123 now happen in av_12
                indices: List[int] = self.col_info[av_123][2][gp]
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
                # The other ones remain
                # (one point each, one point av_12, one_point av_123)
                yield gp

    @staticmethod
    def _gp_slide_split(gp: GriddedPerm, c1: int, c2: int) -> Tuple[
        Tuple[Deque[int], Deque[int], Deque[int], Deque[int], Deque[int], Deque[int]],
        Tuple[List[int], List[int], List[int]],
    ]:
        assert c1 < c2 and min(c1, c2) >= 0 and all(y == 0 for _, (x, y) in gp)
        # Columns not affected
        cols: Tuple[List[int], List[int], List[int]] = ([], [], [])

        def _to_deque_index(x: int) -> int:
            if x < c1:
                cols[0].append(x)
                return 0
            if x == c1:
                return 1
            if x < c2:
                cols[1].append(x)
                return 2
            if x == c2:
                return 3
            cols[2].append(x)
            return 5

        perms: Tuple[
            Deque[int], Deque[int], Deque[int], Deque[int], Deque[int], Deque[int]
        ] = (
            deque([]),  # Columns before
            deque([]),  # Column c1
            deque([]),  # Columns between
            deque([]),  # Column c2
            deque([]),  # 'New' column
            deque([]),  # Columns after
        )

        for val, (x, _) in gp:
            perms[_to_deque_index(x)].append(val)

        return perms, cols
