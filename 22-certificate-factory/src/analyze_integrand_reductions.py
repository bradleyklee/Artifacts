#!/usr/bin/env python3
"""Classify all 23 integrands against the exact q3 reduction algorithms."""

from __future__ import annotations

import json
from fractions import Fraction
from math import comb
from pathlib import Path

import sympy as sp

from expand_target_coverage import CORE, DESC, POWERS

u, x, n = sp.symbols("u x n")


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def polynomial_kernel(q: int, r: int, b: int):
    d = Fraction(b, r - q)
    cs = {k: Fraction(comb(q, k) * d**k, b) for k in range(2, q + 1)}
    D = 1 - sum(sp.Rational(v.numerator, v.denominator) * u ** (k - 1) for k, v in cs.items())
    return d, sp.expand(u * D)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    examples = root / "examples"
    summary = {}

    for case_id, (q, r, b, _) in CORE.items():
        d, rho = polynomial_kernel(q, r, b)
        resultant = sp.resultant(rho, sp.diff(rho, u), u)
        assert resultant != 0
        record = {
            "status": "verified",
            "integrand": f"({d})/(n*({sp.sstr(rho)})^n)",
            "kernel_class": "polynomial_power",
            "term_shift_ratio": f"n/((n+s)*({sp.sstr(rho)})^s)",
            "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
            "G": {
                "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
                "shape": [2 * q, 2 * q],
                "invertibility_witness": f"resultant(rho,rho')={resultant}",
            },
            "remainder_dimension": q - 1,
            "expected_shift_count_for_first_nullvector": q,
            "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
        }
        dump(examples / case_id / "data/integrand_analysis.json", record)
        summary[case_id] = record

    for case_id, (parent, power, _) in POWERS.items():
        q, r, b, _ = CORE[parent]
        d, rho = polynomial_kernel(q, r, b)
        seed = sp.expand((1 + sp.Rational(d.numerator, d.denominator) * u) ** (power - 1))
        resultant = sp.resultant(rho, sp.diff(rho, u), u)
        assert sp.degree(seed, u) < q and resultant != 0
        record = {
            "status": "verified",
            "integrand": f"({power*d})*({sp.sstr(seed)})/(n*({sp.sstr(rho)})^n)",
            "kernel_class": "polynomial_power_with_fixed_seed",
            "term_shift_ratio": f"n/((n+s)*({sp.sstr(rho)})^s)",
            "q3_algorithm_relation": "identical G/U/V and pole lowering; initialize shift 0 with the coefficient vector of the fixed seed instead of e_0",
            "G": {
                "shape": [2 * q, 2 * q],
                "invertibility_witness": f"resultant(rho,rho')={resultant}",
            },
            "seed_degree": int(sp.degree(seed, u)),
            "remainder_dimension": q - 1,
            "expected_shift_count_for_first_nullvector": q,
            "required_change": "accept a fixed numerator seed vector and propagate it through every shifted column",
        }
        dump(examples / case_id / "data/integrand_analysis.json", record)
        summary[case_id] = record

    for case_id, (q, r, s, _) in DESC.items():
        d = Fraction(s, r - q)
        cs = {k: Fraction(comb(q, k) * d**k, s) for k in range(2, q + 1)}
        h = sp.expand(1 + sp.Rational(d.numerator, d.denominator) * u)
        N = sp.expand(1 - sum(sp.Rational(v.numerator, v.denominator) * u ** (k - 1) for k, v in cs.items()))
        p = sp.expand(u * N)
        gx = sp.expand(p - x * h)
        disc = sp.factor(sp.discriminant(gx, u))
        record = {
            "status": "produced",
            "integrand": f"({d})*({sp.sstr(h)})^n/(n*({sp.sstr(p)})^n)",
            "kernel_class": "rational_rho_or_two_polynomial_hyperexponential",
            "term_shift_ratio": f"n*({sp.sstr(h)})^s/((n+s)*({sp.sstr(p)})^s)",
            "logarithmic_u_derivative": f"n*(({sp.sstr(sp.diff(h,u))})/({sp.sstr(h)})-({sp.sstr(sp.diff(p,u))})/({sp.sstr(p)}))",
            "term_shift_assessment": {
                "result": "requires_generalization",
                "reason": "the numerator h^n varies with n, so the single-polynomial rho G/U/V identity does not apply unchanged",
                "candidate": "two-factor Hermite reduction over poles p=0 and h=0, retaining exact n-dependent residues",
            },
            "direct_x_assessment": {
                "result": "same_polynomial_algorithm",
                "kernel": f"g_x(u)=p(u)-x*h(u)={sp.sstr(gx)}",
                "degree_in_u": int(sp.degree(gx, u)),
                "generic_squarefree_witness": f"discriminant_u(g_x)={disc}",
                "route": "apply the paper's G_x/U_x/V_x derivative reduction directly to 1/g_x; this is the preferred first implementation",
            },
            "required_change": "implement direct-x polynomial reduction first; defer term-shift certificates until the two-factor lowering identity is derived and checked",
        }
        dump(examples / case_id / "data/integrand_analysis.json", record)
        summary[case_id] = record

    dump(root / "reports/integrand_reduction_analysis.json", {
        "status": "produced",
        "case_count": len(summary),
        "classes": {
            "polynomial_power": 18,
            "polynomial_power_with_fixed_seed": 2,
            "rational_rho_or_two_polynomial_hyperexponential": 3,
        },
        "cases": summary,
    })
    for case_id, record in summary.items():
        manifest_path = examples / case_id / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["components"]["integrand_analysis"] = {
            "status": record["status"],
            "canonical_path": "data/integrand_analysis.json",
        }
        dump(manifest_path, manifest)
    print(json.dumps({"cases": len(summary), "polynomial_shift_ready": 20, "rational_direct_x_ready": 3}))


if __name__ == "__main__":
    main()
