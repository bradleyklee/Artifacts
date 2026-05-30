#!/usr/bin/env python3
"""SAT search for periodic-pruned equilateral triangle rule systems.

Rule space
----------
Mandatory: AB=DE.
Forbidden: every other join involving AB.
Optional: the 15 unordered joins with repetition on {BC, CA, DE, EF, FD}.

Search filters
--------------
1. Periodic filtering: directly SAT-solve finite periodic WxH parallelogram
   tori.  A satisfying torus uses an optional-rule certificate C; every mask
   containing C permits that same periodic tiling and is pruned.
2. Completion filtering: SAT-solve successively larger finite patches obtained
   by closing around the central triangle.  A survivor must fill the requested
   maximum completion depth.

The SAT encoding is direct in triangle geometry.  It does not use reconstructed
local-model certificates or adjacency-matrix hashing.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from itertools import combinations_with_replacement, permutations
from typing import Iterable

try:
    from pysat.solvers import Solver
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "python-sat is required: python3 -m pip install python-sat"
    ) from exc

EDGE_NAMES = ("AB", "BC", "CA", "DE", "EF", "FD")
AB, BC, CA, DE, EF, FD = range(6)
VARIABLE_EDGES = (BC, CA, DE, EF, FD)
VARIABLE_PAIRS = tuple(combinations_with_replacement(VARIABLE_EDGES, 2))
PAIR_TO_BIT = {pair: bit for bit, pair in enumerate(VARIABLE_PAIRS)}
FULL_MASK = (1 << len(VARIABLE_PAIRS)) - 1
MANDATORY = tuple(sorted((AB, DE)))
STATES = tuple(dict.fromkeys(tuple(p) for base in ((AB, BC, CA), (DE, EF, FD)) for p in permutations(base)))
CENTRAL_STATE_IDS = tuple(STATES.index(s) for s in ((AB, BC, CA), (AB, CA, BC), (DE, EF, FD), (DE, FD, EF)))
Cell = tuple[str, int, int]
Contact = tuple[int, int, int, int]


@dataclass(frozen=True)
class Geometry:
    cells: tuple[Cell, ...]
    contacts: tuple[Contact, ...]
    center: int | None = None


@dataclass(frozen=True)
class Witness:
    states: tuple[int, ...]
    used_mask: int


def vertices(cell: Cell) -> tuple[tuple[int, int], ...]:
    o, i, j = cell
    if o == "U":
        return ((i, j), (i + 1, j), (i, j + 1))
    return ((i + 1, j), (i + 1, j + 1), (i, j + 1))


def sides(cell: Cell) -> tuple[frozenset[tuple[int, int]], ...]:
    vs = vertices(cell)
    return tuple(frozenset((vs[k], vs[(k + 1) % 3])) for k in range(3))


def contacts_for(cells: tuple[Cell, ...]) -> tuple[Contact, ...]:
    out: list[Contact] = []
    for a, ca in enumerate(cells):
        sa = sides(ca)
        for b in range(a + 1, len(cells)):
            sb = sides(cells[b])
            for ia in range(3):
                for ib in range(3):
                    if sa[ia] == sb[ib]:
                        out.append((a, ia, b, ib))
    return tuple(out)


def completion_patch(depth: int) -> Geometry:
    active = set(vertices(("U", 0, 0)))
    included: set[Cell] = set()
    for _ in range(depth):
        next_cells = set(included)
        lim = 2 * depth + 3
        for o in ("U", "D"):
            for i in range(-lim, lim + 1):
                for j in range(-lim, lim + 1):
                    cell = (o, i, j)
                    if active.intersection(vertices(cell)):
                        next_cells.add(cell)
        included = next_cells
        active = {v for cell in included for v in vertices(cell)}
    cells = tuple(sorted(included))
    center = cells.index(("U", 0, 0))
    return Geometry(cells, contacts_for(cells), center)


def torus(width: int, height: int) -> Geometry:
    cells = tuple((o, i, j) for j in range(height) for i in range(width) for o in ("U", "D"))
    index = {cell: n for n, cell in enumerate(cells)}
    contacts: list[Contact] = []
    for j in range(height):
        for i in range(width):
            u = index[("U", i, j)]
            contacts.append((u, 0, index[("D", i, (j - 1) % height)], 1))
            contacts.append((u, 1, index[("D", i, j)], 2))
            contacts.append((u, 2, index[("D", (i - 1) % width, j)], 0))
    return Geometry(cells, tuple(contacts), None)


def join_allowed(mask: int, x: int, y: int) -> bool:
    pair = tuple(sorted((x, y)))
    if pair == MANDATORY:
        return True
    if AB in pair:
        return False
    return bool(mask & (1 << PAIR_TO_BIT[pair]))


def optional_join_bit(x: int, y: int) -> int:
    pair = tuple(sorted((x, y)))
    if pair == MANDATORY:
        return 0
    assert AB not in pair
    return 1 << PAIR_TO_BIT[pair]


def rule_var(bit: int) -> int:
    return bit + 1


def tile_var(cell: int, state: int) -> int:
    return 16 + cell * len(STATES) + state


class EncodedGeometry:
    """One reusable SAT instance; a rule mask is supplied by assumptions."""
    def __init__(self, geometry: Geometry, solver_name: str):
        self.geometry = geometry
        self.solver = Solver(name=solver_name)
        for cell in range(len(geometry.cells)):
            variables = [tile_var(cell, state) for state in range(len(STATES))]
            self.solver.add_clause(variables)
            for a in range(len(variables)):
                for b in range(a + 1, len(variables)):
                    self.solver.add_clause([-variables[a], -variables[b]])
        if geometry.center is not None:
            self.solver.add_clause([tile_var(geometry.center, state) for state in CENTRAL_STATE_IDS])
        # Join permissions are SAT variables.  A mask sets them by assumptions.
        for a, sa, b, sb in geometry.contacts:
            for ta, state_a in enumerate(STATES):
                for tb, state_b in enumerate(STATES):
                    pair = tuple(sorted((state_a[sa], state_b[sb])))
                    prefix = [-tile_var(a, ta), -tile_var(b, tb)]
                    if pair == MANDATORY:
                        continue
                    if AB in pair:
                        self.solver.add_clause(prefix)
                    else:
                        self.solver.add_clause(prefix + [rule_var(PAIR_TO_BIT[pair])])

    def close(self) -> None:
        self.solver.delete()

    def solve(self, mask: int, want_witness: bool = False) -> Witness | None:
        assumptions = [rule_var(bit) if mask & (1 << bit) else -rule_var(bit) for bit in range(15)]
        if not self.solver.solve(assumptions=assumptions):
            return None
        if not want_witness:
            return Witness((), 0)
        model = set(lit for lit in self.solver.get_model() if lit > 0)
        chosen: list[int] = []
        for cell in range(len(self.geometry.cells)):
            selected = [state for state in range(len(STATES)) if tile_var(cell, state) in model]
            assert len(selected) == 1
            chosen.append(selected[0])
        used = 0
        for a, sa, b, sb in self.geometry.contacts:
            left = STATES[chosen[a]][sa]
            right = STATES[chosen[b]][sb]
            assert join_allowed(mask, left, right)
            used |= optional_join_bit(left, right)
        assert used & ~mask == 0
        return Witness(tuple(chosen), used)

def parse_tori(text: str) -> tuple[tuple[int, int], ...]:
    dims: list[tuple[int, int]] = []
    for raw in text.split(","):
        w, h = (int(piece) for piece in raw.lower().split("x"))
        if w < 1 or h < 1:
            raise ValueError("torus dimensions must be positive")
        if (w, h) not in dims:
            dims.append((w, h))
    return tuple(dims)


def tori_through_area(area: int) -> tuple[tuple[int, int], ...]:
    # Ordered periods are kept: no lattice reflection quotient is assumed.
    dims = [(w, h) for product in range(1, area + 1) for w in range(1, product + 1)
            if product % w == 0 for h in (product // w,)]
    return tuple(dims)


def mask_rules(mask: int) -> str:
    rules = [f"{EDGE_NAMES[x]}={EDGE_NAMES[y]}" for bit, (x, y) in enumerate(VARIABLE_PAIRS) if mask & (1 << bit)]
    return ",".join(rules) if rules else "-"


def covers(mask: int, certificate: int) -> bool:
    return mask & certificate == certificate


def periodic_certificates(dims: tuple[tuple[int, int], ...], solver_name: str) -> tuple[list[tuple[int, int, int]], int]:
    certs: list[tuple[int, int, int]] = []  # (mask, width, height)
    sat_calls = 0
    encodings = [(width, height, EncodedGeometry(torus(width, height), solver_name)) for width, height in dims]
    try:
        masks = sorted(range(FULL_MASK + 1), key=lambda m: (m.bit_count(), m))
        for mask in masks:
            if any(covers(mask, cert) for cert, _, _ in certs):
                continue
            for width, height, encoding in encodings:
                sat_calls += 1
                witness = encoding.solve(mask, want_witness=True)
                if witness is None:
                    continue
                certificate = witness.used_mask
                # The concrete periodic witness verifies the extracted permission certificate.
                geometry = encoding.geometry
                for a, sa, b, sb in geometry.contacts:
                    assert join_allowed(certificate, STATES[witness.states[a]][sa], STATES[witness.states[b]][sb])
                if not any(covers(certificate, old) for old, _, _ in certs):
                    certs.append((certificate, width, height))
                break
    finally:
        for _, _, encoding in encodings:
            encoding.close()
    return certs, sat_calls

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    period = parser.add_mutually_exclusive_group(required=True)
    period.add_argument("--periodic-depth", type=int, metavar="A", help="test every ordered WxH torus with W*H <= A; depth 6 includes 3x2")
    period.add_argument("--tori", help="exact comma-separated tori, for example 1x1,1x2,2x1,2x2,2x3,3x2")
    parser.add_argument("--completion-depth", type=int, required=True, metavar="D", help="require a direct finite-patch completion through depth D")
    parser.add_argument("--solver", default="cadical195", help="python-sat backend; default cadical195")
    parser.add_argument("--summary", action="store_true", help="write filter counts to stderr")
    parser.add_argument("--certificates", action="store_true", help="write minimal periodic certificates to stderr")
    args = parser.parse_args()
    if args.completion_depth < 1:
        parser.error("--completion-depth must be positive")
    if args.periodic_depth is not None:
        if args.periodic_depth < 1:
            parser.error("--periodic-depth must be positive")
        dims = tori_through_area(args.periodic_depth)
    else:
        dims = parse_tori(args.tori)

    certs, torus_calls = periodic_certificates(dims, args.solver)
    periodic_masks = {mask for mask in range(FULL_MASK + 1) if any(covers(mask, cert) for cert, _, _ in certs)}
    alive = [mask for mask in range(FULL_MASK + 1) if mask not in periodic_masks]
    stages: list[tuple[int, int, int]] = []
    for depth in range(1, args.completion_depth + 1):
        patch = completion_patch(depth)
        before = len(alive)
        encoding = EncodedGeometry(patch, args.solver)
        try:
            alive = [mask for mask in alive if encoding.solve(mask) is not None]
        finally:
            encoding.close()
        stages.append((depth, before, len(alive)))

    # stdout intentionally contains only successful surviving masks.
    for mask in alive:
        print(f"0x{mask:04x}\tbits={mask.bit_count()}\t{mask_rules(mask)}")

    if args.summary:
        print("periodic_tori=" + ",".join(f"{w}x{h}" for w, h in dims), file=sys.stderr)
        print(f"minimal_periodic_certificates={len(certs)}", file=sys.stderr)
        print(f"periodically_pruned={len(periodic_masks)}", file=sys.stderr)
        print(f"after_periodic_filter={FULL_MASK + 1 - len(periodic_masks)}", file=sys.stderr)
        for depth, before, after in stages:
            print(f"completion_depth={depth} tested={before} live={after} eliminated={before - after}", file=sys.stderr)
        print(f"good_results={len(alive)}", file=sys.stderr)
        print(f"torus_sat_calls={torus_calls}", file=sys.stderr)
    if args.certificates:
        for cert, width, height in sorted(certs, key=lambda x: (x[0].bit_count(), x[0])):
            print(f"certificate=0x{cert:04x} bits={cert.bit_count()} torus={width}x{height} {mask_rules(cert)}", file=sys.stderr)


if __name__ == "__main__":
    main()
