#!/usr/bin/env python3
"""Exact Cartesian differential reduction over Q(alpha).

This module derives period annihilators without period-series guessing.
It works with the energy polynomial E(p,q)=2H(p,q) and the invariant
period form omega = 2*dq/E_p = dq/H_p.

Current backend assumptions:
  * E has rational coefficients;
  * E is monic up to a nonzero rational constant in p;
  * reduction modulo E-alpha is therefore a polynomial remainder in p;
  * the primitive pole divisor is initially restricted to E_p^(2r-1).

The key finite-dimensional object for order r is

  numerator space / exact_image_space

over Q(alpha).  The first dependence among the reduced derivative classes
of omega gives the annihilator.  No candidate operator is supplied.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from typing import Dict, Iterable, List, Sequence, Tuple

import sympy as sp
from sympy import QQ
from sympy.polys.matrices import DomainMatrix

from polynomial_hamiltonian_to_ode import (
    add, scale, mul, power, der, mono, make_hamiltonian, curve_reducer,
)

SparsePoly = Dict[Tuple[int, int, int], F]
RowKey = Tuple[int, int]  # (p_degree, q_degree)

alpha = sp.symbols("alpha")
Qalpha = QQ.frac_field(alpha)


@dataclass
class ReductionAttempt:
    order: int
    primitive_q_degree: int
    rows: List[RowKey]
    primitive_labels: List[RowKey]
    exact_matrix: DomainMatrix
    derivative_matrix: DomainMatrix
    combined_nullspace: DomainMatrix

    @property
    def exact_columns(self) -> int:
        return len(self.primitive_labels)

    @property
    def derivative_columns(self) -> int:
        return self.order + 1

    @property
    def combined_rank(self) -> int:
        return self.exact_columns + self.derivative_columns - self.combined_nullspace.shape[0]


@dataclass
class DerivedRelation:
    order: int
    primitive_q_degree: int
    rational_operator: List[sp.Expr]
    polynomial_operator: List[sp.Expr]
    primitive_coefficients: Dict[RowKey, sp.Expr]
    primitive_numerator: SparsePoly
    exact_column_count: int
    exact_rank: int
    quotient_dimension: int
    combined_rank: int
    row_count: int
    pivot_rows: List[RowKey]
    quotient_rows: List[RowKey]
    reduced_class_entries: Dict[str, Dict[str, str]]
    reduced_class_support: int
    reduced_class_text_size: int
    monomial_order: str


def triangle_square_energy() -> SparsePoly:
    """Return E=2H for the normalized triangle+square example."""
    return make_hamiltonian([
        {"degree": 3, "mode": 3, "coefficient": "1"},
        {"degree": 4, "mode": 4, "coefficient": "1/4"},
    ])


def to_qalpha_rows(poly: SparsePoly) -> Dict[RowKey, object]:
    """Collect alpha powers into coefficients in Q(alpha)."""
    out: Dict[RowKey, object] = {}
    for (a, p, q), c in poly.items():
        coeff = sp.Rational(c.numerator, c.denominator) * alpha**a
        out[(p, q)] = out.get((p, q), Qalpha.zero) + Qalpha.from_sympy(coeff)
    return {k: v for k, v in out.items() if v}


def derivative_numerators(energy: SparsePoly, order: int) -> List[SparsePoly]:
    """N_j for D_alpha^j(2/E_p)=N_j/E_p^(2j+1)."""
    Ep = der(energy, 1)
    Epp = der(Ep, 1)
    nums: List[SparsePoly] = [{(0, 0, 0): F(2)}]
    for j in range(order):
        nxt = add(mul(Ep, der(nums[-1], 1)), mul(nums[-1], Epp), -F(2*j + 1))
        nums.append(nxt)
    return nums


def exact_image_map(energy: SparsePoly, order: int):
    """Return V -> numerator of d(V/E_p^(2r-1)) at denominator E_p^(2r+1)."""
    _, reduce_curve = curve_reducer(energy)
    Ep = der(energy, 1)
    Eq = der(energy, 2)
    Epp = der(Ep, 1)
    Epq = der(Ep, 2)
    m = 2*order - 1
    jac = add(mul(Ep, Epq), mul(Epp, Eq), F(-1))

    def image(V: SparsePoly) -> SparsePoly:
        transport = add(mul(Ep, der(V, 2)), mul(Eq, der(V, 1)), F(-1))
        return reduce_curve(add(mul(Ep, transport), mul(V, jac), F(-m)))

    return image


def common_derivative_numerators(energy: SparsePoly, order: int) -> List[SparsePoly]:
    """Put omega,...,D_alpha^order omega over common denominator E_p^(2r+1)."""
    _, reduce_curve = curve_reducer(energy)
    Ep = der(energy, 1)
    nums = derivative_numerators(energy, order)
    return [reduce_curve(mul(nums[j], power(Ep, 2*(order-j)))) for j in range(order+1)]


def build_attempt(
    energy: SparsePoly,
    order: int,
    primitive_q_degree: int,
    p_degrees: Sequence[int] | None = None,
) -> ReductionAttempt:
    """Build exact-image and derivative matrices over Q(alpha)."""
    p_degree, _ = curve_reducer(energy)
    if p_degrees is None:
        p_degrees = tuple(range(p_degree))
    image = exact_image_map(energy, order)

    labels: List[RowKey] = []
    exact_columns: List[Dict[RowKey, object]] = []
    for p in p_degrees:
        for q in range(primitive_q_degree + 1):
            labels.append((p, q))
            exact_columns.append(to_qalpha_rows(image(mono(0, p, q))))

    derivative_columns = [to_qalpha_rows(w) for w in common_derivative_numerators(energy, order)]
    rows = sorted(set().union(*(c.keys() for c in exact_columns + derivative_columns)))
    exact_matrix = DomainMatrix.from_list(
        [[c.get(row, Qalpha.zero) for c in exact_columns] for row in rows], Qalpha
    )
    derivative_matrix = DomainMatrix.from_list(
        [[c.get(row, Qalpha.zero) for c in derivative_columns] for row in rows], Qalpha
    )
    combined = DomainMatrix.hstack(exact_matrix, derivative_matrix)
    nullspace = combined.nullspace()
    return ReductionAttempt(
        order=order,
        primitive_q_degree=primitive_q_degree,
        rows=rows,
        primitive_labels=labels,
        exact_matrix=exact_matrix,
        derivative_matrix=derivative_matrix,
        combined_nullspace=nullspace,
    )


def relation_rows(attempt: ReductionAttempt) -> List[List[sp.Expr]]:
    """Return combined nullspace rows that contain a derivative relation."""
    B = attempt.combined_nullspace.to_Matrix()
    n_exact = attempt.exact_columns
    good: List[List[sp.Expr]] = []
    for i in range(B.rows):
        row = list(B.row(i))
        if any(sp.simplify(x) != 0 for x in row[n_exact:]):
            good.append(row)
    return good


def primitive_polynomial_operator(rational: Sequence[sp.Expr]) -> Tuple[List[sp.Expr], sp.Expr]:
    """Clear denominators and polynomial content; return coefficients and scale."""
    den = sp.lcm([sp.denom(sp.cancel(x)) for x in rational])
    raw = [sp.expand(sp.cancel(x*den)) for x in rational]
    content = sp.gcd_list(raw)
    if content == 0:
        raise ValueError("zero operator")
    polys = [sp.factor(x/content) for x in raw]
    scale_factor = sp.cancel(den/content)
    # Normalize leading coefficient to positive leading alpha coefficient.
    leading = sp.Poly(polys[-1], alpha, domain=QQ).LC()
    if leading < 0:
        polys = [-x for x in polys]
        scale_factor = -scale_factor
    return polys, sp.factor(scale_factor)


def sparse_from_qalpha_coefficients(coeffs: Dict[RowKey, sp.Expr]) -> SparsePoly:
    """Convert polynomial-in-alpha coefficient functions to sparse triples."""
    out: SparsePoly = {}
    for (p, q), expr in coeffs.items():
        expr = sp.cancel(expr)
        if sp.denom(expr) != 1:
            raise ValueError(f"primitive coefficient is not polynomial: {(p,q)} -> {expr}")
        poly = sp.Poly(expr, alpha, domain=QQ)
        for (a,), c in poly.terms():
            if c:
                out[(a, p, q)] = F(int(c.p), int(c.q))
    return out


def ordered_rows(rows: Iterable[RowKey], strategy: str) -> List[RowKey]:
    if strategy == "low_degree_first":
        return sorted(rows)
    if strategy == "high_q_first":
        return sorted(rows, key=lambda x: (-x[1], -x[0]))
    raise ValueError(f"unknown row ordering: {strategy}")


def explicit_quotient_reduction(
    attempt: ReductionAttempt,
    strategy: str = "high_q_first",
) -> Tuple[List[RowKey], List[RowKey], DomainMatrix, int, int]:
    """Reduce derivative columns modulo exact columns using a chosen pivot-row normal form."""
    row_order = ordered_rows(attempt.rows, strategy)
    pos = {r: i for i, r in enumerate(attempt.rows)}
    permutation = [pos[r] for r in row_order]
    C = attempt.exact_matrix.extract(permutation, list(range(attempt.exact_columns)))
    W = attempt.derivative_matrix.extract(permutation, list(range(attempt.derivative_columns)))
    _, pivot_indices = C.transpose().rref()
    pivot_indices = list(pivot_indices)
    free_indices = [i for i in range(C.shape[0]) if i not in pivot_indices]
    Cp = C.extract(pivot_indices, list(range(C.shape[1])))
    Wp = W.extract(pivot_indices, list(range(W.shape[1])))
    reduced = W - C*(Cp.inv()*Wp)
    for i in pivot_indices:
        for j in range(W.shape[1]):
            if reduced[i, j] != Qalpha.zero:
                raise AssertionError("pivot row failed to reduce to zero")
    support = 0
    text_size = 0
    for i in free_indices:
        for j in range(W.shape[1]):
            elem = reduced[i, j].element
            if elem:
                support += 1
                text_size += len(str(sp.factor(elem.as_expr())))
    return (
        [row_order[i] for i in pivot_indices],
        [row_order[i] for i in free_indices],
        reduced.extract(free_indices, list(range(W.shape[1]))),
        support,
        text_size,
    )


def derive_relation(
    energy: SparsePoly,
    order: int,
    primitive_q_degree: int,
    p_degrees: Sequence[int] | None = None,
    monomial_order: str = "high_q_first",
) -> DerivedRelation | None:
    """Derive the first relation at fixed order/bound, then reconstruct Xi."""
    attempt = build_attempt(energy, order, primitive_q_degree, p_degrees)
    good = relation_rows(attempt)
    if not good:
        return None

    row = good[0]
    n_exact = attempt.exact_columns
    rational = [sp.factor(x) for x in row[n_exact:]]
    highest = next((x for x in reversed(rational) if sp.simplify(x) != 0), None)
    if highest is None:
        return None
    row = [sp.factor(x/highest) for x in row]
    rational = row[n_exact:]
    polynomial_operator, scale_factor = primitive_polynomial_operator(rational)

    # Combined relation: C*x + W*r = 0.  Multiplying by scale_factor gives
    # C*(scale*x) + W*P = 0, hence Xi numerator is V = -scale*x.
    primitive_coeffs = {
        label: sp.factor(-scale_factor*x)
        for label, x in zip(attempt.primitive_labels, row[:n_exact])
        if sp.simplify(x) != 0
    }
    primitive_numerator = sparse_from_qalpha_coefficients(primitive_coeffs)

    pivots, quotient_rows, reduced, support, text_size = explicit_quotient_reduction(
        attempt, monomial_order
    )
    class_entries: Dict[str, Dict[str, str]] = {}
    for j in range(order+1):
        entries: Dict[str, str] = {}
        for i, monomial in enumerate(quotient_rows):
            elem = reduced[i, j].element
            if elem:
                entries[f"p^{monomial[0]} q^{monomial[1]}"] = str(sp.factor(elem.as_expr()))
        class_entries[f"D_alpha^{j}(omega)"] = entries

    # The exact columns are independent in the successful triangle-square sector.
    exact_rank = len(attempt.exact_matrix.transpose().rref()[1])
    quotient_dimension = len(attempt.rows) - exact_rank
    return DerivedRelation(
        order=order,
        primitive_q_degree=primitive_q_degree,
        rational_operator=[sp.factor(x) for x in rational],
        polynomial_operator=polynomial_operator,
        primitive_coefficients=primitive_coeffs,
        primitive_numerator=primitive_numerator,
        exact_column_count=attempt.exact_columns,
        exact_rank=exact_rank,
        quotient_dimension=quotient_dimension,
        combined_rank=attempt.combined_rank,
        row_count=len(attempt.rows),
        pivot_rows=pivots,
        quotient_rows=quotient_rows,
        reduced_class_entries=class_entries,
        reduced_class_support=support,
        reduced_class_text_size=text_size,
        monomial_order=monomial_order,
    )


def search_first_relation(
    energy: SparsePoly,
    max_order: int,
    max_q_degree_by_order: Dict[int, int],
    p_degrees: Sequence[int] | None = None,
    monomial_order: str = "high_q_first",
):
    """Search order first, then primitive q-degree.  No operator is supplied."""
    log = []
    for order in range(1, max_order+1):
        max_q = max_q_degree_by_order.get(order, 0)
        for q_degree in range(0, max_q+1):
            attempt = build_attempt(energy, order, q_degree, p_degrees)
            good = relation_rows(attempt)
            record = {
                "order": order,
                "primitive_q_degree": q_degree,
                "rows": len(attempt.rows),
                "exact_columns": attempt.exact_columns,
                "derivative_columns": attempt.derivative_columns,
                "nullity": attempt.combined_nullspace.shape[0],
                "relation_found": bool(good),
            }
            log.append(record)
            if good:
                return derive_relation(
                    energy, order, q_degree, p_degrees, monomial_order
                ), log
    return None, log


def verify_identity(energy: SparsePoly, relation: DerivedRelation) -> None:
    """Verify A_alpha o omega = d Xi as a sparse polynomial identity."""
    image = exact_image_map(energy, relation.order)
    W = common_derivative_numerators(energy, relation.order)
    lhs: SparsePoly = {}
    for poly, w in zip(relation.polynomial_operator, W):
        pp = sp.Poly(poly, alpha, domain=QQ)
        P_sparse = {
            (a, 0, 0): F(int(c.p), int(c.q))
            for (a,), c in pp.terms()
        }
        lhs = add(lhs, mul(P_sparse, w))
    rhs = image(relation.primitive_numerator)
    residual = add(rhs, lhs, F(-1))
    if residual:
        raise AssertionError(f"nonzero exact-differential residual: {residual}")
