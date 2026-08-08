#!/usr/bin/env python3
"""Randomized constructive search for hard five-point P^4 instances.

This is a discovery tool, not a proof engine. It scans all depth-two symmetry
classes and optional random deeper classes, constructs simple cycles by
randomized vertex-disjoint routing, ranks hard-looking instances, and can send
selected candidates to the exact HiGHS MILP solver from p4_solver.py.
"""
from __future__ import annotations

import argparse
import heapq
import json
import math
import random
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import p4_solver as p4


@dataclass
class HeuristicResult:
    solution: p4.CycleSolution | None
    trials: int


def depth_instances(n: int, depth: int) -> list[p4.Instance]:
    reps: dict[tuple[int, tuple[int, ...]], p4.Instance] = {}
    for tree in p4.trees(n):
        if p4.tree_depth(tree) != depth:
            continue
        leaves, d, count = p4.tree_to_leaf_grid(tree)
        assert count == n and d == depth
        for order in p4.cyclic_orders(n):
            labels = p4.label_grid(leaves, order)
            reps[p4.canonical_key(labels, n)] = p4.Instance(tree, order, labels, d)
    return list(reps.values())


def random_instances(n: int, depths: tuple[int, ...], count: int, rng: random.Random) -> list[p4.Instance]:
    pool = [t for t in p4.trees(n) if p4.tree_depth(t) in depths]
    orders = p4.cyclic_orders(n)
    seen: set[tuple[int, tuple[int, ...]]] = set()
    out: list[p4.Instance] = []
    attempts = 0
    while len(out) < count and attempts < 20 * count:
        attempts += 1
        tree = rng.choice(pool)
        leaves, depth, leaf_count = p4.tree_to_leaf_grid(tree)
        order = rng.choice(orders)
        labels = p4.label_grid(leaves, order)
        key = p4.canonical_key(labels, n)
        if key in seen:
            continue
        seen.add(key)
        out.append(p4.Instance(tree, order, labels, depth))
    return out


def region_vertices(labels: np.ndarray, n: int) -> list[list[int]]:
    w = labels.shape[1]
    return [
        [y * w + x for y in range(w) for x in range(w) if int(labels[y, x]) == k + 1]
        for k in range(n)
    ]


def manhattan(a: int, b: int, width: int) -> int:
    return abs(a % width - b % width) + abs(a // width - b // width)


def terminal_cycle_lower_bound(labels: np.ndarray, n: int) -> tuple[int, list[int]]:
    """Exact minimum cyclic Manhattan distance, ignoring disjointness."""
    width = labels.shape[1]
    regions = region_vertices(labels, n)
    best_cost = math.inf
    best_terminals: list[int] = []
    for start in regions[0]:
        costs = {start: 0}
        parents: list[dict[int, int]] = []
        prev_region = [start]
        for k in range(1, n):
            new_costs: dict[int, int] = {}
            parent: dict[int, int] = {}
            for v in regions[k]:
                u = min(prev_region, key=lambda q: costs[q] + manhattan(q, v, width))
                new_costs[v] = costs[u] + manhattan(u, v, width)
                parent[v] = u
            parents.append(parent)
            costs = new_costs
            prev_region = list(new_costs)
        end = min(prev_region, key=lambda q: costs[q] + manhattan(q, start, width))
        total = costs[end] + manhattan(end, start, width)
        if total < best_cost:
            terminals = [0] * n
            terminals[-1] = end
            for k in range(n - 1, 0, -1):
                terminals[k - 1] = parents[k - 1][terminals[k]]
            best_cost = total
            best_terminals = terminals
    return int(best_cost), best_terminals


def random_terminals(labels: np.ndarray, n: int, rng: random.Random, base: list[int] | None) -> list[int]:
    regions = region_vertices(labels, n)
    if base is not None and rng.random() < 0.35:
        terminals = list(base)
        # Mutate one or two points to nearby/random alternatives.
        for _ in range(1 if rng.random() < 0.7 else 2):
            k = rng.randrange(n)
            old = terminals[k]
            candidates = sorted(regions[k], key=lambda v: manhattan(old, v, labels.shape[1]))
            terminals[k] = rng.choice(candidates[: max(1, min(6, len(candidates)))])
        return terminals
    return [rng.choice(region) for region in regions]


def randomized_path(
    width: int,
    source: int,
    target: int,
    blocked_vertices: set[int],
    blocked_edges: set[tuple[int, int]],
    rng: random.Random,
    noise: float,
) -> list[int] | None:
    count = width * width
    dist = [math.inf] * count
    parent = [-1] * count
    dist[source] = 0.0
    heap = [(0.0, rng.random(), source)]
    while heap:
        cost, _, v = heapq.heappop(heap)
        if cost != dist[v]:
            continue
        if v == target:
            break
        x, y = v % width, v // width
        neigh = []
        if x: neigh.append(v - 1)
        if x + 1 < width: neigh.append(v + 1)
        if y: neigh.append(v - width)
        if y + 1 < width: neigh.append(v + width)
        rng.shuffle(neigh)
        for u in neigh:
            if u != target and u in blocked_vertices:
                continue
            edge = tuple(sorted((u, v)))
            if edge in blocked_edges:
                continue
            # Small random perturbation gives many near-shortest alternatives.
            step = 1.0 + noise * rng.random()
            nc = cost + step
            if nc < dist[u]:
                dist[u] = nc
                parent[u] = v
                heapq.heappush(heap, (nc, rng.random(), u))
    if not math.isfinite(dist[target]):
        return None
    path = [target]
    while path[-1] != source:
        path.append(parent[path[-1]])
    path.reverse()
    return path


def route_terminals(labels: np.ndarray, terminals: list[int], rng: random.Random) -> p4.CycleSolution | None:
    n = len(terminals)
    width = labels.shape[1]
    segment_ids = list(range(n))
    # Routing long pairs early usually leaves fewer catastrophic late blockages.
    if rng.random() < 0.55:
        segment_ids.sort(key=lambda k: manhattan(terminals[k], terminals[(k + 1) % n], width), reverse=True)
    else:
        rng.shuffle(segment_ids)

    all_terminals = set(terminals)
    used_internal: set[int] = set()
    used_edges: set[tuple[int, int]] = set()
    segments: list[list[int] | None] = [None] * n

    for k in segment_ids:
        a, b = terminals[k], terminals[(k + 1) % n]
        blocked = used_internal | (all_terminals - {a, b})
        # Existing endpoints may only be reused when they are the current endpoints.
        for j, path in enumerate(segments):
            if path is not None:
                for v in (path[0], path[-1]):
                    if v not in (a, b):
                        blocked.add(v)
        path = randomized_path(
            width, a, b, blocked, used_edges, rng,
            noise=rng.choice((0.03, 0.10, 0.30, 0.75, 1.50)),
        )
        if path is None:
            return None
        for u, v in zip(path, path[1:]):
            used_edges.add(tuple(sorted((u, v))))
        used_internal.update(path[1:-1])
        segments[k] = path

    solution = p4.CycleSolution(
        length=sum(len(path) - 1 for path in segments if path is not None),
        chosen=terminals,
        segments=[path for path in segments if path is not None],
    )
    try:
        p4.verify_solution(labels, n, solution)
    except AssertionError:
        return None
    return solution


def heuristic_solve(labels: np.ndarray, n: int, trials: int, rng: random.Random) -> HeuristicResult:
    _, base = terminal_cycle_lower_bound(labels, n)
    best: p4.CycleSolution | None = None
    for _ in range(trials):
        terminals = random_terminals(labels, n, rng, base)
        sol = route_terminals(labels, terminals, rng)
        if sol is not None and (best is None or sol.length < best.length):
            best = sol
    return HeuristicResult(best, trials)


def candidate_record(instance: p4.Instance, index: int, inflation: int, lower: int, sol: p4.CycleSolution | None) -> dict:
    width = inflation * (1 << instance.depth)
    rec = {
        "sample_index": index,
        "tree": p4.tree_notation(instance.tree),
        "tree_tuple_repr": repr(instance.tree),
        "leaf_order_zero_based": list(instance.order),
        "depth": instance.depth,
        "inflation": inflation,
        "grid_width": width,
        "terminal_manhattan_lower_bound": lower,
        "heuristic_feasible": sol is not None,
        "heuristic_taxicab_length": None if sol is None else sol.length,
        "heuristic_normalized_value": None if sol is None else sol.length / width,
        "base_label_grid": instance.base_labels.tolist(),
    }
    if sol is not None:
        rec.update({
            "chosen_xy": [[v % width, v // width] for v in sol.chosen],
            "segments_xy": [
                [[v % width, v // width] for v in segment] for segment in sol.segments
            ],
        })
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260722)
    ap.add_argument("--depth2-trials", type=int, default=40)
    ap.add_argument("--deep-samples", type=int, default=300)
    ap.add_argument("--deep-trials", type=int, default=50)
    ap.add_argument("--exact-top", type=int, default=12)
    ap.add_argument("--exact-time-limit", type=float, default=30.0)
    ap.add_argument("--output", type=Path, default=Path("results/p5_random_search.json"))
    args = ap.parse_args()
    rng = random.Random(args.seed)
    started = time.time()

    depth2 = depth_instances(5, 2)
    deep = random_instances(5, (3, 4), args.deep_samples, rng)
    instances = depth2 + deep
    print(f"[setup] depth2_classes={len(depth2)} deeper_random_classes={len(deep)}")

    records: list[dict] = []
    for idx, instance in enumerate(instances):
        # Search l=1 first. If no cycle is found, search l=2 more heavily.
        labels1 = p4.expand_labels(instance.base_labels, 1)
        lb1, _ = terminal_cycle_lower_bound(labels1, 5)
        h1 = heuristic_solve(labels1, 5, args.depth2_trials if instance.depth == 2 else args.deep_trials, rng)
        records.append(candidate_record(instance, idx, 1, lb1, h1.solution))

        if h1.solution is None:
            labels2 = p4.expand_labels(instance.base_labels, 2)
            lb2, _ = terminal_cycle_lower_bound(labels2, 5)
            h2 = heuristic_solve(labels2, 5, 2 * (args.depth2_trials if instance.depth == 2 else args.deep_trials), rng)
            records.append(candidate_record(instance, idx, 2, lb2, h2.solution))

        if (idx + 1) % 100 == 0 or idx + 1 == len(instances):
            best = max((r["heuristic_normalized_value"] or -1 for r in records), default=-1)
            print(f"[heuristic] {idx+1}/{len(instances)} best_upper_C={best:.4f} elapsed={time.time()-started:.1f}s")

    # Hard-looking candidates: no heuristic l=1 solution, then largest l=2
    # Manhattan lower bound and largest found l=2 route.
    by_index: dict[int, list[dict]] = {}
    for rec in records:
        by_index.setdefault(rec["sample_index"], []).append(rec)
    ranked = []
    for idx, recs in by_index.items():
        r1 = next(r for r in recs if r["inflation"] == 1)
        r2 = next((r for r in recs if r["inflation"] == 2), None)
        if r1["heuristic_feasible"] or r2 is None or not r2["heuristic_feasible"]:
            continue
        score = (r2["terminal_manhattan_lower_bound"], r2["heuristic_taxicab_length"])
        ranked.append((score, idx, r2))
    ranked.sort(reverse=True)

    exact_records = []
    for rank, (_, idx, heuristic_rec) in enumerate(ranked[: args.exact_top], start=1):
        instance = instances[idx]
        print(f"[exact {rank}/{min(args.exact_top,len(ranked))}] index={idx} depth={instance.depth} score={_[0]},{_[1]}")
        labels1 = p4.expand_labels(instance.base_labels, 1)
        try:
            sol1, status1 = p4.solve_fixed_grid(labels1, 5, time_limit=args.exact_time_limit)
        except RuntimeError as exc:
            exact_records.append({"sample_index": idx, "l1_status": "timeout", "error": str(exc)})
            continue
        if sol1 is not None:
            exact_records.append({
                "sample_index": idx,
                "l1_status": status1,
                "exact_record": p4.solution_to_json(instance, 1, sol1),
            })
            continue
        labels2 = p4.expand_labels(instance.base_labels, 2)
        try:
            sol2, status2 = p4.solve_fixed_grid(labels2, 5, time_limit=args.exact_time_limit)
        except RuntimeError as exc:
            exact_records.append({"sample_index": idx, "l1_status": status1, "l2_status": "timeout", "error": str(exc)})
            continue
        exact_records.append({
            "sample_index": idx,
            "l1_status": status1,
            "l2_status": status2,
            "exact_record": None if sol2 is None else p4.solution_to_json(instance, 2, sol2),
        })

    payload = {
        "seed": args.seed,
        "model": "randomized constructive routing followed by exact MILP on selected candidates",
        "warning": "Heuristic route lengths are upper bounds on an instance minimum; only exact_records are certified.",
        "counts": {
            "depth2_symmetry_classes_scanned": len(depth2),
            "random_depth3_depth4_classes_scanned": len(deep),
            "heuristic_records": len(records),
            "exact_candidates_attempted": len(exact_records),
        },
        "heuristic_records": records,
        "exact_records": exact_records,
        "runtime_seconds": time.time() - started,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[done] output={args.output} elapsed={time.time()-started:.1f}s")


if __name__ == "__main__":
    main()
