#!/usr/bin/env python3
"""Replay the merged square+hexagon order-four differential certificate."""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import json, sys
import sympy as sp
from sympy.polys.matrices import DomainMatrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "src"))
from polynomial_hamiltonian_to_ode import mono, add, mul
from cartesian_cohomology_reduction import (
    exact_image_map, common_derivative_numerators, to_qalpha_rows,
    Qalpha, alpha,
)

ENERGY = {
    (0, 2, 0): F(1), (0, 0, 2): F(1), (0, 2, 2): F(-2),
    (0, 6, 0): F(1, 4), (0, 4, 2): F(-3, 2), (0, 2, 4): F(9, 4),
}


def operator_polynomials(payload):
    order = payload["order"]
    degree = payload["degree_bound"]
    vector = [int(x) for x in payload["vector"]]
    out = []
    for j in range(order + 1):
        P = {}
        for k in range(degree + 1):
            c = vector[j * (degree + 1) + k]
            if c:
                P[(k, 0, 0)] = F(c)
        out.append(P)
    return out


def xi_sparse(payload):
    out = {}
    for item in payload["coefficients"]:
        p, q = item["p"], item["q"]
        poly = sp.Poly(sp.sympify(item["coefficient"]), alpha, domain=sp.QQ)
        for (a,), c in poly.terms():
            if c:
                out[(a, p, q)] = F(int(c.p), int(c.q))
    return out


def matrices(image, target, q_bound):
    labels = [(p, q) for q in range(1, q_bound + 1, 2) for p in (0, 2, 4)]
    columns = [to_qalpha_rows(image(mono(0, p, q))) for p, q in labels]
    t = to_qalpha_rows(target)
    rows = sorted(set(t).union(*(c.keys() for c in columns)))
    C = DomainMatrix.from_list(
        [[c.get(row, Qalpha.zero) for c in columns] for row in rows], Qalpha
    )
    T = DomainMatrix.from_list([[t.get(row, Qalpha.zero)] for row in rows], Qalpha)
    return C, T


def main():
    op = json.loads((HERE / "order4_operator.json").read_text())
    xi = json.loads((HERE / "order4_xi.json").read_text())
    order = op["order"]
    image = exact_image_map(ENERGY, order)
    W = common_derivative_numerators(ENERGY, order)

    target = {}
    for P, w in zip(operator_polynomials(op), W):
        target = add(target, mul(P, w))

    C25, T25 = matrices(image, target, 25)
    C27, T27 = matrices(image, target, 27)
    rC25, rA25 = C25.rank(), DomainMatrix.hstack(C25, T25).rank()
    rC27, rA27 = C27.rank(), DomainMatrix.hstack(C27, T27).rank()
    assert (rC25, rA25) == (39, 40)
    assert (rC27, rA27) == (42, 42)

    V = xi_sparse(xi)
    residual = add(image(V), target, F(-1))
    assert not residual

    print("MERGED_CERTIFICATE_PASS")
    print("q_bound_25 ranks:", rC25, rA25, "(not in exact-image span)")
    print("q_bound_27 ranks:", rC27, rA27, "(in exact-image span)")
    print("matrix at closure: 55 rows x 42 primitive columns")
    print("rho=(2H)_p=2H_p; omega=dq/H_p=2*dq/rho")
    print("Xi = V/rho^7, nonzero slots: 40, expanded terms: 514")
    print("exact reduced residual: zero")


if __name__ == "__main__":
    main()
