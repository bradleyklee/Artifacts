#!/usr/bin/env python3
"""Reconstruct and exactly verify the first even-sphere certificate."""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"algorithms/src/core"))

import sympy as sp
import even_sphere_quartic_factory as s


def main() -> None:
    a, b, c = sp.symbols("a b c")
    F = s.showcase_models()["asymmetric_top"].action_fiber().subs({a:1,b:2,c:5})
    M, unknowns, Xi = s.bounded_certificate_matrix(F, 2, 3, 0, 6, 3)
    relations = [q for q in M.nullspace() if any(q[i] for i in range(12))]
    assert len(relations) == 1
    q = relations[0]
    Xi = sp.factor(Xi.subs(dict(zip(unknowns, list(q)))))
    operator = [sp.factor(sum(q[4*k+j]*s.alpha**j for j in range(4))) for k in range(3)]
    assert s.verify_operator_exact(F, operator, Xi) == 0
    expected = [z.subs({a:1,b:2,c:5}) for z in s.dissertation_asymmetric_operator()]
    ratios = [sp.cancel(operator[i]/expected[i]) for i in range(3)]
    assert ratios[0] == ratios[1] == ratios[2]
    print("EVEN_SPHERE_ASYMMETRIC_CERTIFICATE_PASS")
    print(f"matrix_shape={M.shape}")
    print(f"operator={operator}")
    print(f"dissertation_common_scale={ratios[0]}")
    print(f"primitive={Xi}")
    print("quotient_residual=0")


if __name__ == "__main__":
    main()

