#!/usr/bin/env python3
"""Simple DH12 search: mutate / mate / anti-mate.

This is deliberately small and readable. It is not the full exploratory
research harness; it is an archival/reproducible search driver for finding
more records from the archived DH12 pools.
"""
import argparse, json, random, importlib.util, hashlib, time
from pathlib import Path
from collections import defaultdict

def load_mechanics(root):
    spec = importlib.util.spec_from_file_location(
        "generic_c6_bootstrap_shot",
        root / "mechanics" / "generic_c6_bootstrap_shot.py",
    )
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    g.BASE = root / "mechanics" / "c6_rephex_catalogues_v2"
    return g

def load_records(path):
    p = Path(path)
    out = []
    if p.is_dir():
        files = list(p.rglob("*.json")) + list(p.rglob("*.jsonl"))
    else:
        files = [p]
    for f in files:
        try:
            if f.suffix == ".jsonl":
                for line in open(f):
                    if line.strip():
                        r = json.loads(line)
                        if isinstance(r, dict) and "output" in r:
                            out.append(r)
            else:
                data = json.load(open(f))
                for r in (data if isinstance(data, list) else [data]):
                    if isinstance(r, dict) and "output" in r:
                        out.append(r)
        except Exception:
            continue
    return out

def maps(rec):
    return (
        {tuple(x["key"]): x["out"] for x in rec.get("output", [])},
        {tuple(x) for x in rec.get("blank_keys", [])},
    )

def freeze_record(model, state, outmap, blank, depth, status, operator):
    output = [{"key": list(k), "out": v} for k, v in sorted(outmap.items())]
    blank_keys = [list(k) for k in sorted(blank)]
    st = [{"q": q, "r": r, "label": lab} for (q, r), lab in sorted(state.items(), key=lambda x: (x[0][1], x[0][0]))]
    h = hashlib.sha1(json.dumps({"o": output, "b": blank_keys}, sort_keys=True).encode()).hexdigest()[:16]
    return {
        "format": "dh12_apex852_search_v1",
        "model": model,
        "operator": operator,
        "cells": len(state),
        "depth": depth,
        "status": status,
        "rule_hash": h,
        "output": output,
        "blank_keys": blank_keys,
        "state": st,
    }

def replay(g, model, outmap, blank, level, max_depth, max_nodes, rng, accept_bias=0.5, mutate_rate=0.0, operator="SEARCH"):
    T = g.target_for(model, level)
    state = {p: T[p] for p in g.SEED}
    depth = 0
    outmap = dict(outmap)
    blank = set(blank)

    while depth < max_depth and len(state) < max_nodes:
        st, data = g.collect_event((state, outmap, frozenset(blank), depth, tuple()), T)
        if st != "BRANCH":
            return freeze_record(model, state, outmap, blank, depth, st, operator)
        sub = []
        for k, info in data["U"].items():
            if k in outmap and rng.random() > mutate_rate:
                sub.append(k)
            elif k in blank and rng.random() > mutate_rate:
                pass
            else:
                if rng.random() < accept_bias:
                    outmap[k] = info["out"]
                    sub.append(k)
                else:
                    blank.add(k)
        ch, err = g.apply_subset((state, outmap, frozenset(blank), depth, tuple()), data, sub)
        if ch is None:
            return freeze_record(model, state, outmap, blank, depth, "DEAD", operator)
        state, _, _, depth, _ = ch

    return freeze_record(model, state, outmap, blank, depth, "DEPTH_OR_NODE_LIMIT", operator)

def make_child(a, b, op, rng, move_count=24):
    ao, ab = maps(a)
    bo, bb = maps(b)
    keys = list(set(ao) | ab | set(bo) | bb)
    rng.shuffle(keys)

    if op == "mutate":
        co, cb = dict(ao), set(ab)
        for k in keys[:move_count]:
            if k in co:
                co.pop(k)
                cb.add(k)
            elif k in cb:
                cb.discard(k)
            else:
                # leave unknown for replay to decide
                pass
        return co, cb

    if op == "mate":
        co, cb = {}, set()
        for k in keys:
            source = (ao, ab) if rng.random() < 0.5 else (bo, bb)
            if k in source[0]:
                co[k] = source[0][k]
            elif k in source[1]:
                cb.add(k)
        return co, cb

    if op == "anti-mate":
        # Start at A and move away from B on differing genes.
        co, cb = dict(ao), set(ab)
        diffs = []
        for k in keys:
            aval = ("accept", ao[k]) if k in ao else ("blank", None) if k in ab else ("unknown", None)
            bval = ("accept", bo[k]) if k in bo else ("blank", None) if k in bb else ("unknown", None)
            if aval != bval:
                diffs.append(k)
        rng.shuffle(diffs)
        for k in diffs[:move_count]:
            if k in bo and k not in ao:
                # B accepts something A does not: push away by blanking it.
                co.pop(k, None)
                cb.add(k)
            elif k in bb and k not in ab:
                # B blanks something A does not: push away by leaving/opening it.
                cb.discard(k)
            elif k in ao:
                # preserve A's allele
                pass
        return co, cb

    raise ValueError(op)

def status_line(i, trials, stats, best):
    parts = []
    for op in ("mutate", "mate", "anti-mate"):
        s = stats[op]
        parts.append(f"{op}:n={s['n']} best={s['best']} ge852={s['ge852']}")
    print(f"[search] trial {i}/{trials} global_best={best} | " + " | ".join(parts), flush=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=Path(__file__).resolve().parents[1], type=Path)
    ap.add_argument("--seeds", default="data/records/pools/pool_852_unique.jsonl")
    ap.add_argument("--outdir", default="runs/search")
    ap.add_argument("--op", choices=["mutate", "mate", "anti-mate", "mixed"], default="mixed")
    ap.add_argument("--trials", type=int, default=100)
    ap.add_argument("--target-level", type=int, default=5)
    ap.add_argument("--max-depth", type=int, default=80)
    ap.add_argument("--max-nodes", type=int, default=12000)
    ap.add_argument("--move-count", type=int, default=32)
    ap.add_argument("--accept-bias", type=float, default=0.65)
    ap.add_argument("--mutate-rate", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=20260609)
    ap.add_argument("--print-every", type=int, default=25)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    root = args.root.resolve()
    g = load_mechanics(root)
    seed_path = root / args.seeds if not Path(args.seeds).is_absolute() else Path(args.seeds)
    seeds = load_records(seed_path)
    if not seeds:
        raise SystemExit(f"no seed records loaded from {seed_path}")

    outdir = Path(args.outdir)
    (outdir / "dh12").mkdir(parents=True, exist_ok=True)

    print(f"[search] loaded {len(seeds)} seed records from {seed_path}", flush=True)
    print(f"[search] methods: {args.op}; trials={args.trials}; target_level={args.target_level}; move_count={args.move_count}", flush=True)

    all_records = []
    ops = ["mutate", "mate", "anti-mate"]
    stats = defaultdict(lambda: {"n": 0, "best": 0, "best_depth": 0, "ge852": 0, "dead": 0})
    t0 = time.time()

    for i in range(1, args.trials + 1):
        op = rng.choice(ops) if args.op == "mixed" else args.op
        a, b = rng.sample(seeds, 2) if len(seeds) > 1 else (seeds[0], seeds[0])
        co, cb = make_child(a, b, op, rng, args.move_count)
        rec = replay(
            g, "dh12", co, cb, args.target_level, args.max_depth, args.max_nodes,
            rng, args.accept_bias, args.mutate_rate, operator="SEARCH_" + op.upper()
        )
        rec["trial"] = i
        all_records.append(rec)

        s = stats[op]
        s["n"] += 1
        if rec["cells"] > s["best"] or (rec["cells"] == s["best"] and rec["depth"] > s["best_depth"]):
            s["best"] = rec["cells"]
            s["best_depth"] = rec["depth"]
        if rec["cells"] >= 852:
            s["ge852"] += 1
            json.dump(rec, open(outdir / "dh12" / f"rank{i:04d}_{rec['operator']}_{rec['status'].lower()}_{rec['cells']:05d}_{rec['rule_hash']}.json", "w"), indent=2)
        if rec["status"] == "DEAD":
            s["dead"] += 1

        if i == 1 or i % args.print_every == 0 or i == args.trials:
            best = max(r["cells"] for r in all_records)
            status_line(i, args.trials, stats, best)

    top = sorted(all_records, key=lambda r: (r["cells"], r["depth"]), reverse=True)[:50]
    json.dump(top, open(outdir / "dh12" / "top_clean.json", "w"), indent=2)

    summary = {
        "trials": args.trials,
        "best_cells": top[0]["cells"],
        "best_depth": top[0]["depth"],
        "best_hash": top[0]["rule_hash"],
        "records_ge_852": sum(r["cells"] >= 852 for r in all_records),
        "seconds": round(time.time() - t0, 3),
        "by_method": dict(stats),
    }
    json.dump(summary, open(outdir / "summary.json", "w"), indent=2)
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
