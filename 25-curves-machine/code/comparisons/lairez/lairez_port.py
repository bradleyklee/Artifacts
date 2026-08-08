#!/usr/bin/env python3
"""Small exact SymPy port of the Griffiths--Dwork core used by Lairez.

This is a deliberately specialized comparison implementation for plane-curve
periods.  Algorithmic attribution: Pierre Lairez, "Computing periods of
rational integrals", Math. Comp. 85 (2016), extending Griffiths--Dwork by
Rham--Koszul reduction.  Research cases and comparison program: Bradley Klee.

The present milestone implements ordinary projective Jacobian pole reduction.
It is expected to close on smooth showcase fibers.  The quotient ledger is
retained for later conversion into an explicit exact-form certificate.
"""

from __future__ import annotations

import argparse
import json
import time
from functools import lru_cache
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

import sympy as s
from sympy import QQ
from sympy.polys.matrices import DomainMatrix

ROOT = Path(__file__).resolve().parent


@dataclass
class ReductionStep:
    pole_from: int
    numerator: s.Expr
    remainder: s.Expr
    quotients: Tuple[s.Expr, ...]
    lowered_numerator: s.Expr


@dataclass
class ReducedClass:
    terms: Dict[int, s.Expr]
    ledger: List[ReductionStep] = field(default_factory=list)
    # beta=(certificate_dp) dp + (certificate_dq) dq, with
    # raw_form = reduced_form + d beta after dehomogenizing z=1.
    certificate: Tuple[s.Expr, s.Expr] | None = None


class PlaneGriffithsDwork:
    def __init__(self, energy: s.Expr, track_certificate: bool = False):
        self.alpha, self.p, self.q, self.z = s.symbols("alpha p q z")
        self.vars = (self.p, self.q, self.z)
        self.parameters = tuple(sorted(energy.free_symbols - {self.p, self.q},
                                       key=str))
        poly = s.Poly(energy, self.p, self.q)
        self.degree = poly.total_degree()
        d = self.degree
        # Homogenize E(p,q)-alpha to degree d.
        F = s.expand(self.z**d * energy.subs({self.p: self.p/self.z,
                                               self.q: self.q/self.z})
                     - self.alpha*self.z**d)
        self.F = s.cancel(F)
        self.f = s.expand(energy - self.alpha)
        self.Fa = s.diff(self.F, self.alpha)
        self.jac = tuple(s.diff(self.F, v) for v in self.vars)
        self.domain = s.QQ.frac_field(self.alpha, *self.parameters)
        self.coefficient_field = (s.QQ.frac_field(*self.parameters)
                                  if self.parameters else s.QQ)
        self.gb = s.groebner(self.jac, *self.vars,
                             order="grevlex", domain=self.domain)
        # Homogenized 2/(E-alpha) dp dq in projective dimension 2.
        self.track_certificate = track_certificate
        initial_certificate = (s.Integer(0), s.Integer(0)) if track_certificate else None
        self.initial = ReducedClass({1: s.Integer(2)*self.z**(d-3)},
                                    certificate=initial_certificate)
        self.profile_stats = {}

    @staticmethod
    def _exponents_of_degree(deg: int):
        return [(i, j, deg-i-j) for i in range(deg+1)
                for j in range(deg-i+1)]

    def _monomial(self, exp):
        return self.p**exp[0]*self.q**exp[1]*self.z**exp[2]

    @lru_cache(maxsize=None)
    def _jacobian_map(self, multiplier_degree: int):
        """Matrix for (G_p,G_q,G_z) -> sum G_i F_i at fixed degree."""
        src_exp = self._exponents_of_degree(multiplier_degree)
        out_degree = multiplier_degree + self.degree - 1
        out_exp = self._exponents_of_degree(out_degree)
        columns = []
        for fi in self.jac:
            for exp in src_exp:
                poly = s.Poly(s.expand(self._monomial(exp)*fi), *self.vars,
                              domain=self.domain)
                columns.append([poly.coeff_monomial(self._monomial(e))
                                for e in out_exp])
        return src_exp, out_exp, s.Matrix(len(out_exp), len(columns),
                                          lambda i, j: columns[j][i])

    @lru_cache(maxsize=None)
    def _generic_profile(self, multiplier_degree: int):
        """Generic column/row profile, analogous to Lairez's profile reuse."""
        _, _, A = self._jacobian_map(multiplier_degree)
        tick = time.perf_counter()
        print("PROFILE_BUILD", multiplier_degree, A.rows, A.cols, flush=True)
        point = s.Integer(101)
        evaluation = {self.alpha: point}
        for parameter, value in zip(self.parameters, (103, 107, 109, 113)):
            evaluation[parameter] = s.Integer(value)
        Ae = A.subs(evaluation)
        # Pivot columns form a basis of the generic image.
        _, cols = Ae.rref()
        Aec = Ae[:, list(cols)]
        # Pivot columns of the transpose select independent equations (rows).
        _, rows = Aec.T.rref()
        rows = tuple(rows)
        cols = tuple(cols)
        if len(rows) != len(cols):
            raise AssertionError((len(rows), len(cols)))
        self.profile_stats[multiplier_degree] = {
            "ambient_rows": A.rows, "source_columns": A.cols,
            "rank": len(cols), "pivot_rows": len(rows),
            "pivot_columns": len(cols),
            "evaluation_point": {str(k): int(v) for k, v in evaluation.items()},
        }
        print("PROFILE_BUILD_SECONDS", multiplier_degree,
              f"{time.perf_counter()-tick:.6f}", "RANK", len(cols), flush=True)
        return rows, cols

    def _profiled_solve(self, multiplier_degree: int, b: s.Matrix):
        """Fraction-free solve over QQ[alpha] in a cached generic profile."""
        _, _, A = self._jacobian_map(multiplier_degree)
        rows, cols = self._generic_profile(multiplier_degree)
        B = A.extract(list(rows), list(cols))
        bp = b.extract(list(rows), [0])
        den = s.lcm([s.denom(s.cancel(x)) for x in bp])
        bp = bp.applyfunc(lambda x: s.cancel(x*den))
        R = self.coefficient_field.poly_ring(self.alpha)

        def cv(x):
            return R.from_sympy(s.Poly(s.cancel(x), self.alpha,
                                       domain=self.coefficient_field).as_expr())

        Bdm = DomainMatrix.from_list(
            [[cv(B[i, j]) for j in range(B.cols)] for i in range(B.rows)], R)
        bdm = DomainMatrix.from_list(
            [[cv(bp[i, 0])] for i in range(bp.rows)], R)
        tick = time.perf_counter()
        print("PROFILE_SOLVE", multiplier_degree, B.rows, B.cols, flush=True)
        xnum, xden = Bdm.solve_den(bdm)
        print("PROFILE_SOLVE_SECONDS", multiplier_degree,
              f"{time.perf_counter()-tick:.6f}", flush=True)
        # Preserve one common denominator. Cancelling every coordinate
        # separately dominates high-order runs and throws away useful shared
        # structure (Lairez's reconstruction also seeks a common denominator).
        nums = [s.expand(x.as_expr()) for x in xnum.to_list_flat()]
        common_den = s.expand(xden.as_expr()*den)
        sol_num = [s.Integer(0)]*A.cols
        for j, value in zip(cols, nums):
            sol_num[j] = value
        # Full-row verification is mandatory; do it fraction-free in QQ[alpha]
        # rather than simplifying a large rational expression row by row.
        Afull = DomainMatrix.from_list(
            [[cv(A[i, j]) for j in cols] for i in range(A.rows)], R)
        bfull = DomainMatrix.from_list(
            [[cv(s.cancel(b[i, 0]*den))] for i in range(b.rows)], R)
        if Afull*xnum != bfull.mul(xden):
            raise AssertionError("cached generic profile failed full-row check")
        return s.Matrix(sol_num), common_den

    def jacobian_decompose(self, target: s.Expr):
        """Write target=sum G_i F_i, choosing one exact degreewise solution."""
        if target == 0:
            return (s.Integer(0),)*3
        poly = s.Poly(target, *self.vars, domain=self.domain)
        degrees = {sum(mon) for mon, coeff in poly.terms() if coeff != 0}
        if len(degrees) != 1:
            raise ValueError(f"Jacobian target is not homogeneous: {degrees}")
        out_degree = degrees.pop()
        mult_degree = out_degree - (self.degree-1)
        if mult_degree < 0:
            raise ValueError("target degree below Jacobian degree")
        src_exp, out_exp, A = self._jacobian_map(mult_degree)
        b = s.Matrix([poly.coeff_monomial(self._monomial(e)) for e in out_exp])
        sol_num, sol_den = self._profiled_solve(mult_degree, b)
        n = len(src_exp)
        G = []
        for block in range(3):
            numerator = s.expand(sum(sol_num[block*n+j]*self._monomial(exp)
                                     for j, exp in enumerate(src_exp)))
            G.append(s.cancel(numerator/sol_den))
        # _profiled_solve already verified the complete original-Jacobian map
        # fraction-free, so avoid repeating it via costly expression expansion.
        return tuple(G)

    def reduce(self, cls: ReducedClass) -> ReducedClass:
        terms = {k: s.expand(v) for k, v in cls.terms.items() if v != 0}
        ledger = list(cls.ledger)
        certificate = cls.certificate
        if not terms:
            return ReducedClass({}, ledger, certificate)
        maxpole = max(terms)
        for k in range(maxpole, 1, -1):
            P = s.expand(terms.pop(k, 0))
            if P == 0:
                continue
            _, rem = self.gb.reduce(P)
            rem = s.expand(rem)
            quot = self.jacobian_decompose(s.expand(P-rem))
            if rem != 0:
                terms[k] = s.expand(terms.get(k, 0) + rem)
            # If P = rem + sum_i quot_i F_i, then
            # sum quot_i F_i/F^k is cohomologous to
            # (sum d_i quot_i)/(k-1)/F^(k-1).
            low = s.expand(sum(s.diff(quot[i], self.vars[i])
                               for i in range(3)) / s.Integer(k-1))
            ledger.append(ReductionStep(k, P, rem, tuple(quot), low))
            if certificate is not None:
                # Dehomogenize the projective Griffiths--Dwork homotopy.
                # Put A=G_p-pG_z and B=G_q-qG_z at z=1. Then
                # P/f^k - rem/f^k - div(G)/(k-1)f^(k-1)
                #   = d[(B dp-A dq)/((k-1)f^(k-1))].
                gp, gq, gz = [s.expand(g.subs(self.z, 1)) for g in quot]
                A = s.expand(gp - self.p*gz)
                B = s.expand(gq - self.q*gz)
                denom = s.Integer(k-1)*self.f**(k-1)
                certificate = (certificate[0] + B/denom,
                               certificate[1] - A/denom)
            if low != 0:
                terms[k-1] = s.expand(terms.get(k-1, 0) + low)
        return ReducedClass({k: s.cancel(v) for k, v in terms.items() if v != 0},
                            ledger, certificate)

    def derivative(self, cls: ReducedClass) -> ReducedClass:
        out: Dict[int, s.Expr] = {}
        for k, P in cls.terms.items():
            out[k] = s.expand(out.get(k, 0) + s.diff(P, self.alpha))
            # d(P/F^k)/da = P_a/F^k - k P F_a/F^(k+1)
            out[k+1] = s.expand(out.get(k+1, 0) - k*P*self.Fa)
        certificate = None
        if cls.certificate is not None:
            certificate = tuple(s.diff(x, self.alpha) for x in cls.certificate)
        return self.reduce(ReducedClass(out, list(cls.ledger), certificate))

    def assemble_certificate(self, classes: List[ReducedClass], op: List[s.Expr]):
        """Assemble and verify the affine exact one-form for an Ore relation."""
        if any(cls.certificate is None for cls in classes):
            raise ValueError("certificate tracking was not enabled")
        beta_p = sum(op[j]*classes[j].certificate[0] for j in range(len(op)))
        beta_q = sum(op[j]*classes[j].certificate[1] for j in range(len(op)))
        # d(beta_p dp + beta_q dq)=(d_p beta_q-d_q beta_p) dp dq.
        exterior = s.diff(beta_q, self.p) - s.diff(beta_p, self.q)
        target = sum(op[j]*s.factorial(j)*2/self.f**(j+1)
                     for j in range(len(op)))
        residual = s.cancel(s.together(exterior-target))
        if residual != 0:
            raise AssertionError(f"nonzero affine certificate residual: {residual}")
        return s.cancel(s.together(beta_p)), s.cancel(s.together(beta_q))

    def vectorize(self, classes: List[ReducedClass]):
        keys = set()
        dicts = []
        for cls in classes:
            dct = {}
            for pole, expr in cls.terms.items():
                poly = s.Poly(expr, *self.vars, domain=self.domain)
                for mon, coeff in poly.terms():
                    key = (pole,) + tuple(mon)
                    dct[key] = coeff
                    keys.add(key)
            dicts.append(dct)
        keys = sorted(keys)
        M = s.Matrix([[dct.get(key, 0) for j, dct in enumerate(dicts)]
                      for key in keys])
        return keys, M

    def first_relation(self, max_order=8):
        classes = [self.reduce(self.initial)]
        for order in range(1, max_order+1):
            print("REDUCE_DERIVATIVE", order, flush=True)
            tick = time.perf_counter()
            classes.append(self.derivative(classes[-1]))
            print("REDUCE_DERIVATIVE_SECONDS", order,
                  f"{time.perf_counter()-tick:.6f}", flush=True)
            keys, M = self.vectorize(classes)
            print("CURRENT_CLASS_ROWS", order, len(keys), flush=True)
            ns = M.nullspace()
            if ns:
                # Prefer a relation using the newest derivative.
                candidates = [v for v in ns if v[-1] != 0]
                if candidates:
                    return classes, keys, M, candidates[0]
        return classes, keys, M, None


def parse_case(path: Path):
    data = json.loads(path.read_text())
    alpha, p, q, c1, c2 = s.symbols("alpha p q c1 c2")
    energy = s.sympify(data["energy_E_equals_2H"],
                       locals={"alpha": alpha, "p": p, "q": q,
                               "c1": c1, "c2": c2})
    return data, energy


def primitive_polynomial_relation(v):
    alpha = s.symbols("alpha")
    parameters = tuple(sorted(set().union(*(x.free_symbols for x in v)) - {alpha},
                              key=str))
    vals = [s.cancel(x) for x in list(v)]
    den = s.lcm([s.denom(x) for x in vals])
    exprs = [s.expand(s.cancel(x*den)) for x in vals]
    common_poly = s.gcd_list(exprs)
    if common_poly not in (0, 1, -1):
        exprs = [s.cancel(x/common_poly) for x in exprs]
    variables = (alpha,) + parameters
    pols = [s.Poly(x, *variables, domain=s.QQ) for x in exprs]
    content = s.gcd_list([c for p in pols for c in p.coeffs()])
    if content not in (0, 1, -1):
        exprs = [s.expand(x/content) for x in exprs]
    # Fix global sign by the leading nonzero coefficient of the last entry.
    lc = s.Poly(exprs[-1], *variables, domain=s.QQ).LC()
    if lc < 0:
        exprs = [-x for x in exprs]
    return exprs


def run_case(path: Path, max_order: int, certificate: bool = False,
             certificate_summary: bool = False, json_output: Path | None = None):
    data, energy = parse_case(path)
    t0 = time.perf_counter()
    gd = PlaneGriffithsDwork(energy, track_certificate=certificate)
    t1 = time.perf_counter()
    classes, keys, M, rel = gd.first_relation(max_order=max_order)
    t2 = time.perf_counter()
    print("CASE", data["name"])
    print("DEGREE", gd.degree)
    print("HOMOGENIZED_F", gd.F)
    print("JACOBIAN_BASIS_SIZE", len(gd.gb.polys))
    print("CLASS_VECTOR_ROWS", len(keys))
    print("DERIVATIVES_COMPUTED", len(classes)-1)
    print("SETUP_SECONDS", f"{t1-t0:.6f}")
    print("REDUCTION_SECONDS", f"{t2-t1:.6f}")
    if rel is None:
        print("NO_RELATION_THROUGH", max_order)
        return 2
    op = primitive_polynomial_relation(rel)
    print("FOUND_ORDER", len(op)-1)
    for j, coeff in enumerate(op):
        print(f"P{j}", s.factor(coeff))
    if certificate:
        cert_tick = time.perf_counter()
        beta_p, beta_q = gd.assemble_certificate(classes, op)
        print("CERTIFICATE_SECONDS", f"{time.perf_counter()-cert_tick:.6f}")
        if certificate_summary:
            for label, expr in (("DP", beta_p), ("DQ", beta_q)):
                num, den = s.fraction(expr)
                print(f"CERTIFICATE_{label}_NUM_TERMS",
                      len(s.Poly(num, gd.alpha, gd.p, gd.q).terms()))
                print(f"CERTIFICATE_{label}_DEN_TERMS",
                      len(s.Poly(den, gd.alpha, gd.p, gd.q).terms()))
        else:
            print("CERTIFICATE_DP", beta_p)
            print("CERTIFICATE_DQ", beta_q)
        print("CERTIFICATE_RESIDUAL_ZERO", True)
    if "known_operator_order" in data:
        print("KNOWN_ORDER", data["known_operator_order"])
        print("ORDER_MATCH", len(op)-1 == int(data["known_operator_order"]))
    print("LEDGER_STEPS", len(classes[-1].ledger))
    print("PROFILE_STATS", json.dumps(gd.profile_stats, sort_keys=True))
    if json_output is not None:
        json_output.write_text(json.dumps({
            "case": data["name"], "degree": gd.degree,
            "free_parameters": [str(x) for x in gd.parameters],
            "order": len(op)-1, "operator": [str(s.factor(x)) for x in op],
            "setup_seconds": t1-t0, "reduction_seconds": t2-t1,
            "profile_stats": gd.profile_stats,
            "certificate_requested": certificate,
        }, indent=2) + "\n")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case", type=Path)
    ap.add_argument("--max-order", type=int, default=8)
    ap.add_argument("--certificate", action="store_true")
    ap.add_argument("--certificate-summary", action="store_true")
    ap.add_argument("--json-output", type=Path)
    ns = ap.parse_args()
    raise SystemExit(run_case(ns.case, ns.max_order,
                              ns.certificate or ns.certificate_summary,
                              ns.certificate_summary, ns.json_output))


if __name__ == "__main__":
    main()
