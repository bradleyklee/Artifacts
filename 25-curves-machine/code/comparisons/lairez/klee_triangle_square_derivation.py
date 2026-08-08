#!/usr/bin/env python3
"""Lean from-scratch triangle-square exact-image derivation benchmark.

This invokes Klee's support-driven Cartesian reduction without loading a
candidate operator or stored certificate and verifies the returned primitive
identity.  It deliberately omits the large human-audit JSON trace.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pair_root", type=Path)
    ap.add_argument("--family", choices=("triangle_square", "square_only", "hexagon_only"),
                    default="triangle_square")
    ap.add_argument("--search", action="store_true",
                    help="exhaust bounded order 1 before deriving order 2")
    ap.add_argument("--weight-bound", type=int, default=29)
    ap.add_argument("--case-json", type=Path)
    ap.add_argument("--q-degree", type=int)
    ap.add_argument("--json-output", type=Path)
    ns = ap.parse_args()
    src = ns.pair_root / "replay" / "triangle_square" / "src"
    sys.path.insert(0, str(src.resolve()))
    from cartesian_cohomology_reduction import (  # type: ignore
        Qalpha, common_derivative_numerators, derive_relation,
        exact_image_map, primitive_polynomial_operator,
        search_first_relation, sparse_from_qalpha_coefficients,
        to_qalpha_rows, triangle_square_energy, verify_identity,
    )
    from polynomial_hamiltonian_to_ode import (  # type: ignore
        add, mono, mul, make_hamiltonian,
    )
    import sympy as sp
    from sympy import QQ
    from sympy.polys.matrices import DomainMatrix

    terms = {
        "square_only": [{"degree": 4, "mode": 4, "coefficient": "1/4"}],
        "hexagon_only": [{"degree": 6, "mode": 6, "coefficient": "1/4"}],
    }
    if ns.case_json:
        case = json.loads(ns.case_json.read_text())
        family_name = case["name"]
        if "harmonic_terms" in case:
            energy = make_hamiltonian(case["harmonic_terms"])
        else:
            p, q = sp.symbols("p q")
            expr = sp.Poly(sp.sympify(case["energy_E_equals_2H"].replace("^", "**"),
                                      locals={"p": p, "q": q}), p, q,
                           domain=sp.QQ)
            energy = {(0, pm, qm): F(int(c.p), int(c.q))
                      for (pm, qm), c in expr.terms()}
        cfg = case["klee_config"]
        order = int(cfg["order"])
        q_degree = int(cfg.get("q_degree", 0))
        p_degrees = tuple(cfg["p_degrees"])
        support = cfg["support"]
        weight_bound = int(cfg.get("weight_bound", ns.weight_bound))
    else:
        family_name = ns.family
        energy = (triangle_square_energy() if ns.family == "triangle_square"
                  else make_hamiltonian(terms[ns.family]))
        order, q_degree, p_degrees = {
        "triangle_square": (2, 9, (0, 2)),
        "square_only": (2, 9, (0, 2)),
        "hexagon_only": (4, 29, (0, 2, 4)),
        }[ns.family]
        support = ("even_p_odd_q_weighted" if ns.family == "hexagon_only"
                   else "rectangular")
        weight_bound = ns.weight_bound
    if ns.q_degree is not None:
        q_degree = ns.q_degree
    start = time.perf_counter()
    weighted = support == "even_p_odd_q_weighted" and not ns.search
    if weighted:
        # The even-p/even-q energy forces the primitive into the even-p/odd-q
        # sector.  This is the same finite weighted support used successfully
        # in the square-hexagon derivation, not an operator-dependent support.
        bound = weight_bound
        image = exact_image_map(energy, order)
        labels = [(p, q) for p in p_degrees
                  for q in range(1, bound - p + 1, 2)]
        ccols = [to_qalpha_rows(image(mono(0, p, q))) for p, q in labels]
        wpolys = common_derivative_numerators(energy, order)
        wcols = [to_qalpha_rows(w) for w in wpolys]
        rows = sorted(set().union(*(c.keys() for c in ccols + wcols)))
        C = DomainMatrix.from_list(
            [[c.get(row, Qalpha.zero) for c in ccols] for row in rows], Qalpha)
        W = DomainMatrix.from_list(
            [[c.get(row, Qalpha.zero) for c in wcols] for row in rows], Qalpha)
        B = DomainMatrix.hstack(C, W).nullspace().to_Matrix()
        good = [list(B.row(i)) for i in range(B.rows)
                if any(sp.simplify(x) != 0 for x in list(B.row(i))[len(labels):])]
        if not good:
            relation = None
        else:
            row = good[0]
            highest = next(x for x in reversed(row[len(labels):])
                           if sp.simplify(x) != 0)
            row = [sp.factor(x / highest) for x in row]
            rational = row[len(labels):]
            operator, scale = primitive_polynomial_operator(rational)
            coeffs = {label: sp.factor(-scale*x)
                      for label, x in zip(labels, row[:len(labels)]) if x != 0}
            primitive = sparse_from_qalpha_coefficients(coeffs)
            lhs = {}
            alpha = sp.symbols("alpha")
            for poly, w in zip(operator, wpolys):
                pp = sp.Poly(poly, alpha, domain=QQ)
                ps = {(a, 0, 0): F(int(c.p), int(c.q))
                      for (a,), c in pp.terms()}
                lhs = add(lhs, mul(ps, w))
            if add(image(primitive), lhs, F(-1)):
                raise AssertionError("weighted exact identity failed")
            relation = {
                "order": order, "operator": operator,
                "primitive": primitive, "rows": len(rows),
                "columns": len(labels), "rank": len(C.transpose().rref()[1]),
                "quotient_dimension": len(rows)-len(C.transpose().rref()[1]),
            }
        log = []
    elif ns.search:
        relation, log = search_first_relation(
            energy, max_order=order,
            max_q_degree_by_order={j: q_degree for j in range(1, order + 1)},
            p_degrees=p_degrees, monomial_order="high_q_first",
        )
    else:
        relation = derive_relation(
            energy, order=order, primitive_q_degree=q_degree,
            p_degrees=p_degrees, monomial_order="high_q_first",
        )
        log = []
    derive_seconds = time.perf_counter() - start
    if relation is None:
        raise RuntimeError(f"no {family_name} relation found within configured support")
    verify_start = time.perf_counter()
    if not weighted:
        verify_identity(energy, relation)
    verify_seconds = time.perf_counter() - verify_start
    operator = relation["operator"] if weighted else relation.polynomial_operator
    primitive = relation["primitive"] if weighted else relation.primitive_numerator
    result = {
        "case": family_name,
        "method": "Klee support-driven Cartesian exact image",
        "search_mode": "bounded_order_first" if ns.search else "fixed_order_and_support",
        "order": relation["order"] if weighted else relation.order,
        "operator": [str(x) for x in operator],
        "primitive_terms": len(primitive),
        "matrix_rows": relation["rows"] if weighted else relation.row_count,
        "exact_columns": relation["columns"] if weighted else relation.exact_column_count,
        "exact_rank": relation["rank"] if weighted else relation.exact_rank,
        "quotient_dimension": (relation["quotient_dimension"] if weighted
                               else relation.quotient_dimension),
        "derive_seconds": derive_seconds,
        "verify_seconds": verify_seconds,
        "total_seconds": derive_seconds + verify_seconds,
        "search_attempts": log,
        "identity_verified": True,
    }
    rendered = json.dumps(result, indent=2)
    if ns.json_output:
        ns.json_output.write_text(rendered + "\n")
    print(rendered)


if __name__ == "__main__":
    main()
