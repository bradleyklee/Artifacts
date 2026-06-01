#!/usr/bin/env python3
"""SAT search for periodic-pruned equilateral triangle rule systems.

Tiles are orientation-preserving only: the three cyclic CCW rotations of ABC
and of DEF.  Reflections are never admitted.

Rule families
-------------
anchored (default)
    AB=DE is mandatory and every other join involving AB is forbidden.  The
    optional unordered joins with repetition on {BC, CA, DE, EF, FD} give 15
    variable bits.

unrestricted
    AB=DE is mandatory.  Every other unordered join with repetition on all six
    edge types is optional, giving 20 variable bits.

free
    Every unordered join with repetition on all six edge types is optional,
    giving 21 variable bits.  Masks are canonicalized under independent cyclic
    relabeling of ABC and DEF and interchange of the two triangle species: the
    18-element (C3 x C3) semidirect C2 symmetry group.

Search filters
--------------
1. Trivial-periodic filtering finds one-tile periodic certificates, meaning a
   torus filled with one repeated oriented CCW triangle state.
2. General periodic filtering SAT-solves periodic W x H parallelogram tori.
   A satisfying torus uses an optional-rule certificate C; every mask
   containing C permits that same periodic tiling and is pruned.
3. Completion filtering SAT-solves successively larger finite patches obtained
   by closing around a central triangle.  A survivor must fill the requested
   maximum completion depth.

The SAT encoding is direct in triangle geometry.  It does not use reconstructed
local-model certificates or adjacency-matrix hashing.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations_with_replacement, product
from typing import Iterable

try:
    from pysat.solvers import Solver
except ImportError as exc:  # pragma: no cover
    raise SystemExit("python-sat is required: python3 -m pip install python-sat") from exc

EDGE_NAMES = ("AB", "BC", "CA", "DE", "EF", "FD")
AB, BC, CA, DE, EF, FD = range(6)
ALL_EDGES = (AB, BC, CA, DE, EF, FD)
ANCHORED_EDGES = (BC, CA, DE, EF, FD)
AB_DE = tuple(sorted((AB, DE)))
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
    mandatory_pairs: frozenset[tuple[int, int]]
    quotient_symmetry: bool = False

    @property
    def pair_to_bit(self) -> dict[tuple[int, int], int]:
        return {pair: bit for bit, pair in enumerate(self.variable_pairs)}

    @property
    def bits(self) -> int:
        return len(self.variable_pairs)

    @property
    def full_mask(self) -> int:
        return (1 << self.bits) - 1

    @property
    def hex_width(self) -> int:
        return max(4, (self.bits + 3) // 4)


def rule_space(family: str) -> RuleSpace:
    if family == "anchored":
        pairs = tuple(combinations_with_replacement(ANCHORED_EDGES, 2))
        return RuleSpace(family, pairs, frozenset((AB_DE,)))
    if family == "unrestricted":
        pairs = tuple(pair for pair in combinations_with_replacement(ALL_EDGES, 2) if pair != AB_DE)
        return RuleSpace(family, pairs, frozenset((AB_DE,)))
    if family == "free":
        pairs = tuple(combinations_with_replacement(ALL_EDGES, 2))
        return RuleSpace(family, pairs, frozenset(), quotient_symmetry=True)
    raise ValueError(f"unknown family {family!r}")


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
    if pair in space.mandatory_pairs:
        return True
    bit = space.pair_to_bit.get(pair)
    return bit is not None and bool(mask & (1 << bit))


def optional_join_bit(space: RuleSpace, x: int, y: int) -> int:
    pair = tuple(sorted((x, y)))
    if pair in space.mandatory_pairs:
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
        if geometry.center is not None and self.space.family != "free":
            # Anchored families may fix the distinguished phase.  In the fully
            # free family a fixed center phase would remove valid masks before
            # quotienting, so all six CCW center states remain admissible.
            self.solver.add_clause([tile_var(self.space, geometry.center, state) for state in CENTRAL_STATE_IDS])
        for a, sa, b, sb in geometry.contacts:
            for ta, state_a in enumerate(STATES):
                for tb, state_b in enumerate(STATES):
                    pair = tuple(sorted((state_a[sa], state_b[sb])))
                    prefix = [-tile_var(self.space, a, ta), -tile_var(self.space, b, tb)]
                    if pair in self.space.mandatory_pairs:
                        continue
                    bit = pair_to_bit.get(pair)
                    if bit is None:
                        self.solver.add_clause(prefix)
                    else:
                        self.solver.add_clause(prefix + [rule_var(bit)])

    def close(self) -> None:
        self.solver.delete()

    def solve(self, mask: int, want_witness: bool = False) -> Witness | None:
        assumptions = [rule_var(bit) if mask & (1 << bit) else -rule_var(bit) for bit in range(self.space.bits)]
        if not self.solver.solve(assumptions=assumptions):
            return None
        if not want_witness:
            return Witness((), 0)
        model = {lit for lit in self.solver.get_model() if lit > 0}
        chosen: list[int] = []
        for cell in range(len(self.geometry.cells)):
            selected = [state for state in range(len(STATES)) if tile_var(self.space, cell, state) in model]
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
    return tuple((w, product // w) for product in range(1, area + 1) for w in range(1, product + 1) if product % w == 0)


def mask_rules(space: RuleSpace, mask: int) -> str:
    rules = [f"{EDGE_NAMES[x]}={EDGE_NAMES[y]}" for bit, (x, y) in enumerate(space.variable_pairs) if mask & (1 << bit)]
    return ",".join(rules) if rules else "-"


def covers(mask: int, certificate: int) -> bool:
    return mask & certificate == certificate


# For the free family, independent cyclic relabelings and optional tile swap.
ABC_CYCLE = (AB, BC, CA)
DEF_CYCLE = (DE, EF, FD)


def symmetry_maps(space: RuleSpace) -> tuple[tuple[int, ...], ...]:
    if not space.quotient_symmetry:
        return (tuple(ALL_EDGES),)
    maps: list[tuple[int, ...]] = []
    for rabc in range(3):
        for rdef in range(3):
            for swap in (False, True):
                mapping = list(ALL_EDGES)
                target_abc = DEF_CYCLE if swap else ABC_CYCLE
                target_def = ABC_CYCLE if swap else DEF_CYCLE
                for k, edge in enumerate(ABC_CYCLE):
                    mapping[edge] = target_abc[(k + rabc) % 3]
                for k, edge in enumerate(DEF_CYCLE):
                    mapping[edge] = target_def[(k + rdef) % 3]
                maps.append(tuple(mapping))
    return tuple(dict.fromkeys(maps))


def transform_mask(space: RuleSpace, mask: int, mapping: tuple[int, ...]) -> int:
    transformed = 0
    pair_to_bit = space.pair_to_bit
    for bit, pair in enumerate(space.variable_pairs):
        if mask & (1 << bit):
            image = tuple(sorted((mapping[pair[0]], mapping[pair[1]])))
            transformed |= 1 << pair_to_bit[image]
    return transformed


def mask_orbit(space: RuleSpace, mask: int) -> tuple[int, ...]:
    return tuple(sorted({transform_mask(space, mask, mapping) for mapping in symmetry_maps(space)}))


def canonical_mask(space: RuleSpace, mask: int) -> int:
    return min(mask_orbit(space, mask))


def is_representative(space: RuleSpace, mask: int) -> bool:
    return not space.quotient_symmetry or canonical_mask(space, mask) == mask


def representative_orbits(space: RuleSpace) -> dict[int, tuple[int, ...]]:
    if not space.quotient_symmetry:
        return {mask: (mask,) for mask in range(space.full_mask + 1)}
    seen: set[int] = set()
    orbits: dict[int, tuple[int, ...]] = {}
    for mask in range(space.full_mask + 1):
        if mask in seen:
            continue
        orbit = mask_orbit(space, mask)
        seen.update(orbit)
        orbits[min(orbit)] = orbit
    return orbits


def representative_masks(space: RuleSpace) -> list[int]:
    return list(representative_orbits(space))


@lru_cache(maxsize=2048)
def certificate_orbit(space: RuleSpace, certificate: int) -> tuple[int, ...]:
    return mask_orbit(space, certificate)


def covers_under_symmetry(space: RuleSpace, mask: int, certificate: int) -> bool:
    return any(covers(mask, image) for image in certificate_orbit(space, certificate))


def add_minimal_certificate(space: RuleSpace, certs: list[tuple[int, int, int]],
                            certificate: int, width: int, height: int) -> None:
    if any(covers_under_symmetry(space, certificate, old) for old, _, _ in certs):
        return
    certs[:] = [(old, w, h) for old, w, h in certs
                if not covers_under_symmetry(space, old, certificate)]
    certs.append((certificate, width, height))


def one_tile_certificates(space: RuleSpace) -> list[tuple[int, int, int]]:
    """Certificates for a torus filled by one repeated oriented state."""
    geometry = torus(1, 1)
    certs: list[tuple[int, int, int]] = []
    for state in STATES:
        used = 0
        legal = True
        for _, sa, _, sb in geometry.contacts:
            pair = tuple(sorted((state[sa], state[sb])))
            if pair in space.mandatory_pairs:
                continue
            bit = space.pair_to_bit.get(pair)
            if bit is None:
                legal = False
                break
            used |= 1 << bit
        if legal:
            add_minimal_certificate(space, certs, used, 1, 1)
    return certs


def direct_1x1_certificates(space: RuleSpace) -> list[tuple[int, int, int]]:
    """Enumerate all 36 U/D assignments on the one-cell torus directly."""
    geometry = torus(1, 1)
    certs: list[tuple[int, int, int]] = []
    for chosen in product(range(len(STATES)), repeat=2):
        used = 0
        legal = True
        for a, sa, b, sb in geometry.contacts:
            left, right = STATES[chosen[a]][sa], STATES[chosen[b]][sb]
            pair = tuple(sorted((left, right)))
            if pair in space.mandatory_pairs:
                continue
            bit = space.pair_to_bit.get(pair)
            if bit is None:
                legal = False
                break
            used |= 1 << bit
        if legal:
            add_minimal_certificate(space, certs, used, 1, 1)
    return certs


def periodic_certificates(dims: tuple[tuple[int, int], ...], solver_name: str,
                          space: RuleSpace | None = None,
                          representatives: list[int] | None = None) -> tuple[list[tuple[int, int, int]], int, int]:
    space = space or rule_space("anchored")
    one_tile = one_tile_certificates(space)
    certs: list[tuple[int, int, int]] = list(one_tile)
    if (1, 1) in dims:
        for cert, width, height in direct_1x1_certificates(space):
            add_minimal_certificate(space, certs, cert, width, height)
    sat_calls = 0
    sat_dims = tuple((width, height) for width, height in dims if (width, height) != (1, 1))
    encodings = [(width, height, EncodedGeometry(torus(width, height), solver_name, space)) for width, height in sat_dims]
    try:
        masks = representatives if representatives is not None else representative_masks(space)
        masks = sorted(masks, key=lambda m: (m.bit_count(), m))
        for mask in masks:
            if any(covers_under_symmetry(space, mask, cert) for cert, _, _ in certs):
                continue
            for width, height, encoding in encodings:
                sat_calls += 1
                witness = encoding.solve(mask, want_witness=True)
                if witness is None:
                    continue
                certificate = witness.used_mask
                for a, sa, b, sb in encoding.geometry.contacts:
                    assert join_allowed(space, certificate, STATES[witness.states[a]][sa], STATES[witness.states[b]][sb])
                add_minimal_certificate(space, certs, certificate, width, height)
                break
    finally:
        for _, _, encoding in encodings:
            encoding.close()
    return certs, sat_calls, len(one_tile)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    period = parser.add_mutually_exclusive_group(required=True)
    period.add_argument("--periodic-depth", type=int, metavar="A", help="test every ordered WxH torus with W*H <= A")
    period.add_argument("--tori", help="exact comma-separated tori, for example 1x1,1x2,2x1")
    parser.add_argument("--family", choices=("anchored", "unrestricted", "free"), default="anchored", help="rule family; default anchored")
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
    space = rule_space(args.family)

    orbit_map = representative_orbits(space)
    representatives = list(orbit_map)
    certs, torus_calls, one_tile_count = periodic_certificates(dims, args.solver, space, representatives)
    one_tile = certs[:one_tile_count]
    orbit_sizes = {mask: len(orbit) for mask, orbit in orbit_map.items()}
    one_tile_pruned_full = sum(orbit_sizes[mask] for mask in representatives
                               if any(covers_under_symmetry(space, mask, cert) for cert, _, _ in one_tile))
    periodic_pruned_full = sum(orbit_sizes[mask] for mask in representatives
                               if any(covers_under_symmetry(space, mask, cert) for cert, _, _ in certs))
    alive = [mask for mask in representatives if not any(covers_under_symmetry(space, mask, cert) for cert, _, _ in certs)]
    stages: list[tuple[int, int, int]] = []
    for depth in range(1, args.completion_depth + 1):
        before = len(alive)
        encoding = EncodedGeometry(completion_patch(depth), args.solver, space)
        try:
            alive = [mask for mask in alive if encoding.solve(mask) is not None]
        finally:
            encoding.close()
        stages.append((depth, before, len(alive)))

    for mask in alive:
        print(f"0x{mask:0{space.hex_width}x}\tbits={mask.bit_count()}\t{mask_rules(space, mask)}")

    if args.summary:
        print(f"family={space.family}", file=sys.stderr)
        print(f"optional_rule_bits={space.bits}", file=sys.stderr)
        print(f"total_masks={space.full_mask + 1}", file=sys.stderr)
        print(f"symmetry_actions={len(symmetry_maps(space))}", file=sys.stderr)
        print(f"canonical_rule_masks={len(representatives)}", file=sys.stderr)
        print("periodic_tori=" + ",".join(f"{w}x{h}" for w, h in dims), file=sys.stderr)
        print(f"minimal_one_tile_certificates={one_tile_count}", file=sys.stderr)
        print(f"one_tile_pruned_full_masks={one_tile_pruned_full}", file=sys.stderr)
        print(f"minimal_periodic_certificates={len(certs)}", file=sys.stderr)
        print(f"periodically_pruned_full_masks={periodic_pruned_full}", file=sys.stderr)
        print(f"periodically_pruned={periodic_pruned_full}", file=sys.stderr)
        print(f"after_periodic_filter_canonical={len(alive) if not stages else stages[0][1]}", file=sys.stderr)
        for depth, before, after in stages:
            print(f"completion_depth={depth} tested={before} live={after} eliminated={before - after}", file=sys.stderr)
        print(f"good_results_canonical={len(alive)}", file=sys.stderr)
        print(f"good_results={len(alive)}", file=sys.stderr)
        print(f"torus_sat_calls={torus_calls}", file=sys.stderr)
    if args.certificates:
        for index, (cert, width_t, height_t) in enumerate(sorted(certs, key=lambda x: (x[0].bit_count(), canonical_mask(space, x[0]), x[0])), start=1):
            kind = "one-tile" if index <= one_tile_count else "periodic"
            print(f"certificate=0x{canonical_mask(space, cert):0{space.hex_width}x} bits={cert.bit_count()} torus={width_t}x{height_t} kind={kind} {mask_rules(space, canonical_mask(space, cert))}", file=sys.stderr)


if __name__ == "__main__":
    main()
