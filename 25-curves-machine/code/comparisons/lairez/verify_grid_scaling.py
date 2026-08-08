#!/usr/bin/env python3
"""Verify exact radial-scaling equivalence for duplicate tau grid points."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp

from lairez_port import primitive_polynomial_relation


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("grid_result", type=Path)
    ap.add_argument("case_directory", type=Path)
    ns = ap.parse_args()
    alpha = sp.symbols("alpha")
    data = json.loads(ns.grid_result.read_text())
    groups = {}
    for row in data["results"]:
        case = json.loads((ns.case_directory/f"{row['case']}.json").read_text())
        tau = case["scaling_invariant_tau_equals_c3_squared_over_c4"]
        terms = {t["degree"]:Fraction(t["coefficient"])
                 for t in case["harmonic_terms"]}
        operator = [sp.sympify(x, locals={"alpha":alpha})
                    for x in row["lairez"]["parsed"]["operator"]]
        groups.setdefault(tau, []).append((row["case"], terms, operator))
    checks = []
    for tau, members in sorted(groups.items(), key=lambda x: Fraction(x[0])):
        if len(members) < 2:
            continue
        name_a, terms_a, op_a = members[0]
        for name_b, terms_b, op_b in members[1:]:
            scale = sp.Rational(terms_b[3].numerator, terms_b[3].denominator) / \
                    sp.Rational(terms_a[3].numerator, terms_a[3].denominator)
            if terms_b[4] != terms_a[4]*Fraction(scale**2):
                raise AssertionError("tau pair failed coefficient scaling")
            transformed = [sp.factor(P.subs(alpha, scale**2*alpha)/scale**(2*j))
                           for j, P in enumerate(op_a)]
            lhs = primitive_polynomial_relation(transformed)
            rhs = primitive_polynomial_relation(op_b)
            equal = all(sp.expand(x-y) == 0 for x, y in zip(lhs, rhs))
            if not equal:
                raise AssertionError((name_a, name_b, "operator scaling mismatch"))
            checks.append({"tau":tau,"source":name_a,"target":name_b,
                           "radial_scale":str(scale),"operators_equal":True})
    print(json.dumps({"schema":"quartic-scaling-equivalence-v1",
                      "checks":checks}, indent=2))


if __name__ == "__main__":
    main()
