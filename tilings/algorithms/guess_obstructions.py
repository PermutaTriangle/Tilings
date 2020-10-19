from collections import deque
from typing import Deque, Iterable, Set, Tuple

from tilings.griddedperm import GriddedPerm


def guess_obstructions(
    gps: Iterable[GriddedPerm], max_len: int = -1
) -> Set[GriddedPerm]:
    """Generate minimal obstructions avoided by the provided gridded perms,
    if possible. We check to a fixed length."""
    gps = set(gps)
    c, r, longest = _get_dimensions(gps)
    max_len = longest if max_len == -1 else min(max_len, longest)
    return _search(deque([GriddedPerm()]), gps, c, r, max_len)


def _search(
    frontier: Deque[GriddedPerm],
    gps: Set[GriddedPerm],
    c: int,
    r: int,
    max_len: int,
) -> Set[GriddedPerm]:
    obstructions: Set[GriddedPerm] = set()
    while frontier:
        curr = frontier.popleft()
        if len(curr) > max_len:
            break
        if all(gp.avoids(curr) for gp in gps):
            obstructions.add(curr)
        else:
            if curr not in gps:
                raise ValueError(f"Set should contain {repr(curr)}")
            for gp in curr.extend(c, r):
                frontier.append(gp)
    return obstructions


def _get_dimensions(gps: Iterable[GriddedPerm]) -> Tuple[int, int, int]:
    m_x, m_y, m_len = 0, 0, 0
    for gp in gps:
        m_len = max(m_len, len(gp))
        for _, (x, y) in gp:
            m_x = max(m_x, x)
            m_y = max(m_y, y)
    return m_x + 1, m_y + 1, m_len
