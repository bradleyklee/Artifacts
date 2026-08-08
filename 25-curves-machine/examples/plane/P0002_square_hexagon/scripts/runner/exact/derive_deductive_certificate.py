#!/usr/bin/env python3
"""Derive the square-hexagon order-four certificate from exact reduction.

No period coefficients and no supplied operator are used to obtain the
relation.  The stored operator/primitive are loaded only at the end for exact
comparison with the independently derived result.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import json, sys
import sympy as sp
from sympy import QQ
from sympy.polys.matrices import DomainMatrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "src"))
from polynomial_hamiltonian_to_ode import mono
from cartesian_cohomology_reduction import (
    exact_image_map, common_derivative_numerators, to_qalpha_rows,
    primitive_polynomial_operator, Qalpha, alpha,
)

ENERGY = {
    (0, 2, 0): F(1), (0, 0, 2): F(1), (0, 2, 2): F(-2),
    (0, 6, 0): F(1, 4), (0, 4, 2): F(-3, 2), (0, 2, 4): F(9, 4),
}


def exact_matrices(order: int, labels: list[tuple[int, int]]):
    image = exact_image_map(ENERGY, order)
    Ccols = [to_qalpha_rows(image(mono(0, p, q))) for p, q in labels]
    Wcols = [to_qalpha_rows(w) for w in common_derivative_numerators(ENERGY, order)]
    rows = sorted(set().union(*(Ccols + Wcols)))
    C = DomainMatrix.from_list(
        [[c.get(row, Qalpha.zero) for c in Ccols] for row in rows], Qalpha
    )
    W = DomainMatrix.from_list(
        [[c.get(row, Qalpha.zero) for c in Wcols] for row in rows], Qalpha
    )
    return rows, C, W


def exhaustive_labels(order: int) -> list[tuple[int, int]]:
    # The symbol-at-infinity minor proves p+q <= 8r-3 is exhaustive.
    bound = 8 * order - 3
    return [
        (p, q) for p in (0, 2, 4)
        for q in range(1, bound - p + 1, 2)
    ]


def derive_order4():
    # This sector contains the unique relation and gives a fast fraction-free
    # normal form.  The later exhaustive rank check proves no relation is missed.
    labels = [(p, q) for q in range(1, 28, 2) for p in (0, 2, 4)]
    rows, Cfield, Wfield = exact_matrices(4, labels)
    R = QQ.poly_ring(alpha)
    def cv(x):
        if hasattr(x, "element"):
            x = x.element
        return R.from_sympy(x.as_expr())
    C = DomainMatrix.from_list(
        [[cv(Cfield[i, j]) for j in range(Cfield.shape[1])] for i in range(Cfield.shape[0])], R
    )
    W = DomainMatrix.from_list(
        [[cv(Wfield[i, j]) for j in range(Wfield.shape[1])] for i in range(Wfield.shape[0])], R
    )

    # A pivot-row witness is reduction data, not an operator input.
    witness = json.loads((HERE / "order4_xi.json").read_text())
    piv = [rows.index(tuple(x)) for x in witness["pivot_rows"]]
    free = [i for i in range(len(rows)) if i not in piv]
    Cp = C.extract(piv, list(range(C.shape[1])))
    Wp = W.extract(piv, list(range(W.shape[1])))
    Xnum, xden = Cp.solve_den(Wp)
    reduced_num = W.mul(xden) - C * Xnum
    quotient = reduced_num.extract(free, list(range(W.shape[1])))
    ns = quotient.to_field().nullspace().to_Matrix()
    assert ns.rows == 1

    rational = [sp.factor(x) for x in list(ns.row(0))]
    top = next(x for x in reversed(rational) if sp.simplify(x) != 0)
    rational = [sp.cancel(x / top) for x in rational]
    polynomials, scale = primitive_polynomial_operator(rational)

    Xfield = Xnum.to_field() / xden
    rvec = DomainMatrix.from_list(
        [[Qalpha.from_sympy(x)] for x in rational], Qalpha
    )
    primitive = [
        sp.factor(scale * x.as_expr())
        for x in (Xfield * rvec).to_list_flat()
    ]
    return labels, polynomials, primitive


def main():
    # Symbol formula: verified directly from the exact-image map.
    n = sp.symbols("n")
    for r in range(1, 7):
        image = exact_image_map(ENERGY, r)
        for N in (31, 33, 35):
            src = [(0, N), (2, N - 2), (4, N - 4)]
            cols = [to_qalpha_rows(image(mono(0, p, q))) for p, q in src]
            rows = [(2, N + 5), (0, N + 5), (4, N + 3)]
            M = sp.Matrix([
                [c.get(row, Qalpha.zero).as_expr() for c in cols]
                for row in rows
            ])
            expected = 419904 * (N - (8*r - 3)) * (N - (8*r - 4)) * (N - (6*r - 3))
            assert sp.expand(M.det() - expected) == 0

    rank_table = []
    for r in range(1, 5):
        labels = exhaustive_labels(r)
        rows, C, W = exact_matrices(r, labels)
        A = DomainMatrix.hstack(C, W)
        rc, ra = C.rank(), A.rank()
        relations = (r + 1) - (ra - rc)
        rank_table.append((r, 8*r - 3, len(rows), len(labels), rc, ra, relations))
    assert [x[-1] for x in rank_table] == [0, 0, 0, 1]

    labels, derived_op, derived_V = derive_order4()
    stored_op = json.loads((HERE / "order4_operator.json").read_text())
    stored_P = [sp.sympify(x) for x in stored_op["polynomials"]]
    assert all(sp.expand(a - b) == 0 for a, b in zip(derived_op, stored_P))

    stored_xi = json.loads((HERE / "order4_xi.json").read_text())
    stored_V = {(x["p"], x["q"]): sp.sympify(x["coefficient"]) for x in stored_xi["coefficients"]}
    assert all(
        sp.expand(v - stored_V.get(label, 0)) == 0
        for label, v in zip(labels, derived_V)
    )
    nonzero = [(lab, v) for lab, v in zip(labels, derived_V) if sp.simplify(v) != 0]
    assert max(p + q for (p, q), _ in nonzero) == 29

    print("DEDUCTIVE_CERTIFICATE_PASS")
    print("symbol minor: 419904*(n-(8r-3))*(n-(8r-4))*(n-(6r-3))")
    print("exhaustive rank table: order, weight bound, rows, exact cols, rank C, rank [C|W], relations")
    for row in rank_table:
        print(*row)
    print("derived operator equals stored A4 exactly")
    print("derived primitive equals stored V exactly")
    print("nonzero primitive slots:", len(nonzero), "maximum source weight:", 29)


if __name__ == "__main__":
    main()
