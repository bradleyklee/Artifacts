#!/usr/bin/env python3
"""Exact vertex-merge reducer for the 9-hex Spectre source model.

This is the reproducibility step that produces the two reduced hexes used by
sage_hexagons.py.  It is deliberately conservative: a merge is accepted only
when remembered free-Wang rows stay injective, the transported slot matrix is
unchanged, and rebuilding free-Wang rows from the reduced tiles/rules produces
exactly the mapped row set.
"""
from __future__ import annotations

import argparse
import itertools
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

Label = str
Edge = Tuple[Label, Label]
Side = Tuple[Edge, Edge]
Row = Tuple[Side, ...]
Tile = Tuple[Label, ...]
VTri = Tuple[Label, Label, Label]


def canon_cycle(seq: Iterable) -> Tuple:
    x = tuple(seq)
    return min(x[i:] + x[:i] for i in range(len(x)))


def canon3(seq: Iterable[Label]) -> VTri:
    return canon_cycle(tuple(seq))  # type: ignore[return-value]


def canon_row(row: Iterable[Side]) -> Row:
    return canon_cycle(tuple(row))  # type: ignore[return-value]


def canon_tile(tile: Iterable[Label]) -> Tile:
    return canon_cycle(tuple(tile))  # type: ignore[return-value]


def parse_edge(text: str) -> Edge:
    a, b = [x.strip() for x in text.split(",")]
    return (a, b)


def fmt_edge(e: Edge) -> str:
    return f"{e[0]},{e[1]}"


def fmt_row(row: Row) -> str:
    return " | ".join(f"{fmt_edge(a)} = {fmt_edge(b)}" for a, b in row)


def edge_at(tile: Tile, rot: int, side: int) -> Edge:
    i = (side - rot) % 6
    return (tile[i], tile[(i + 1) % 6])


def vertex_at(tile: Tile, rot: int, corner: int) -> Label:
    return tile[(corner - rot) % 6]


def side_match(a: Side, b: Side) -> bool:
    return a[0] == b[1] and a[1] == b[0]


def slot_mask(a: Row, b: Row) -> int:
    mask = 0
    for i, sa in enumerate(a):
        for j, sb in enumerate(b):
            if side_match(sa, sb):
                mask |= 1 << (6 * i + j)
    return mask


def shift_mask(mask: int, row_shift: int, col_shift: int) -> int:
    out = 0
    for i in range(6):
        for j in range(6):
            ti = (i + row_shift) % 6
            tj = (j + col_shift) % 6
            if mask & (1 << (6 * ti + tj)):
                out |= 1 << (6 * i + j)
    return out


def row_canon_with_offset(raw: Row) -> Tuple[Row, int]:
    best = raw
    best_k = 0
    for k in range(1, 6):
        rot = raw[k:] + raw[:k]
        if rot < best:
            best = rot
            best_k = k
    return best, best_k


@dataclass(frozen=True)
class SourceModel:
    source_tiles: Tuple[Tile, ...]
    edge_rules: frozenset[Tuple[Edge, Edge]]
    vertex_rules: frozenset[VTri]
    free_rows: Tuple[Row, ...]

    @staticmethod
    def load(path: Path) -> "SourceModel":
        section = None
        tiles: Dict[int, Tile] = {}
        edge_rules: set[Tuple[Edge, Edge]] = set()
        vertex_rules: set[VTri] = set()
        rows: set[Row] = set()
        for raw in path.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1]
                continue
            if section == "source_tiles":
                name, rest = line.split(":", 1)
                tiles[int(name.strip().lstrip("T"))] = tuple(rest.split())
            elif section == "edge_rules":
                lhs, rhs = [x.strip() for x in line.split("=")]
                edge_rules.add((parse_edge(lhs), parse_edge(rhs)))
            elif section == "vertex_rules":
                vertex_rules.add(canon3(line.split()))
            elif section == "free_wang_rows":
                _, rest = line.split(":", 1)
                sides: List[Side] = []
                for part in rest.split("|"):
                    lhs, rhs = [x.strip() for x in part.split("=")]
                    sides.append((parse_edge(lhs), parse_edge(rhs)))
                rows.add(canon_row(sides))
        return SourceModel(
            source_tiles=tuple(tiles[i] for i in sorted(tiles)),
            edge_rules=frozenset(edge_rules),
            vertex_rules=frozenset(vertex_rules),
            free_rows=tuple(sorted(rows)),
        )


class DSU:
    def __init__(self, labels: Iterable[Label]):
        self.p = {x: x for x in labels}

    def copy(self) -> "DSU":
        q = DSU(())
        q.p = dict(self.p)
        return q

    def find(self, x: Label) -> Label:
        p = self.p.setdefault(x, x)
        while p != self.p[p]:
            self.p[p] = self.p[self.p[p]]
            p = self.p[p]
        # compress x
        while x != p:
            nxt = self.p[x]
            self.p[x] = p
            x = nxt
        return p

    def merge(self, a: Label, b: Label) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        keep, drop = sorted((ra, rb))
        self.p[drop] = keep
        for x in list(self.p):
            self.find(x)

    def key(self) -> Tuple[Tuple[Label, Label], ...]:
        return tuple(sorted((x, self.find(x)) for x in self.p))

    def reps(self) -> List[Label]:
        return sorted({self.find(x) for x in self.p})

    def map_label(self, x: Label) -> Label:
        return self.find(x)

    def map_edge(self, e: Edge) -> Edge:
        return (self.map_label(e[0]), self.map_label(e[1]))

    def map_side(self, s: Side) -> Side:
        return (self.map_edge(s[0]), self.map_edge(s[1]))

    def map_row_raw(self, row: Row) -> Row:
        return tuple(self.map_side(s) for s in row)

    def map_tile(self, tile: Tile) -> Tile:
        return canon_tile(self.map_label(x) for x in tile)

    def map_vtri(self, tri: VTri) -> VTri:
        return canon3(self.map_label(x) for x in tri)


def labels_in_model(model: SourceModel) -> List[Label]:
    out = set()
    for t in model.source_tiles:
        out.update(t)
    for a, b in model.edge_rules:
        out.update(a); out.update(b)
    for tri in model.vertex_rules:
        out.update(tri)
    for row in model.free_rows:
        for a, b in row:
            out.update(a); out.update(b)
    return sorted(out)


def matrix(rows: Tuple[Row, ...]) -> Tuple[Tuple[int, ...], ...]:
    return tuple(tuple(slot_mask(a, b) for b in rows) for a in rows)


def mapped_image(model: SourceModel, dsu: DSU):
    image_rows: List[Row] = []
    root_of: List[int] = []
    offsets: List[int] = []
    seen = set()
    for i, row in enumerate(model.free_rows):
        can, off = row_canon_with_offset(dsu.map_row_raw(row))
        if can in seen:
            return None
        seen.add(can)
        image_rows.append(can)
        root_of.append(i)
        offsets.append(off)
    order = sorted(range(len(image_rows)), key=lambda i: image_rows[i])
    return (
        tuple(image_rows[i] for i in order),
        [root_of[i] for i in order],
        [offsets[i] for i in order],
    )


def matrix_preserved(model: SourceModel, dsu: DSU, root_matrix) -> bool:
    out = mapped_image(model, dsu)
    if out is None:
        return False
    rows, root_of, offsets = out
    for i, row_a in enumerate(rows):
        for j, row_b in enumerate(rows):
            cur = slot_mask(row_a, row_b)
            old = root_matrix[root_of[i]][root_of[j]]
            want = shift_mask(old, offsets[i], offsets[j])
            if cur != want:
                return False
    return True


def rebuild_rows(tiles: Tuple[Tile, ...], edge_rules: frozenset[Tuple[Edge, Edge]], vertex_rules: frozenset[VTri], max_trials: int = 20_000_000):
    basic = [(i, tile, rot) for i, tile in enumerate(tiles) for rot in range(6)]
    rebuilt: set[Row] = set()
    surrounds = 0
    trials = 0
    for ci, center in enumerate(tiles):
        cand: List[List[Tuple[int, Tile, int]]] = []
        for d in range(6):
            ce = edge_at(center, 0, d)
            choices = [(ni, nt, nr) for ni, nt, nr in basic if (ce, edge_at(nt, nr, d + 3)) in edge_rules]
            cand.append(choices)
        if any(not c for c in cand):
            continue
        for ns in itertools.product(*cand):
            trials += 1
            if trials > max_trials:
                return rebuilt, surrounds, trials, True
            ok = True
            for d in range(6):
                _, lt, lr = ns[d]
                _, rt, rr = ns[(d + 1) % 6]
                if (edge_at(lt, lr, d + 2), edge_at(rt, rr, d + 5)) not in edge_rules:
                    ok = False
                    break
            if not ok:
                continue
            for j in range(6):
                _, pt, pr = ns[(j - 1) % 6]
                _, nt, nr = ns[j]
                tri = canon3((vertex_at(center, 0, j), vertex_at(pt, pr, j + 2), vertex_at(nt, nr, j + 4)))
                if tri not in vertex_rules:
                    ok = False
                    break
            if not ok:
                continue
            row = []
            for d in range(6):
                _, nt, nr = ns[d]
                row.append((edge_at(center, 0, d), edge_at(nt, nr, d + 3)))
            rebuilt.add(canon_row(row))
            surrounds += 1
    return rebuilt, surrounds, trials, False


def reduced_components(model: SourceModel, dsu: DSU):
    tiles = tuple(sorted({dsu.map_tile(t) for t in model.source_tiles}))
    edge_rules = frozenset((dsu.map_edge(a), dsu.map_edge(b)) for a, b in model.edge_rules)
    vertex_rules = frozenset(dsu.map_vtri(t) for t in model.vertex_rules)
    out = mapped_image(model, dsu)
    if out is None:
        return tiles, edge_rules, vertex_rules, None
    image_rows, _, _ = out
    return tiles, edge_rules, vertex_rules, image_rows


def acceptable(model: SourceModel, dsu: DSU, root_matrix, a: Label, b: Label, require_tile_drop: bool = True):
    before_tiles, _, _, _ = reduced_components(model, dsu)
    q = dsu.copy()
    q.merge(a, b)
    out = mapped_image(model, q)
    if out is None:
        return False, "row_collision", q, None
    if not matrix_preserved(model, q, root_matrix):
        return False, "matrix_changed", q, None
    tiles, erules, vrules, image_rows = reduced_components(model, q)
    assert image_rows is not None
    if require_tile_drop and len(tiles) >= len(before_tiles):
        return False, f"no_tile_drop tiles={len(tiles)}", q, None
    rebuilt, surrounds, trials, escaped = rebuild_rows(tiles, erules, vrules)
    if escaped:
        return False, f"rebuild_escape trials={trials}", q, None
    missing = set(image_rows) - rebuilt
    extra = rebuilt - set(image_rows)
    if missing:
        return False, f"missing_rows {len(missing)}", q, None
    if extra:
        return False, f"extra_rows {len(extra)}", q, None
    return True, f"ok tiles={len(tiles)} rows={len(image_rows)} surrounds={surrounds} trials={trials}", q, (tiles, erules, vrules, image_rows, surrounds, trials)


def search(model: SourceModel, verbose: bool = False, status_every: int = 200):
    labels = labels_in_model(model)
    root = DSU(labels)
    root_matrix = matrix(model.free_rows)
    queue = deque([(root, [])])
    seen = {root.key()}
    best = (len(model.source_tiles), root, [], None)
    stats = Counter()
    states = 0
    trials = 0
    accepted = 0
    while queue:
        dsu, path = queue.popleft()
        states += 1
        tiles, _, _, _ = reduced_components(model, dsu)
        if len(tiles) < best[0]:
            best = (len(tiles), dsu, path, None)
            print(f"best tiles={best[0]} depth={len(path)} path={' '.join(path) if path else 'root'}")
        reps = dsu.reps()
        for a, b in itertools.combinations(reps, 2):
            trials += 1
            ok, why, q, payload = acceptable(model, dsu, root_matrix, a, b)
            stats[why.split()[0]] += 1
            if verbose and (ok or trials <= 40 or trials % status_every == 0):
                print(f"try state={states} depth={len(path)} pair={a}={b} -> {why}")
            if not ok:
                continue
            accepted += 1
            key = q.key()
            if key in seen:
                continue
            seen.add(key)
            new_path = path + [f"{a}={b}"]
            tiles2, _, _, _ = reduced_components(model, q)
            print(f"accept depth={len(new_path)} tiles={len(tiles2)} path={' '.join(new_path)}")
            if len(tiles2) < best[0]:
                best = (len(tiles2), q, new_path, payload)
                print(f"best tiles={best[0]} depth={len(new_path)} path={' '.join(new_path)}")
            queue.append((q, new_path))
        if verbose:
            print(f"state_done state={states} depth={len(path)} queued={len(queue)} seen={len(seen)} trials={trials} accepted={accepted} best={best[0]}")
    return best, {"states": states, "trials": trials, "accepted": accepted, "seen": len(seen), "stats": stats}


def print_reduced(model: SourceModel, dsu: DSU) -> None:
    tiles, erules, vrules, rows = reduced_components(model, dsu)
    print("reduced_tiles")
    for i, t in enumerate(tiles):
        print(f"  H{i}: {' '.join(t)}")
    print(f"reduced_edge_rules {len(erules)}")
    print(f"reduced_vertex_rules {len(vrules)}")
    print(f"remembered_rows {len(rows or [])}")



def write_reduced_model(path: Path) -> None:
    """Write the stable, diagram-oriented reduced 2-hex model.

    The exhaustive exact reducer verifies that the source model has exactly one
    unique two-tile terminal under the accepted merge search.  This writer emits
    that terminal in the display alphabet used by sage_hexagons.py and the fact
    sheet skin.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("""# Reduced Spectre 2-hex model, diagram orientation.
# Hex cycles are listed in the orientation used by the generated figures.

[tiles]
H1: H A D E B G
H0: C A B F G I

[edge_rules]
A,B = B,G
A,B = C,A
A,B = G,H
A,B = G,I
A,B = I,C
A,D = C,A
B,F = C,A
B,F = D,E
B,F = F,G
B,G = A,B
B,G = E,B
C,A = A,B
C,A = A,D
C,A = B,F
C,A = G,I
C,A = H,A
D,E = B,F
D,E = G,I
E,B = B,G
E,B = G,I
F,G = B,F
F,G = G,I
F,G = I,C
G,H = A,B
G,I = A,B
G,I = C,A
G,I = D,E
G,I = E,B
G,I = F,G
H,A = C,A
I,C = A,B
I,C = F,G
I,C = I,C

[vertex_rules]
A A C
A A H
A B C
A B G
A B I
A G I
B B B
B B G
B G E
B G G
B I E
C F D
C F F
C I D
C I F
E G I
F F F
G G G
""")


def verify_reduced_model(path: Path) -> bool:
    section = None
    tiles: Dict[str, Tile] = {}
    edge_rules: set[Tuple[Edge, Edge]] = set()
    vertex_rules: set[VTri] = set()
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            continue
        if section == "tiles":
            name, rest = line.split(":", 1)
            tiles[name.strip()] = tuple(rest.split())
        elif section == "edge_rules":
            lhs, rhs = [x.strip() for x in line.split("=")]
            edge_rules.add((parse_edge(lhs), parse_edge(rhs)))
        elif section == "vertex_rules":
            vertex_rules.add(canon3(line.split()))

    expected_tiles = {
        "H1": ("H", "A", "D", "E", "B", "G"),
        "H0": ("C", "A", "B", "F", "G", "I"),
    }
    ok = True
    if tiles != expected_tiles:
        print(f"verify_reduced FAIL tiles={tiles}")
        ok = False
    if len(edge_rules) != 33:
        print(f"verify_reduced FAIL edge_rules={len(edge_rules)} expected=33")
        ok = False
    if len(vertex_rules) != 18:
        print(f"verify_reduced FAIL vertex_rules={len(vertex_rules)} expected=18")
        ok = False

    singular = []
    h1 = tiles.get("H1")
    if h1 is not None:
        for i in range(6):
            lhs = (h1[i], h1[(i + 1) % 6])
            matches = sorted(rhs for a, rhs in edge_rules if a == lhs)
            if len(matches) == 1:
                singular.append((lhs, matches[0]))
    expected_singular = [
        (("H", "A"), ("C", "A")),
        (("A", "D"), ("C", "A")),
        (("G", "H"), ("A", "B")),
    ]
    if singular != expected_singular:
        print(f"verify_reduced FAIL singular_H1={singular} expected={expected_singular}")
        ok = False
    if ok:
        print("verify_reduced ok")
        print(f"  tiles {len(tiles)}")
        print(f"  directed_edge_rules {len(edge_rules)}")
        print(f"  vertex_triples {len(vertex_rules)}")
        print(f"  singular_H1_edges {len(singular)}")
    return ok


def exhaustive_two_tile_terminals(model: SourceModel, verbose: bool = False, status_every: int = 500):
    """Exhaustively enumerate accepted merge states and collect two-tile terminals.

    This uses the same acceptance predicate as `search`: row injectivity,
    slot-matrix preservation, and exact rebuild with no missing/extra rows.
    It explores every accepted tile-dropping merge path, not just the first
    path that reaches two tiles.
    """
    labels = labels_in_model(model)
    root = DSU(labels)
    root_matrix = matrix(model.free_rows)
    queue = deque([(root, [])])
    seen = {root.key()}
    terminals: Dict[Tuple[Tile, ...], Tuple[DSU, List[str]]] = {}
    stats = Counter()
    states = 0
    trials = 0
    accepted = 0

    while queue:
        dsu, path = queue.popleft()
        states += 1
        tiles, _, _, _ = reduced_components(model, dsu)
        if len(tiles) == 2:
            terminals.setdefault(tiles, (dsu, path))
            # Do not merge past two for this uniqueness check.
            continue
        for a, b in itertools.combinations(labels, 2):
            if dsu.find(a) == dsu.find(b):
                continue
            trials += 1
            ok, why, q, _payload = acceptable(model, dsu, root_matrix, a, b, require_tile_drop=True)
            key = why.split()[0]
            stats[key] += 1
            if not ok:
                continue
            accepted += 1
            qkey = q.key()
            if qkey in seen:
                continue
            seen.add(qkey)
            queue.append((q, path + [f"{a}={b}"]))
        if verbose or (status_every and states % status_every == 0):
            print(f"exhaustive states={states} queue={len(queue)} terminals={len(terminals)} seen={len(seen)}")

    return terminals, {
        "states": states,
        "trials": trials,
        "accepted": accepted,
        "seen": len(seen),
        "stats": stats,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="data/spectre_unified_model_v0.dat")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--status-every", type=int, default=200)
    ap.add_argument("--check-path", default="b2=b1 b5=b6 b13=X b9=b8 b11=b10")
    ap.add_argument("--write-reduced", help="write stable reduced model .dat")
    ap.add_argument("--verify-reduced", help="verify stable reduced model .dat")
    ap.add_argument("--expect-unique-two", type=int, default=1,
                    help="expected number of unique two-tile terminals under exhaustive accepted-merge search")
    args = ap.parse_args()

    model = SourceModel.load(Path(args.model))
    print(f"source_tiles {len(model.source_tiles)}")
    print(f"source_edge_rules {len(model.edge_rules)}")
    print(f"source_vertex_rules {len(model.vertex_rules)}")
    print(f"source_free_wang_rows {len(model.free_rows)}")
    print("search_acceptance exact: row_injective matrix_preserved rebuild_exact no_extra_rows")

    terminals, einfo = exhaustive_two_tile_terminals(
        model,
        verbose=args.verbose,
        status_every=args.status_every,
    )
    print("exhaustive_two_tile_search")
    print(f"  states {einfo['states']}")
    print(f"  pair_trials {einfo['trials']}")
    print(f"  accepted_merges {einfo['accepted']}")
    print(f"  seen_states {einfo['seen']}")
    print(f"  rejection_counts {dict(sorted(einfo['stats'].items()))}")
    print(f"  unique_two_tile_terminals {len(terminals)}")
    for i, (tiles, (_dsu, path)) in enumerate(sorted(terminals.items())):
        print(f"  terminal {i}: path_len={len(path)} path={' '.join(path) if path else 'root'}")
        for j, t in enumerate(tiles):
            print(f"    T{j}: {' '.join(t)}")

    if len(terminals) != args.expect_unique_two:
        print(f"unique_two_tile_terminals FAIL expected={args.expect_unique_two} got={len(terminals)}")
        return 1
    print("unique_two_tile_terminals ok")

    # Keep the original best-path summary for continuity/debugging.
    best, info = search(model, verbose=args.verbose, status_every=args.status_every)
    print("summary")
    print(f"  states {info['states']}")
    print(f"  pair_trials {info['trials']}")
    print(f"  accepted_merges {info['accepted']}")
    print(f"  seen_states {info['seen']}")
    print(f"  rejection_counts {dict(sorted(info['stats'].items()))}")
    print(f"  best_tiles {best[0]}")
    print(f"  best_path {' '.join(best[2]) if best[2] else 'root'}")
    print_reduced(model, best[1])

    expected = args.check_path.split()
    if best[0] == 2 and best[2] == expected:
        print("check_path ok")
    elif best[0] == 2:
        print("check_path note: found a 2-tile path, but not the stored order")
    else:
        print("check_path FAIL: did not recover 2-tile model")
        return 1

    if args.write_reduced:
        write_reduced_model(Path(args.write_reduced))
        print(f"write_reduced {args.write_reduced}")
    if args.verify_reduced:
        if not verify_reduced_model(Path(args.verify_reduced)):
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
