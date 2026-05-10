#!/usr/bin/env python3
"""
example.py

Generate dihedral_4_4_words.dat for the n=4,k=4 worked example.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import collections


N = 4
K = 4
WORDS = [tuple(w) for w in product(range(1, K + 1), repeat=N)]
GROUP = [("rot", a) for a in range(N)] + [("ref", a) for a in range(N)]


def text(w: tuple[int, ...]) -> str:
    return "".join(map(str, w))


def rotate(w: tuple[int, ...], a: int = 1) -> tuple[int, ...]:
    a %= len(w)
    return w[a:] + w[:a]


def reverse(w: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(reversed(w))


def cyclic_orbit(w: tuple[int, ...]) -> set[tuple[int, ...]]:
    return {rotate(w, a) for a in range(N)}


def dihedral_orbit(w: tuple[int, ...]) -> set[tuple[int, ...]]:
    return cyclic_orbit(w) | {rotate(reverse(w), a) for a in range(N)}


def necklace_canonical(w: tuple[int, ...]) -> tuple[int, ...]:
    return min(cyclic_orbit(w))


def bracelet_canonical(w: tuple[int, ...]) -> tuple[int, ...]:
    return min(dihedral_orbit(w))


def permute_index(kind: str, a: int, i: int) -> int:
    if kind == "rot":
        return (i + a) % N
    if kind == "ref":
        return (a - i) % N
    raise ValueError(kind)


def act(w: tuple[int, ...], kind: str, a: int) -> tuple[int, ...]:
    out = [None] * N
    for i in range(N):
        out[permute_index(kind, a, i)] = w[i]
    return tuple(out)


def character(rep: str, kind: str, a: int) -> int:
    if rep == "B1":
        return (-1) ** a
    if rep == "B2":
        return (-1) ** a if kind == "rot" else -((-1) ** a)
    raise ValueError(rep)


def projector_column(rep: str, seed: tuple[int, ...]) -> list[Fraction]:
    coeffs = collections.defaultdict(Fraction)
    for kind, a in GROUP:
        coeffs[act(seed, kind, a)] += Fraction(character(rep, kind, a), len(GROUP))
    return [coeffs[w] for w in WORDS]


def rank_fraction(rows: list[list[Fraction]]) -> int:
    if not rows:
        return 0
    A = [r[:] for r in rows]
    m = len(A)
    ncols = len(A[0])
    r = 0
    for c in range(ncols):
        pivot = None
        for i in range(r, m):
            if A[i][c] != 0:
                pivot = i
                break
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        pv = A[r][c]
        A[r] = [x / pv for x in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                fac = A[i][c]
                A[i] = [A[i][j] - fac * A[r][j] for j in range(ncols)]
        r += 1
        if r == m:
            break
    return r


def greedy_b_split(pool: list[tuple[int, ...]]) -> tuple[list[tuple[int, ...]], list[tuple[int, ...]]]:
    b1_rows = []
    b1 = []
    rank = 0
    for w in pool:
        col = projector_column("B1", w)
        if all(x == 0 for x in col):
            continue
        nrank = rank_fraction(b1_rows + [col])
        if nrank > rank:
            b1_rows.append(col)
            b1.append(w)
            rank = nrank
    assert rank == 45

    used = set(b1)
    b2_rows = []
    b2 = []
    rank = 0
    for w in pool:
        if w in used:
            continue
        col = projector_column("B2", w)
        if all(x == 0 for x in col):
            continue
        nrank = rank_fraction(b2_rows + [col])
        if nrank > rank:
            b2_rows.append(col)
            b2.append(w)
            rank = nrank
    assert rank == 21
    return sorted(b1), sorted(b2)


def format_list(label: str, items: list[tuple[int, ...]], per_line: int = 12) -> str:
    words = [text(w) for w in items]
    lines = [f"{label}:"]
    for i in range(0, len(words), per_line):
        chunk = words[i:i + per_line]
        comma = "," if i + per_line < len(words) else ""
        lines.append("    " + ", ".join(f"{w:>4}" for w in chunk) + comma)
    return "\n".join(lines)


def main() -> None:
    a1 = sorted({bracelet_canonical(w) for w in WORDS})
    a1_set = set(a1)
    a2 = sorted({necklace_canonical(reverse(w)) for w in a1
                 if necklace_canonical(reverse(w)) != necklace_canonical(w)})

    # Chosen convention: right-rotation B-pool, then B1-first greedy projector split.
    b_pool = sorted(({rotate(w, -1) for w in a1} - a1_set) |
                    {rotate(w, -1) for w in a2})
    b1, b2 = greedy_b_split(b_pool)

    claimed = set(a1) | set(a2) | set(b1) | set(b2)
    e = sorted(set(WORDS) - claimed)

    assert len(a1) == 55
    assert len(a2) == 15
    assert len(b1) == 45
    assert len(b2) == 21
    assert len(e) == 120
    assert len(claimed | set(e)) == 256

    lines = [
        "# dihedral_4_4_words.dat",
        "# n=4, k=4",
        "# Convention: right-rotation B-pool; B1-first greedy projector split.",
        "# Counts: A1=55, A2=15, B1=45, B2=21, E=120.",
        "",
        format_list("A1", a1),
        "",
        format_list("A2", a2),
        "",
        format_list("B1", b1),
        "",
        format_list("B2", b2),
        "",
        format_list("E", e),
        "",
    ]

    with open("dihedral_4_4_words.dat", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
