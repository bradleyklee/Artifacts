#!/usr/bin/env python3
"""Reconstruct the octahedral certificate in the invariant t=v(1-v) chart."""
from __future__ import annotations

import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"algorithms/src/core"))

import sympy as sp
import octahedral_invariant_reduction as o


def main() -> None:
    M,unknowns,Xi=o.bounded_matrix(1,6,3,0)
    rel=[q for q in M.nullspace() if any(q[i] for i in range(12))]
    assert len(rel)==1
    q=rel[0]
    Xi=sp.factor(Xi.subs(dict(zip(unknowns,list(q)))))
    operator=[sp.factor(sum(q[4*k+j]*o.alpha**j for j in range(4))) for k in range(3)]
    assert o.verify(operator,Xi)==0
    expected=o.known_operator()
    ratios=[sp.cancel(operator[k]/expected[k]) for k in range(3)]
    assert ratios[0]==ratios[1]==ratios[2]==sp.Rational(-1,768)
    print("EVEN_SPHERE_OCTAHEDRAL_CERTIFICATE_PASS")
    print(f"matrix_shape={M.shape}")
    print(f"operator={operator}")
    print("dissertation_common_scale=-1/768")
    print(f"primitive={Xi}")
    print("quotient_residual=0")


if __name__=="__main__":
    main()

