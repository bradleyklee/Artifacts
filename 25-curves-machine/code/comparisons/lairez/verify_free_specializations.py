#!/usr/bin/env python3
"""Verify the universal c1,c2 operator against exact specializations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp

from lairez_port import primitive_polynomial_relation


def normalized(expressions):
    return [sp.factor(x) for x in primitive_polynomial_relation(expressions)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("symbolic_result", type=Path)
    ns = ap.parse_args()
    data = json.loads(ns.symbolic_result.read_text())
    alpha, c1, c2 = sp.symbols("alpha c1 c2")
    symbolic = [sp.sympify(x, locals={"alpha":alpha,"c1":c1,"c2":c2})
                for x in data["operator"]]
    must_have = normalized([
        3*alpha*(9*alpha-16),
        216*alpha**3-195*alpha**2-28*alpha+8,
        alpha*(3*alpha-2)*(4*alpha-1)*(9*alpha+4),
    ])
    specialized = normalized([x.subs({c1:1,c2:sp.Rational(1,4)}) for x in symbolic])
    if specialized != must_have:
        raise AssertionError("universal operator does not specialize to must-have operator")
    # Scaling covariance: p,q -> s(p,q) changes c1 -> s*c1,
    # c2 -> s^2*c2 and alpha -> s^2*alpha after restoring the quadratic term.
    # Record invariant values used by the numeric grid for later interpolation.
    probes = [{"c1":"1","c2":"1/4"},
              {"c1":"1/2","c2":"1/8"},
              {"c1":"2","c2":"1/2"}]
    print(json.dumps({"symbolic_order":data["order"],
                      "must_have_specialization_equal":True,
                      "planned_exact_probes":probes}, indent=2))


if __name__ == "__main__":
    main()
