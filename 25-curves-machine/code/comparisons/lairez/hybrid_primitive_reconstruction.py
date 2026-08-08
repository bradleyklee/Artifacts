#!/usr/bin/env python3
"""Reconstruct a Klee curve primitive from a supplied Lairez operator.

This is intentionally a bridge, not an algorithm merger: operator discovery
and support-driven certificate reconstruction remain independently timed.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path


OPERATORS = {
    "square_only": [
        "3*alpha", "4*(3*alpha**2-1)", "4*alpha*(alpha-1)*(alpha+1)"],
    "triangle_square": [
        "3*(136*alpha**3+215*alpha**2-87*alpha+9)",
        "1632*alpha**4+5736*alpha**3-2827*alpha**2+426*alpha-18",
        "alpha*(alpha+6)*(4*alpha-1)*(8*alpha-1)*(17*alpha-3)"],
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pair_root", type=Path)
    ap.add_argument("--family", choices=tuple(OPERATORS), default="triangle_square")
    ns = ap.parse_args()
    src = ns.pair_root / "replay" / "triangle_square" / "src"
    sys.path.insert(0, str(src.resolve()))

    import sympy as sp
    from sympy.polys.matrices import DomainMatrix
    from cartesian_cohomology_reduction import (  # type: ignore
        Qalpha, common_derivative_numerators, exact_image_map,
        sparse_from_qalpha_coefficients, to_qalpha_rows, triangle_square_energy,
    )
    from polynomial_hamiltonian_to_ode import add, mono, mul, make_hamiltonian  # type: ignore

    alpha = sp.symbols("alpha")
    energy = (triangle_square_energy() if ns.family == "triangle_square" else
              make_hamiltonian([{"degree":4,"mode":4,"coefficient":"1/4"}]))
    p_degrees, q_degree = (0, 2), 9
    operator = [sp.sympify(x, locals={"alpha": alpha}) for x in OPERATORS[ns.family]]
    order = len(operator)-1

    start = time.perf_counter()
    image = exact_image_map(energy, order)
    labels = [(p, q) for p in p_degrees for q in range(q_degree+1)]
    ccols = [to_qalpha_rows(image(mono(0, p, q))) for p, q in labels]
    wpolys = common_derivative_numerators(energy, order)
    wcols = [to_qalpha_rows(w) for w in wpolys]
    rows = sorted(set().union(*(c.keys() for c in ccols+wcols)))
    C = DomainMatrix.from_list(
        [[c.get(row, Qalpha.zero) for c in ccols] for row in rows], Qalpha)
    W = DomainMatrix.from_list(
        [[c.get(row, Qalpha.zero) for c in wcols] for row in rows], Qalpha)
    P = DomainMatrix.from_list([[Qalpha.from_sympy(x)] for x in operator], Qalpha)
    rhs = W*P
    _, pivots = C.transpose().rref()
    pivots = list(pivots)
    Cp = C.extract(pivots, list(range(C.shape[1])))
    rp = rhs.extract(pivots, [0])
    x = -(Cp.inv()*rp)
    matrix_residual = (C*x + rhs).to_Matrix()
    if any(value != 0 for value in matrix_residual):
        raise AssertionError("supplied operator is outside the exact image")
    coeffs = {label: sp.factor(-value.as_expr())
              for label, value in zip(labels, x.to_list_flat()) if value}
    primitive = sparse_from_qalpha_coefficients(coeffs)
    build_seconds = time.perf_counter()-start

    verify_start = time.perf_counter()
    lhs = {}
    for poly, w in zip(operator, wpolys):
        pp = sp.Poly(poly, alpha, domain=sp.QQ)
        ps = {(a,0,0): F(int(c.p), int(c.q)) for (a,), c in pp.terms()}
        lhs = add(lhs, mul(ps, w))
    residual = add(image(primitive), lhs, F(-1))
    if residual:
        raise AssertionError("nonzero curve-certificate residual")
    verify_seconds = time.perf_counter()-verify_start
    stored_equal = None
    if ns.family == "triangle_square":
        stored = json.loads((ns.pair_root / "examples" / "triangle_square" /
                             "primitive.json").read_text())
        expected = {}
        for block in stored["nonzero_coefficient_blocks"]:
            poly = sp.Poly(sp.sympify(block["coefficient"],
                                     locals={"alpha": alpha}), alpha, domain=sp.QQ)
            for (a,), c in poly.terms():
                expected[(a, block["p"], block["q"])] = F(int(c.p), int(c.q))
        stored_equal = primitive == expected
        if not stored_equal:
            raise AssertionError("hybrid primitive differs from stored Klee primitive")
    print(json.dumps({
        "case": ns.family,
        "source_operator": "Pierre Lairez-style port normalized output",
        "reconstructor": "Klee support-driven exact image",
        "order": order,
        "matrix_shape": list(C.shape),
        "primitive_terms": len(primitive),
        "reconstruction_seconds": build_seconds,
        "verification_seconds": verify_seconds,
        "total_seconds": build_seconds+verify_seconds,
        "identity_verified": True,
        "stored_klee_primitive_equal": stored_equal,
    }, indent=2))


if __name__ == "__main__":
    main()
