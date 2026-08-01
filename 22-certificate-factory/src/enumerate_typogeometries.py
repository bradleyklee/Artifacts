#!/usr/bin/env python3
"""Explicitly enumerate the verified finite-color Delta-word models."""

from __future__ import annotations

import json
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import comb
from pathlib import Path

from expand_target_coverage import CORE, DESC, POWERS

MAX_LEAVES = 3


def compositions(total: int, parts: int):
    if parts == 1:
        if total >= 1:
            yield (total,)
        return
    for first in range(1, total - parts + 2):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def tree_factory(coefficients: dict[int, int], marked: int = 0):
    @lru_cache(None)
    def trees(n: int) -> tuple[str, ...]:
        out = ["l"] if n == 1 else []
        if marked and n >= 2:
            for child in trees(n - 1):
                for color in range(marked):
                    out.append(f"Delta_2m[{color}](l,{child})")
        for arity, colors in coefficients.items():
            if n < arity:
                continue
            for profile in compositions(n, arity):
                child_sets = [trees(size) for size in profile]
                for children in product(*child_sets):
                    body = ",".join(children)
                    for color in range(colors):
                        out.append(f"Delta_{arity}[{color}]({body})")
        assert len(out) == len(set(out))
        return tuple(out)
    return trees


def colored_roots(trees, d: int, n: int) -> list[str]:
    return [f"root[{color}]({tree})" for color in range(d) for tree in trees(n)]


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    examples = root / "examples"
    summaries = {}
    parent_objects = {}

    for case_id, (q, r, b, _) in CORE.items():
        d = Fraction(b, r - q)
        assert d.denominator == 1
        coefficients = {
            k: int(Fraction(comb(q, k) * d**k, b))
            for k in range(2, q + 1)
        }
        trees = tree_factory(coefficients)
        by_n = {str(n): colored_roots(trees, int(d), n) for n in range(1, MAX_LEAVES + 1)}
        terms = json.loads((examples / case_id / "data/terms.json").read_text())["terms"]
        checks = {str(n): {"enumerated": len(by_n[str(n)]), "published_term": terms[n], "pass": len(by_n[str(n)]) == terms[n]} for n in range(1, MAX_LEAVES + 1)}
        assert all(v["pass"] for v in checks.values())
        dump(examples / case_id / "data/set_elements_n_le_3.json", {
            "status": "verified",
            "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
            "maximum_true_leaves": MAX_LEAVES,
            "elements_by_true_leaf_count": by_n,
            "checks": checks,
        })
        parent_objects[case_id] = by_n
        summaries[case_id] = checks

    for case_id, (parent, power, _) in POWERS.items():
        parent_by_n = parent_objects[parent]
        units = {0: ("false",)}
        for n in range(1, MAX_LEAVES + 1):
            units[n] = tuple(parent_by_n[str(n)])
        by_n = {}
        for n in range(1, MAX_LEAVES + 1):
            objects = []
            # Weak compositions allow unit/false forest components.
            def weak(total, parts):
                if parts == 1:
                    yield (total,)
                else:
                    for first in range(total + 1):
                        for rest in weak(total - first, parts - 1):
                            yield (first,) + rest
            for profile in weak(n, power):
                for children in product(*(units[size] for size in profile)):
                    objects.append(f"Delta_{power}F(" + ",".join(children) + ")")
            by_n[str(n)] = objects
        terms = json.loads((examples / case_id / "data/terms.json").read_text())["terms"]
        checks = {str(n): {"enumerated": len(by_n[str(n)]), "published_term": terms[n], "pass": len(by_n[str(n)]) == terms[n]} for n in range(1, MAX_LEAVES + 1)}
        assert all(v["pass"] for v in checks.values())
        dump(examples / case_id / "data/set_elements_n_le_3.json", {
            "status": "verified",
            "encoding": f"ordered {power}-forest; false is the unit parent object",
            "maximum_true_leaves": MAX_LEAVES,
            "elements_by_true_leaf_count": by_n,
            "checks": checks,
        })
        summaries[case_id] = checks

    for case_id, (q, r, s, _) in DESC.items():
        d = Fraction(s, r - q)
        assert d.denominator == 1
        coefficients = {
            k: int(Fraction(comb(q, k) * d**k, s))
            for k in range(2, q + 1)
        }
        trees = tree_factory(coefficients, marked=int(d))
        by_n = {str(n): colored_roots(trees, int(d), n) for n in range(1, MAX_LEAVES + 1)}
        terms = json.loads((examples / case_id / "data/terms.json").read_text())["terms"]
        checks = {str(n): {"enumerated": len(by_n[str(n)]), "published_term": terms[n], "pass": len(by_n[str(n)]) == terms[n]} for n in range(1, MAX_LEAVES + 1)}
        assert all(v["pass"] for v in checks.values())
        dump(examples / case_id / "data/set_elements_n_le_3.json", {
            "status": "verified",
            "encoding": "prefix depth-first Delta word; Delta_2m(l,T) is the marked binary x*T constructor",
            "maximum_true_leaves": MAX_LEAVES,
            "elements_by_true_leaf_count": by_n,
            "checks": checks,
        })
        summaries[case_id] = checks

    dump(root / "reports/explicit_set_enumeration.json", {
        "status": "verified",
        "case_count": len(summaries),
        "maximum_true_leaves": MAX_LEAVES,
        "published_term_comparisons": 3 * len(summaries),
        "checks": summaries,
    })
    for case_id in summaries:
        manifest_path = examples / case_id / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["components"]["explicit_set_elements"] = {
            "status": "verified",
            "canonical_path": "data/set_elements_n_le_3.json",
        }
        dump(manifest_path, manifest)
    print(json.dumps({"cases": len(summaries), "published_term_comparisons": 3 * len(summaries)}))


if __name__ == "__main__":
    main()
