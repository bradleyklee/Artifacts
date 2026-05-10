#!/usr/bin/env python3
"""
implementation.py

Dihedral representation count tables for colorings of n bead positions by k
available colors.

Representations:
  A1   S -> +1, R -> +1   ordinary bracelets
  A2   S -> +1, R -> -1   chiral necklace pairs
  B1   S -> -1, R -> +1   even n only
  B2   S -> -1, R -> -1   even n only
  E:m  two-dimensional Fourier sector
"""

from __future__ import annotations

import argparse
from math import gcd


def divisors(n: int) -> list[int]:
    return [d for d in range(1, n + 1) if n % d == 0]


def mobius(n: int) -> int:
    if n == 1:
        return 1
    x = n
    p = 2
    factors = 0
    while p * p <= x:
        if x % p == 0:
            x //= p
            factors += 1
            if x % p == 0:
                return 0
            while x % p == 0:
                x //= p
        p += 1
    if x > 1:
        factors += 1
    return -1 if factors % 2 else 1


def ramanujan_sum(q: int, m: int) -> int:
    """Exact Ramanujan sum c_q(m)."""
    g = gcd(q, m)
    return sum(d * mobius(q // d) for d in divisors(g))


def rotation_cycles(n: int, a: int) -> int:
    return gcd(n, a)


def reflection_cycles(n: int, a: int) -> int:
    if n % 2:
        return (n + 1) // 2
    return n // 2 + 1 if a % 2 == 0 else n // 2


def valid_rep(n: int, rep: str) -> bool:
    rep = rep.upper()
    if rep in ("A1", "A2"):
        return n >= 1
    if rep in ("B1", "B2"):
        return n >= 2 and n % 2 == 0
    if rep.startswith("E:"):
        if n < 3:
            return False
        m = int(rep.split(":", 1)[1])
        if n % 2:
            return 1 <= m <= (n - 1) // 2
        return 1 <= m <= n // 2 - 1
    return False


def character(rep: str, kind: str, a: int) -> int:
    rep = rep.upper()
    if rep == "A1":
        return 1
    if rep == "A2":
        return 1 if kind == "rot" else -1
    if rep == "B1":
        return (-1) ** a
    if rep == "B2":
        return (-1) ** a if kind == "rot" else -((-1) ** a)
    raise ValueError(rep)


def multiplicity(n: int, k: int, rep: str) -> int | None:
    rep = rep.upper()
    if not valid_rep(n, rep):
        return None

    if rep.startswith("E:"):
        m = int(rep.split(":", 1)[1])
        total = sum(ramanujan_sum(q, m) * (k ** (n // q)) for q in divisors(n))
        if total % n != 0:
            raise ArithmeticError(f"non-integer E multiplicity: {total}/{n}")
        return total // n

    total = 0
    for a in range(n):
        total += character(rep, "rot", a) * (k ** rotation_cycles(n, a))
    for a in range(n):
        total += character(rep, "ref", a) * (k ** reflection_cycles(n, a))

    if total % (2 * n) != 0:
        raise ArithmeticError(f"non-integer multiplicity: {total}/{2*n}")
    return total // (2 * n)


def print_table(rep: str, max_n: int, max_k: int) -> None:
    rep = rep.upper()
    cells = []
    for n in range(1, max_n + 1):
        row = []
        for k in range(1, max_k + 1):
            v = multiplicity(n, k, rep)
            row.append("-" if v is None else str(v))
        cells.append(row)

    width = max(5, max(len(x) for row in cells for x in row) + 1)
    print(f"{rep} table; rows n, columns k")
    print()
    print("n\\k" + "".join(f"{k:>{width}}" for k in range(1, max_k + 1)))
    for n, row in enumerate(cells, start=1):
        print(f"{n:>3}" + "".join(f"{x:>{width}}" for x in row))


def print_decomposition(n: int, k: int) -> None:
    reps = ["A1", "A2"]
    if n % 2 == 0:
        reps += ["B1", "B2"]
    max_m = (n - 1) // 2 if n % 2 else n // 2 - 1
    reps += [f"E:{m}" for m in range(1, max_m + 1)]

    print(f"D_{n} decomposition for k={k}; total dimension {k ** n}")
    total = 0
    for rep in reps:
        mult = multiplicity(n, k, rep)
        dim = 2 if rep.startswith("E:") else 1
        contribution = mult * dim
        total += contribution
        print(f"{rep:>4}: multiplicity={mult:<10} dim={dim} contribution={contribution}")
    print(f"sum={total}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--table", default="A1", help="A1, A2, B1, B2, or E:m")
    parser.add_argument("--max-n", type=int, default=6)
    parser.add_argument("--max-k", type=int, default=6)
    parser.add_argument("--decompose", nargs=2, type=int, metavar=("N", "K"))
    args = parser.parse_args()

    if args.decompose:
        print_decomposition(args.decompose[0], args.decompose[1])
    else:
        print_table(args.table, args.max_n, args.max_k)


if __name__ == "__main__":
    main()
