#!/usr/bin/env python3
"""SAT search for periodic-pruned equilateral triangle rule systems.

Rule families
-------------
Both families require the mandatory join AB=DE.  Tiles are orientation-
preserving only: the three cyclic CCW rotations of ABC and of DEF.

anchored (default)
    Every other join involving AB is forbidden.  The optional unordered joins
    with repetition on {BC, CA, DE, EF, FD} give 15 variable bits.

unrestricted
    Every other unordered join with repetition on {AB, BC, CA, DE, EF, FD}
    is optional.  Removing only the mandatory AB=DE join leaves 20 bits.

Search filters
--------------
1. Periodic filtering: directly SAT-solve periodic W x H parallelogram tori.
   A satisfying torus uses an optional-rule certificate C; every mask
   containing C permits that same periodic tiling and is pruned.
2. Completion filtering: SAT-solve successively larger finite patches obtained
   by closing around a central triangle.  A survivor must fill the requested
   maximum completion depth.

The SAT encoding is direct in triangle geometry.  It does not use reconstructed
local-model certificates or adjacency-matrix hashing.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from itertools import combinations_with_replacement

try:
    from pysat.solvers import Solver
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "python-sat is required: python3 -m pip install python-sat"
    ) from exc

EDGE_NAMES = ("AB", "BC", "CA", "DE", "EF", "FD")
AB, BC, CA, DE, EF, FD = range(6)
ALL_EDGES = (AB, BC, CA, DE, EF, FD)
ANCHORED_EDGES = (BC, CA, DE, EF, FD)
MANDATORY = tuple(sorted((AB, DE)))
Cell = tuple[str, int, int]
Contact = tuple[int, int, int, int]


def cyclic_rotations(base: tuple[int, int, int]) -> tuple[tuple[int, int, int], ...]:
    return tuple(base[k:] + base[:k] for k in range(3))


# Reflections are intentionally excluded: all tile vertex orders are CCW.
STATES = cyclic_rotations((AB, BC, CA)) + cyclic_rotations((DE, EF, FD))
CENTRAL_STATE_IDS = tuple(STATES.index(s) for s in ((AB, BC, CA), (DE, EF, FD)))


@dataclass(frozen=True)
class RuleSpace:
    family: str
    variable_pairs: tuple[tuple[int, int], ...]

    @property
    def pair_to_bit(self) -> dict[tuple[int, int], int]:
        return {pair: bit for bit, pair in enumerate(self.variable_pairs)}

    @property
    def bits(self) -> int:
        return len(self.variable_pairs)

    @property
    def full_mask(self) -> int:
        return (1 << self.bits) - 1


def rule_space(family: str) -> RuleSpace:
    if family == "anchored":
        pairs = tuple(combinations_with_replacement(ANCHORED_EDGES, 2))
    elif family == "unrestricted":
        pairs = tuple(pair for pair in combinations_with_replacement(ALL_EDGES, 2)
                      if tuple(sorted(pair)) != MANDATORY)
    else:
        raise ValueError(f"unknown family {family!r}")
    return RuleSpace(family, pairs)


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


def join_allowed(space: RuleSpace, mask: int, x: int, y: int) -> bool:
    pair = tuple(sorted((x, y)))
    if pair == MANDATORY:
        return True
    bit = space.pair_to_bit.get(pair)
    return bit is not None and bool(mask & (1 << bit))


def optional_join_bit(space: RuleSpace, x: int, y: int) -> int:
    pair = tuple(sorted((x, y)))
    if pair == MANDATORY:
        return 0
    bit = space.pair_to_bit.get(pair)
    assert bit is not None, f"forbidden optional join in witness: {pair}"
    return 1 << bit


def rule_var(bit: int) -> int:
    return bit + 1


def tile_var(space: RuleSpace, cell: int, state: int) -> int:
    return space.bits + 1 + cell * len(STATES) + state


class EncodedGeometry:
    """One reusable SAT instance; a rule mask is supplied by assumptions."""
    def __init__(self, geometry: Geometry, solver_name: str, space: RuleSpace | None = None):
        self.geometry = geometry
        self.space = space or rule_space("anchored")
        pair_to_bit = self.space.pair_to_bit
        self.solver = Solver(name=solver_name)
        for cell in range(len(geometry.cells)):
            variables = [tile_var(self.space, cell, state) for state in range(len(STATES))]
            self.solver.add_clause(variables)
            for a in range(len(variables)):
                for b in range(a + 1, len(variables)):
                    self.solver.add_clause([-variables[a], -variables[b]])
        if geometry.center is not None:
            self.solver.add_clause([tile_var(self.space, geometry.center, state) for state in CENTRAL_STATE_IDS])
        for a, sa, b, sb in geometry.contacts:
            for ta, state_a in enumerate(STATES):
                for tb, state_b in enumerate(STATES):
                    pair = tuple(sorted((state_a[sa], state_b[sb])))
                    prefix = [-tile_var(self.space, a, ta), -tile_var(self.space, b, tb)]
                    if pair == MANDATORY:
                        continue
                    bit = pair_to_bit.get(pair)
                    if bit is None:
                        self.solver.add_clause(prefix)
                    else:
                        self.solver.add_clause(prefix + [rule_var(bit)])

    def close(self) -> None:
        self.solver.delete()

    def solve(self, mask: int, want_witness: bool = False) -> Witness | None:
        assumptions = [rule_var(bit) if mask & (1 << bit) else -rule_var(bit)
                       for bit in range(self.space.bits)]
        if not self.solver.solve(assumptions=assumptions):
            return None
        if not want_witness:
            return Witness((), 0)
        model = {lit for lit in self.solver.get_model() if lit > 0}
        chosen: list[int] = []
        for cell in range(len(self.geometry.cells)):
            selected = [state for state in range(len(STATES))
                        if tile_var(self.space, cell, state) in model]
            assert len(selected) == 1
            chosen.append(selected[0])
        used = 0
        for a, sa, b, sb in self.geometry.contacts:
            left = STATES[chosen[a]][sa]
            right = STATES[chosen[b]][sb]
            assert join_allowed(self.space, mask, left, right)
            used |= optional_join_bit(self.space, left, right)
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


def mask_rules(space: RuleSpace, mask: int) -> str:
    rules = [f"{EDGE_NAMES[x]}={EDGE_NAMES[y]}" for bit, (x, y) in enumerate(space.variable_pairs)
             if mask & (1 << bit)]
    return ",".join(rules) if rules else "-"


def covers(mask: int, certificate: int) -> bool:
    return mask & certificate == certificate


def periodic_certificates(dims: tuple[tuple[int, int], ...], solver_name: str,
                          space: RuleSpace | None = None) -> tuple[list[tuple[int, int, int]], int]:
    space = space or rule_space("anchored")
    certs: list[tuple[int, int, int]] = []  # (mask, width, height)
    sat_calls = 0
    encodings = [(width, height, EncodedGeometry(torus(width, height), solver_name, space))
                 for width, height in dims]
    try:
        masks = sorted(range(space.full_mask + 1), key=lambda m: (m.bit_count(), m))
        for mask in masks:
            if any(covers(mask, cert) for cert, _, _ in certs):
                continue
            for width, height, encoding in encodings:
                sat_calls += 1
                witness = encoding.solve(mask, want_witness=True)
                if witness is None:
                    continue
                certificate = witness.used_mask
                for a, sa, b, sb in encoding.geometry.contacts:
                    assert join_allowed(space, certificate, STATES[witness.states[a]][sa], STATES[witness.states[b]][sb])
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
    period.add_argument("--periodic-depth", type=int, metavar="A",
                        help="test every ordered WxH torus with W*H <= A")
    period.add_argument("--tori", help="exact comma-separated tori, for example 1x1,1x2,2x1")
    parser.add_argument("--family", choices=("anchored", "unrestricted"), default="anchored",
                        help="rule family; default anchored")
    parser.add_argument("--completion-depth", type=int, required=True, metavar="D",
                        help="require a direct finite-patch completion through depth D")
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
    space = rule_space(args.family)

    certs, torus_calls = periodic_certificates(dims, args.solver, space)
    periodic_masks = {mask for mask in range(space.full_mask + 1)
                      if any(covers(mask, cert) for cert, _, _ in certs)}
    alive = [mask for mask in range(space.full_mask + 1) if mask not in periodic_masks]
    stages: list[tuple[int, int, int]] = []
    for depth in range(1, args.completion_depth + 1):
        before = len(alive)
        encoding = EncodedGeometry(completion_patch(depth), args.solver, space)
        try:
            alive = [mask for mask in alive if encoding.solve(mask) is not None]
        finally:
            encoding.close()
        stages.append((depth, before, len(alive)))

    width = max(4, (space.bits + 3) // 4)
    for mask in alive:
        print(f"0x{mask:0{width}x}\tbits={mask.bit_count()}\t{mask_rules(space, mask)}")

    if args.summary:
        print(f"family={space.family}", file=sys.stderr)
        print(f"optional_rule_bits={space.bits}", file=sys.stderr)
        print(f"total_masks={space.full_mask + 1}", file=sys.stderr)
        print("periodic_tori=" + ",".join(f"{w}x{h}" for w, h in dims), file=sys.stderr)
        print(f"minimal_periodic_certificates={len(certs)}", file=sys.stderr)
        print(f"periodically_pruned={len(periodic_masks)}", file=sys.stderr)
        print(f"after_periodic_filter={space.full_mask + 1 - len(periodic_masks)}", file=sys.stderr)
        for depth, before, after in stages:
            print(f"completion_depth={depth} tested={before} live={after} eliminated={before - after}", file=sys.stderr)
        print(f"good_results={len(alive)}", file=sys.stderr)
        print(f"torus_sat_calls={torus_calls}", file=sys.stderr)
    if args.certificates:
        for cert, width_t, height_t in sorted(certs, key=lambda x: (x[0].bit_count(), x[0])):
            print(f"certificate=0x{cert:0{width}x} bits={cert.bit_count()} torus={width_t}x{height_t} {mask_rules(space, cert)}", file=sys.stderr)


if __name__ == "__main__":
    main()
