#!/usr/bin/env python3
"""
Replay verifier for the Apex 852 reduced finite-certificate payload.

Input: apex852_pdf_payload_v88_reduced_certificate.json or compatible payload.
This script uses only the JSON certificate fields: seed_axiom, accept_rules,
reject_rules, and the declared visual-frame C6 canonicalization. It does not
read PDF embedded files, SVG geometry, or PNGs.

It checks that the certificate grows to a closed finite state of 852 placed
cells with zero unknown frontier and the expected growth counts.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

DIRS_AXIAL = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
BLOCKED = {(0, 0)}

def parse_coord(s: str) -> tuple[int, int]:
    q, r = s.split(",")
    return int(q), int(r)

def split_key(s: str) -> tuple[str, ...]:
    return tuple(s.split("|"))

def plus_state(st: str, k: int) -> str:
    if st == "*":
        return "*"
    typ, idx = st.split(".")
    return f"{typ}.{(int(idx) + k) % 6}"

def plus_inv_state(st: str, k: int) -> str:
    if st == "*":
        return "*"
    typ, idx = st.split(".")
    return f"{typ}.{(int(idx) - k) % 6}"

def plus_key(raw: tuple[str, ...], k: int) -> tuple[str, ...]:
    out = ["*"] * 6
    for p, st in enumerate(raw):
        out[(p + k) % 6] = plus_state(st, k)
    return tuple(out)

def plus_canon(raw: tuple[str, ...]) -> tuple[tuple[str, ...], int]:
    cands = [plus_key(tuple(raw), k) for k in range(6)]
    best = min(cands)
    return best, cands.index(best)

def frontier(state: dict[tuple[int, int], str]) -> set[tuple[int, int]]:
    out: set[tuple[int, int]] = set()
    for q, r in state:
        for dq, dr in DIRS_AXIAL:
            c = (q + dq, r + dr)
            if c not in state and c not in BLOCKED:
                out.add(c)
    return out

def replay(payload: dict, max_steps: int = 1000):
    state = {parse_coord(k): v for k, v in payload["seed_axiom"].items()}
    accept = {split_key(r["canonical_neighbor_key"]): r["output"] for r in payload["accept_rules"]}
    reject = {split_key(r["canonical_neighbor_key"]) for r in payload["reject_rules"]}
    history = []
    unknown = []
    used_accept = set()
    used_reject = set()

    for t in range(max_steps):
        births: dict[tuple[int, int], str] = {}
        unknown = []
        rejected_frontier = 0
        for q, r in sorted(frontier(state)):
            raw = tuple(state.get((q + dq, r + dr), "*") for dq, dr in DIRS_AXIAL)
            key, k = plus_canon(raw)
            if key in accept:
                births[(q, r)] = plus_inv_state(accept[key], k)
                used_accept.add(key)
            elif key in reject:
                rejected_frontier += 1
                used_reject.add(key)
            else:
                unknown.append({
                    "cell": [q, r],
                    "raw_key": list(raw),
                    "canonical_key": list(key),
                    "rotation_k": k,
                })
        history.append({
            "t": t,
            "births": len(births),
            "placed": len(state) + len(births),
            "rejected_frontier": rejected_frontier,
            "unknown_frontier": len(unknown),
        })
        if not births:
            return state, history, unknown, used_accept, used_reject
        state.update(births)
    raise RuntimeError(f"max_steps exceeded: {max_steps}")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("payload", type=Path)
    ap.add_argument("--json", action="store_true", help="print machine-readable report")
    ns = ap.parse_args()
    payload = json.loads(ns.payload.read_text())
    state, history, unknown, used_accept, used_reject = replay(payload)
    expected = payload.get("verification", {})
    growth = payload.get("growth_counts", {})

    a_sequence = [h["placed"] // 6 for h in history[:-1]]
    # Include seed as a_0. h[0] is after first frontier evaluation and first births are already counted.
    # In this replay convention, the stored history rows are after attempted step t; placed includes births.
    # The payload sequence is seed followed by successful-birth steps.
    reconstructed_a = [len(payload["seed_axiom"]) // 6] + [h["placed"] // 6 for h in history if h["births"] > 0]
    diffs = [b - a for a, b in zip(reconstructed_a, reconstructed_a[1:])]

    report = {
        "payload": str(ns.payload),
        "final_cells": len(state),
        "terminal_step": history[-1]["t"],
        "terminal_births": history[-1]["births"],
        "terminal_unknown_frontier": history[-1]["unknown_frontier"],
        "used_accept_rules": len(used_accept),
        "used_reject_rules": len(used_reject),
        "a_sequence_matches_payload": reconstructed_a == growth.get("a_sequence"),
        "first_differences_matches_payload": diffs == growth.get("first_differences"),
        "matches_declared_verification": {
            "final_cells_is_852": len(state) == 852,
            "terminal_step": history[-1]["t"] == expected.get("terminal_step"),
            "terminal_births": history[-1]["births"] == expected.get("terminal_births"),
            "terminal_unknown_frontier": history[-1]["unknown_frontier"] == expected.get("terminal_unknown_frontier"),
            "used_accept_outputs": len(used_accept) == expected.get("used_accept_outputs"),
            "used_reject_rules": len(used_reject) == expected.get("used_reject_rules"),
        },
        "unknown_sample": unknown[:5],
    }
    ok = all(report["matches_declared_verification"].values()) and report["a_sequence_matches_payload"] and report["first_differences_matches_payload"]
    report["ok"] = ok

    if ns.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"payload: {ns.payload}")
        print(f"final_cells: {report['final_cells']}")
        print(f"terminal_step: {report['terminal_step']}")
        print(f"terminal_births: {report['terminal_births']}")
        print(f"terminal_unknown_frontier: {report['terminal_unknown_frontier']}")
        print(f"used_accept_rules: {report['used_accept_rules']}")
        print(f"used_reject_rules: {report['used_reject_rules']}")
        print(f"a_sequence_matches_payload: {report['a_sequence_matches_payload']}")
        print(f"first_differences_matches_payload: {report['first_differences_matches_payload']}")
        print(f"OK: {ok}")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
