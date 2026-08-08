#!/usr/bin/env python3
"""Exact small-n solver for a precise discrete P^4 interpretation.

Model implemented
-----------------
* A typogeometry is a rooted plane quadtree with four CCW slots
  (NW, SW, SE, NE), no unary internal nodes, and n true leaves.
* Its maximum depth is d.  At inflation l, the grid has width W=l*2^d.
* A true leaf owns every grid vertex in its dyadic block. Empty slots own none.
* A Polya path is a simple cycle in the W x W nearest-neighbor grid graph.
* Leaves receive a cyclic order 1,...,n. The cycle is valid when one may select
  one visited vertex from each leaf block in that cyclic order. Earlier visits
  to the same block are allowed, exactly as in the supplied prompt.
* For each labeled typogeometry we first minimize l, then minimize taxicab
  cycle length L at that first feasible l. Its reported normalized value is
  C=L/(l*2^d). This is a lexicographic "first-resolution" invariant; it is not
  the infimum of L/(l*2^d) over all l.

The fixed-l optimization is a binary multicommodity-flow MILP. Segment k joins
one selected vertex in region k to one selected vertex in region k+1. Vertex
and edge capacity constraints force the segments to form one simple cycle.
The positive edge objective removes disconnected cycles. SciPy's HiGHS backend
proves optimality/infeasibility for every reported case.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import time
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix, lil_matrix

LEAF = "L"
# Counterclockwise from NW when array y coordinates increase downward.
QUADRANTS = ((0, 0), (0, 1), (1, 1), (1, 0))  # NW, SW, SE, NE

Tree = str | tuple["Tree | None", "Tree | None", "Tree | None", "Tree | None"]


@dataclass(frozen=True)
class Instance:
    tree: Tree
    order: tuple[int, ...]
    base_labels: np.ndarray
    depth: int


@dataclass
class CycleSolution:
    length: int
    chosen: list[int]
    segments: list[list[int]]


@lru_cache(None)
def trees(n: int) -> tuple[Tree, ...]:
    """Enumerate all reduced four-slot plane quadtrees with n true leaves."""
    if n == 1:
        return (LEAF,)
    out: list[Tree] = []
    for counts in weak_compositions(n, 4):
        if sum(c > 0 for c in counts) < 2:
            continue  # suppress unary internal nodes
        choices: list[Sequence[Tree | None]] = [
            (None,) if c == 0 else trees(c) for c in counts
        ]
        out.extend(tuple(x) for x in itertools.product(*choices))
    return tuple(out)


def weak_compositions(total: int, parts: int) -> Iterable[tuple[int, ...]]:
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in weak_compositions(total - first, parts - 1):
            yield (first,) + rest


def typogeometry_formula(n: int) -> int:
    """Closed formula from the prompt; used as an independent count check."""
    total = 0
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if 1 + i + 2 * j + 3 * k != n:
                    continue
                m = n + i + j + k
                numerator = 6**i * 4**j * math.factorial(m - 1)
                denominator = (
                    math.factorial(n)
                    * math.factorial(i)
                    * math.factorial(j)
                    * math.factorial(k)
                )
                total += numerator // denominator
    return total


def tree_depth(tree: Tree) -> int:
    if tree == LEAF:
        return 0
    assert isinstance(tree, tuple)
    return 1 + max(tree_depth(child) for child in tree if child is not None)


def tree_to_leaf_grid(tree: Tree) -> tuple[np.ndarray, int, int]:
    """Return a 2^d square array of leaf IDs; -1 means empty."""
    depth = tree_depth(tree)
    width = 1 << depth
    grid = np.full((width, width), -1, dtype=np.int16)
    counter = [0]

    def fill(node: Tree, x0: int, y0: int, size: int) -> None:
        if node == LEAF:
            leaf_id = counter[0]
            counter[0] += 1
            grid[y0 : y0 + size, x0 : x0 + size] = leaf_id
            return
        assert isinstance(node, tuple)
        half = size // 2
        for slot, child in enumerate(node):
            if child is None:
                continue
            qx, qy = QUADRANTS[slot]
            fill(child, x0 + qx * half, y0 + qy * half, half)

    fill(tree, 0, 0, width)
    return grid, depth, counter[0]


def cyclic_orders(n: int) -> list[tuple[int, ...]]:
    """Cyclic orders of leaf IDs modulo rotation and reversal."""
    if n == 1:
        return [(0,)]
    if n == 2:
        return [(0, 1)]
    out = []
    for rest in itertools.permutations(range(1, n)):
        if rest <= rest[::-1]:
            out.append((0,) + rest)
    return out


def label_grid(leaf_grid: np.ndarray, order: tuple[int, ...]) -> np.ndarray:
    out = np.zeros_like(leaf_grid, dtype=np.int16)
    for label, leaf_id in enumerate(order, start=1):
        out[leaf_grid == leaf_id] = label
    return out


def d4_images(array: np.ndarray) -> Iterable[np.ndarray]:
    seen: set[bytes] = set()
    for k in range(4):
        rotated = np.rot90(array, k)
        for image in (rotated, np.fliplr(rotated)):
            key = image.tobytes()
            if key not in seen:
                seen.add(key)
                yield image


def relabel_cycle(array: np.ndarray, n: int, shift: int, sign: int) -> np.ndarray:
    out = array.copy()
    mask = out > 0
    values = out[mask] - 1
    out[mask] = ((sign * values + shift) % n) + 1
    return out


def canonical_key(array: np.ndarray, n: int) -> tuple[int, tuple[int, ...]]:
    """Quotient by global D4 and dihedral renaming of the cyclic labels."""
    best: tuple[int, tuple[int, ...]] | None = None
    for image in d4_images(array):
        for sign in (1, -1):
            for shift in range(n):
                relabeled = relabel_cycle(image, n, shift, sign)
                key = (relabeled.shape[0], tuple(int(x) for x in relabeled.ravel()))
                if best is None or key < best:
                    best = key
    assert best is not None
    return best


def representative_instances(n: int) -> list[Instance]:
    representatives: dict[tuple[int, tuple[int, ...]], Instance] = {}
    for tree in trees(n):
        leaves, depth, leaf_count = tree_to_leaf_grid(tree)
        assert leaf_count == n
        for order in cyclic_orders(n):
            labels = label_grid(leaves, order)
            representatives[canonical_key(labels, n)] = Instance(
                tree=tree, order=order, base_labels=labels, depth=depth
            )
    return list(representatives.values())


def expand_labels(base: np.ndarray, inflation: int) -> np.ndarray:
    return np.repeat(np.repeat(base, inflation, axis=0), inflation, axis=1)


def solve_fixed_grid(
    labels: np.ndarray,
    n: int,
    *,
    time_limit: float = 120.0,
) -> tuple[CycleSolution | None, str]:
    """Minimize simple-cycle length on one labeled square grid."""
    height, width = labels.shape
    if height != width:
        raise ValueError("grid must be square")
    vertex_count = width * height

    undirected: list[tuple[int, int]] = []
    for y in range(height):
        for x in range(width):
            v = y * width + x
            if x + 1 < width:
                undirected.append((v, v + 1))
            if y + 1 < height:
                undirected.append((v, v + width))

    directed: list[tuple[int, int]] = []
    for a, b in undirected:
        directed.extend(((a, b), (b, a)))
    directed_count = len(directed)

    out_edges: list[list[int]] = [[] for _ in range(vertex_count)]
    in_edges: list[list[int]] = [[] for _ in range(vertex_count)]
    for edge_id, (a, b) in enumerate(directed):
        out_edges[a].append(edge_id)
        in_edges[b].append(edge_id)

    region_cells: dict[int, list[int]] = {}
    z_index: dict[tuple[int, int], int] = {}
    next_var = n * directed_count
    for k in range(n):
        cells = [
            v
            for v in range(vertex_count)
            if int(labels[v // width, v % width]) == k + 1
        ]
        if not cells:
            raise ValueError(f"region {k + 1} has no cells")
        region_cells[k] = cells
        for v in cells:
            z_index[k, v] = next_var
            next_var += 1

    variable_count = next_var
    objective = np.zeros(variable_count)
    objective[: n * directed_count] = 1.0
    integrality = np.ones(variable_count, dtype=np.uint8)
    bounds = Bounds(np.zeros(variable_count), np.ones(variable_count))

    sparse_rows: list[dict[int, float]] = []
    lower: list[float] = []
    upper: list[float] = []

    # Select exactly one actual point in every coarse-point region.
    for k in range(n):
        row = {z_index[k, v]: 1.0 for v in region_cells[k]}
        sparse_rows.append(row)
        lower.append(1.0)
        upper.append(1.0)

    # Commodity k goes from selected region k to selected region k+1.
    for k in range(n):
        next_k = (k + 1) % n
        for v in range(vertex_count):
            row: dict[int, float] = {}
            for edge_id in out_edges[v]:
                row[k * directed_count + edge_id] = 1.0
            for edge_id in in_edges[v]:
                index = k * directed_count + edge_id
                row[index] = row.get(index, 0.0) - 1.0
            if (k, v) in z_index:
                row[z_index[k, v]] = row.get(z_index[k, v], 0.0) - 1.0
            if (next_k, v) in z_index:
                row[z_index[next_k, v]] = row.get(z_index[next_k, v], 0.0) + 1.0
            sparse_rows.append(row)
            lower.append(0.0)
            upper.append(0.0)

    # A simple cycle has total incident directed degree at most two per vertex.
    for v in range(vertex_count):
        row = {}
        for k in range(n):
            for edge_id in out_edges[v] + in_edges[v]:
                row[k * directed_count + edge_id] = 1.0
        sparse_rows.append(row)
        lower.append(-np.inf)
        upper.append(2.0)

    # No undirected grid edge may be used twice, even in opposite directions.
    for undirected_id in range(len(undirected)):
        row = {}
        forward = 2 * undirected_id
        backward = forward + 1
        for k in range(n):
            row[k * directed_count + forward] = 1.0
            row[k * directed_count + backward] = 1.0
        sparse_rows.append(row)
        lower.append(-np.inf)
        upper.append(1.0)

    matrix = lil_matrix((len(sparse_rows), variable_count), dtype=float)
    for row_id, row in enumerate(sparse_rows):
        for col, value in row.items():
            matrix[row_id, col] = value

    result = milp(
        objective,
        integrality=integrality,
        bounds=bounds,
        constraints=LinearConstraint(
            csr_matrix(matrix), np.asarray(lower), np.asarray(upper)
        ),
        options={
            "presolve": True,
            "mip_rel_gap": 0.0,
            "time_limit": time_limit,
            "disp": False,
        },
    )

    if not result.success:
        message = result.message.lower()
        if "infeasible" in message:
            return None, "infeasible"
        if "time limit reached" in message:
            return None, "timeout"
        raise RuntimeError(f"MILP did not finish: {result.message}")

    edge_values = result.x[: n * directed_count].reshape(n, directed_count)
    chosen = [
        next(v for v in region_cells[k] if result.x[z_index[k, v]] > 0.5)
        for k in range(n)
    ]
    segments: list[list[int]] = []
    for k in range(n):
        successor = {
            a: b
            for edge_id, (a, b) in enumerate(directed)
            if edge_values[k, edge_id] > 0.5
        }
        target = chosen[(k + 1) % n]
        current = chosen[k]
        path = [current]
        while current != target:
            if current not in successor:
                raise AssertionError("broken MILP path")
            current = successor[current]
            path.append(current)
            if len(path) > vertex_count + 1:
                raise AssertionError("cycle inside a commodity")
        segments.append(path)

    solution = CycleSolution(
        length=int(round(float(result.fun))), chosen=chosen, segments=segments
    )
    verify_solution(labels, n, solution)
    return solution, "optimal"


def verify_solution(labels: np.ndarray, n: int, solution: CycleSolution) -> None:
    """Independent structural verification of a returned primal cycle."""
    width = labels.shape[1]
    if len(solution.chosen) != n or len(solution.segments) != n:
        raise AssertionError("wrong number of markers or segments")
    for k, v in enumerate(solution.chosen):
        if int(labels[v // width, v % width]) != k + 1:
            raise AssertionError("chosen point is outside its region")

    all_edges: set[tuple[int, int]] = set()
    full_cycle: list[int] = []
    for k, path in enumerate(solution.segments):
        if path[0] != solution.chosen[k]:
            raise AssertionError("wrong segment start")
        if path[-1] != solution.chosen[(k + 1) % n]:
            raise AssertionError("wrong segment end")
        if len(path) != len(set(path)):
            raise AssertionError("segment repeats a vertex")
        for a, b in zip(path, path[1:]):
            ax, ay = a % width, a // width
            bx, by = b % width, b // width
            if abs(ax - bx) + abs(ay - by) != 1:
                raise AssertionError("non-nearest-neighbor step")
            edge = tuple(sorted((a, b)))
            if edge in all_edges:
                raise AssertionError("grid edge reused")
            all_edges.add(edge)
        if not full_cycle:
            full_cycle.extend(path)
        else:
            full_cycle.extend(path[1:])

    if full_cycle[0] != full_cycle[-1]:
        raise AssertionError("cycle does not close")
    body = full_cycle[:-1]
    if len(body) != len(set(body)):
        raise AssertionError("cycle repeats a vertex")
    if len(all_edges) != solution.length or len(body) != solution.length:
        raise AssertionError("reported length is inconsistent")


def tree_notation(tree: Tree) -> str:
    if tree == LEAF:
        return "▪"
    assert isinstance(tree, tuple)
    return "⟨" + "".join("□" if x is None else tree_notation(x) for x in tree) + "⟩"


def solution_to_json(
    instance: Instance,
    inflation: int,
    solution: CycleSolution,
) -> dict:
    width = inflation * (1 << instance.depth)
    return {
        "tree": tree_notation(instance.tree),
        "leaf_order_zero_based": list(instance.order),
        "depth": instance.depth,
        "inflation": inflation,
        "grid_width": width,
        "taxicab_length": solution.length,
        "normalized_value": solution.length / width,
        "base_label_grid": instance.base_labels.tolist(),
        "chosen_xy": [[v % width, v // width] for v in solution.chosen],
        "segments_xy": [
            [[v % width, v // width] for v in segment]
            for segment in solution.segments
        ],
    }


def solve_n(
    n: int,
    *,
    max_inflation: int,
    time_limit: float,
    progress_every: int,
) -> tuple[dict, list[dict]]:
    raw_trees = len(trees(n))
    formula_count = typogeometry_formula(n)
    if raw_trees != formula_count:
        raise AssertionError((raw_trees, formula_count))
    instances = representative_instances(n)
    started = time.time()

    print(
        f"[n={n}] trees={raw_trees} cyclic_orders={len(cyclic_orders(n))} "
        f"symmetry_classes={len(instances)}"
    )

    # Batch by inflation. In practice this is much faster and more stable than
    # alternating infeasibility proofs and larger-grid optimizations.
    unresolved = list(range(len(instances)))
    record_by_index: dict[int, dict] = {}
    for inflation in range(1, max_inflation + 1):
        next_unresolved: list[int] = []
        phase_started = time.time()
        for phase_index, instance_index in enumerate(unresolved, start=1):
            instance = instances[instance_index]
            expanded = expand_labels(instance.base_labels, inflation)
            solution, status = solve_fixed_grid(
                expanded, n, time_limit=time_limit
            )
            if solution is None:
                next_unresolved.append(instance_index)
            else:
                record = solution_to_json(instance, inflation, solution)
                record["representative_index"] = instance_index
                record_by_index[instance_index] = record
            if phase_index % progress_every == 0 or phase_index == len(unresolved):
                print(
                    f"[n={n},l={inflation}] {phase_index}/{len(unresolved)}; "
                    f"still_unresolved={len(next_unresolved)}; "
                    f"phase_elapsed={time.time() - phase_started:.2f}s"
                )
        unresolved = next_unresolved
        if not unresolved:
            break

    if unresolved:
        raise RuntimeError(
            f"no cycle found through inflation {max_inflation} for "
            f"{len(unresolved)} symmetry classes"
        )

    records = [record_by_index[i] for i in range(len(instances))]
    max_value = max(r["normalized_value"] for r in records)
    max_taxicab = max(r["taxicab_length"] for r in records)
    summary = {
        "n": n,
        "typogeometry_count": raw_trees,
        "cyclic_orders_mod_dihedral": len(cyclic_orders(n)),
        "raw_labeled_instances": raw_trees * len(cyclic_orders(n)),
        "global_symmetry_classes": len(instances),
        "first_resolution_value": max_value,
        "first_resolution_value_fraction": fraction_string(max_value),
        "maximum_taxicab_length": max_taxicab,
        "metric_witness_count_among_classes": sum(
            r["normalized_value"] == max_value for r in records
        ),
        "taxicab_witness_count_among_classes": sum(
            r["taxicab_length"] == max_taxicab for r in records
        ),
        "inflation_histogram": dict(
            sorted(Counter(r["inflation"] for r in records).items())
        ),
        "runtime_seconds": time.time() - started,
    }
    return summary, records


def fraction_string(value: float) -> str:
    from fractions import Fraction

    return str(Fraction(value).limit_denominator())


def write_results(output: Path, summaries: list[dict], all_records: dict[int, list[dict]]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": "first feasible inflation, then shortest simple cycle",
        "warning": (
            "This is a lexicographic first-resolution invariant, not the infimum "
            "over all inflations."
        ),
        "summaries": summaries,
    }
    (output / "exact_terms.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (output / "exact_terms.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "n",
                "typogeometry_count",
                "raw_labeled_instances",
                "global_symmetry_classes",
                "first_resolution_value_fraction",
                "maximum_taxicab_length",
                "runtime_seconds",
            ],
        )
        writer.writeheader()
        for summary in summaries:
            writer.writerow({k: summary[k] for k in writer.fieldnames})

    for n, records in all_records.items():
        (output / f"n{n}_class_records.json").write_text(
            json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-n", type=int, default=2)
    parser.add_argument("--max-n", type=int, default=4)
    parser.add_argument("--max-inflation", type=int, default=2)
    parser.add_argument("--time-limit", type=float, default=120.0)
    parser.add_argument("--progress-every", type=int, default=50)
    parser.add_argument("--output", type=Path, default=Path("results"))
    args = parser.parse_args()

    if args.min_n < 2 or args.max_n < args.min_n:
        parser.error("require 2 <= min-n <= max-n")

    summaries = []
    all_records: dict[int, list[dict]] = {}
    overall = time.time()
    for n in range(args.min_n, args.max_n + 1):
        summary, records = solve_n(
            n,
            max_inflation=args.max_inflation,
            time_limit=args.time_limit,
            progress_every=args.progress_every,
        )
        summaries.append(summary)
        all_records[n] = records
        print(
            f"[n={n}] C_first={summary['first_resolution_value_fraction']} "
            f"max_L={summary['maximum_taxicab_length']}"
        )
    write_results(args.output, summaries, all_records)
    print(f"[done] total_runtime={time.time() - overall:.2f}s output={args.output}")


if __name__ == "__main__":
    main()
