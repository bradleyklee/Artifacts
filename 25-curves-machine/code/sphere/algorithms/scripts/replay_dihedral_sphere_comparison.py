#!/usr/bin/env python3
"""Derive Dihedral sphere certificates and compare to the new reducer exactly."""
from __future__ import annotations

import pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"algorithms/src/core"))

import sympy as sp
import dihedral_ode_sphere as d
import even_sphere_quartic_factory as q
import octahedral_invariant_reduction as o


def asymmetric_check():
    z=d.derive(d.asymmetric_top(),numerator_lambda_degree=0)
    assert z["status"]=="closed"
    a,b,c=sp.symbols("a b c")
    F=q.showcase_models()["asymmetric_top"].action_fiber().subs({a:1,b:2,c:5})
    Xi_general=q.v**2*(q.v-1)**2/(q.y**3*(q.v+3))
    Xi_dihedral=-2*(1-q.u)*q.y/(q.u**2*(q.alpha-5))
    assert q.reduce_on_curve(Xi_dihedral-2*Xi_general,F)==0
    return z


def octahedral_check():
    z=d.derive(d.octahedral(),numerator_lambda_degree=8)
    assert z["status"]=="closed"
    N=(6*o.alpha*o.t*o.u-6*o.alpha*o.t-6*o.alpha*o.u+5*o.alpha
       -12*o.t*o.u+12*o.t+12*o.u-6)
    Xi_general=-o.t**2*(4*o.t-1)**2*N/(6144*o.w**3*(2*o.t*o.u-2*o.t-2*o.u+1)**3)
    Nd=3*o.alpha**2-10*o.alpha*o.u-2*o.alpha+12*o.u
    Xi_dihedral=-sp.Rational(1,3)*(1-o.u)**2*o.w*Nd/(o.u**2*(o.alpha-2*o.u)**3)
    assert o.reduce_curve(Xi_dihedral-512*Xi_general)==0
    return z


def main():
    za=asymmetric_check(); zo=octahedral_check()
    ka=d.dissertation_kernel(d.asymmetric_top())
    ko=d.dissertation_kernel(d.octahedral())
    print("DIHEDRAL_SPHERE_COMPARISON_PASS")
    print(f"asymmetric_G={ka['G'].shape} det={ka['determinant']}")
    print(f"asymmetric_operator={za['operator']}")
    print(f"asymmetric_R={za['R']}")
    print("asymmetric_primitive_ratio_to_general=2 exact_difference=0")
    print(f"octahedral_G={ko['G'].shape} det={ko['determinant']}")
    print(f"octahedral_operator={zo['operator']}")
    print(f"octahedral_R={zo['R']}")
    print("octahedral_primitive_ratio_to_general=512 exact_difference=0")


if __name__=="__main__": main()
