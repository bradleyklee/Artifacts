#!/usr/bin/env python3
"""Replay the first exact non-dihedral even-quartic sphere certificate."""
from __future__ import annotations
import os
import json,pathlib,sys,time
import sympy as sp

ROOT=pathlib.Path(__file__).resolve().parents[2]
DATA_ROOT=pathlib.Path(os.environ.get('CURVES_MACHINE_DATA_ROOT', str(ROOT/'data')))
sys.path.insert(0,str(ROOT/"algorithms/src/core"))
from even_sphere_degree_bounds import EvenSphereDegreeBound,assumptions
from hyperelliptic_period_reduction import from_linear_in_t,alpha,x


def main():
    u,t=sp.symbols("u t")
    F=(t+10)*u**2-(2*t+11)*u+(t+6)-alpha
    reducer,N,B=from_linear_in_t(F,u,t)
    started=time.monotonic()
    cert=reducer.cohomology_certificate()
    seconds=time.monotonic()-started
    assert cert["status"]=="closed" and cert["order"]==4
    assert cert["matrix"].shape==(4,5) and cert["exact_residual"]==0
    bounds=[EvenSphereDegreeBound(d).record() for d in range(1,5)]
    out={
      "status":"exact_closed", "family":"reflection_xy",
      "hamiltonian_degree_in_J":4,
      "invariant_equation_F":str(sp.factor(F)),
      "linear_in_t_numerator_N":str(N), "linear_in_t_denominator_B":str(B),
      "hyperelliptic_P":str(sp.factor(reducer.P)),
      "hyperelliptic_degree":reducer.degree,"quotient_genus":reducer.genus,
      "cohomological_order_ceiling":reducer.order_ceiling,
      "actual_operator_order":cert["order"],
      "reduced_matrix_shape":list(cert["matrix"].shape),
      "operator_low_to_high":[str(a) for a in cert["operator"]],
      "primitive":str(cert["primitive"]),"exact_residual":"0",
      "normalization_multiplier":str(cert["normalization_multiplier"]),
      "exact_replay_seconds":seconds,
      "degree_ladder":bounds,"generic_bound_assumptions":assumptions(),
      "interpretation":"Reflection lowers the generic even-quartic ceiling from 6 to 4; exact cohomology reaches the genus-2 ceiling.",
      "bounded_ansatz_warning":"Earlier finite polynomial-support searches through x-degree 8 found no relation. This was a support failure, not an ODE nonexistence result."
    }
    target=DATA_ROOT/"examples/sphere_curves/reflection_xy_exact_certificate.json"
    target.write_text(json.dumps(out,indent=2)+"\n")
    (DATA_ROOT/"bounds/even_sphere_degree_bounds.json").write_text(
       json.dumps({"formula":{"genus":"d^2-d+1","order_ceiling":"2d^2-2d+2"},
                   "assumptions":assumptions(),"records":bounds},indent=2)+"\n")
    print("EVEN_SPHERE_REFLECTION_CERTIFICATE_PASS")
    print(f"order={cert['order']} matrix={cert['matrix'].shape} seconds={seconds:.3f}")
    print("exact_residual=0")

if __name__=="__main__":main()
