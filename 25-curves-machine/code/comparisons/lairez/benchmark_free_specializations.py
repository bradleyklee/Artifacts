#!/usr/bin/env python3
"""Fresh exact numeric checks of the universal free-coefficient operator."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import sympy as sp

from lairez_port import PlaneGriffithsDwork, primitive_polynomial_relation


POINTS = [(sp.Rational(1), sp.Rational(1,4)),
          (sp.Rational(1,2), sp.Rational(1,8)),
          (sp.Rational(2), sp.Rational(1,2))]


def norm(op):
    return [sp.factor(x) for x in primitive_polynomial_relation(op)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("symbolic_result", type=Path)
    ap.add_argument("--output", type=Path)
    ns = ap.parse_args()
    alpha, p, q, c1, c2 = sp.symbols("alpha p q c1 c2")
    source = json.loads(ns.symbolic_result.read_text())
    universal = [sp.sympify(x, locals={"alpha":alpha,"c1":c1,"c2":c2})
                 for x in source["operator"]]
    rows = []
    for u, v in POINTS:
        energy = p**2+q**2+u*(q**3-3*p**2*q)+v*(q**2-3*p**2)**2
        start = time.perf_counter()
        gd = PlaneGriffithsDwork(energy)
        setup = time.perf_counter()-start
        classes, keys, matrix, relation = gd.first_relation(max_order=2)
        if relation is None:
            raise AssertionError((u, v, "no numeric relation"))
        numeric = norm(list(relation))
        specialized = norm([x.subs({c1:u,c2:v}) for x in universal])
        equal = numeric == specialized
        if not equal:
            raise AssertionError((u, v, "operator mismatch"))
        rows.append({"c1":str(u),"c2":str(v),"order":len(numeric)-1,
                     "operator":[str(x) for x in numeric],
                     "setup_seconds":setup,
                     "total_seconds":time.perf_counter()-start,
                     "symbolic_specialization_equal":equal,
                     "profile_stats":gd.profile_stats})
    result = {"schema":"free-coefficient-specializations-v1","results":rows}
    if ns.output:
        ns.output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
