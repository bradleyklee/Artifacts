#!/usr/bin/env python3
"""Benchmark unrestricted polynomial sphere models after angle elimination."""
from __future__ import annotations
import os
import json,pathlib,sys,time
import sympy as sp

ROOT=pathlib.Path(__file__).resolve().parents[2]
DATA_ROOT=pathlib.Path(os.environ.get('CURVES_MACHINE_DATA_ROOT', str(ROOT/'data')))
sys.path.insert(0,str(ROOT/"algorithms/src/core"))
import dihedral_ode_sphere as d
from hyperelliptic_period_reduction import HyperellipticPeriodReducer,x


def run(name,h1):
    h2=sp.Rational(3,2)*sp.sqrt(3)*d.lam*(1-d.lam**2)
    model=d.DihedralSphereModel(name,h1,h2,2)
    P=sp.expand(model.lambda_dot_squared.subs(d.lam,x))
    reducer=HyperellipticPeriodReducer(P)
    started=time.monotonic()
    cert=reducer.polynomial_reduction_certificate()
    seconds=time.monotonic()-started
    assert cert["status"]=="closed" and cert["exact_residual"]==0
    return {"name":name,"h1":str(h1),"h2":str(h2),
      "hamiltonian_angle_form":f"({h1}) + ({h2})*cos(2*phi)",
      "eliminated_P":str(P),"P_degree_lambda":reducer.degree,
      "actual_operator_order":cert["order"],
      "reduced_matrix_shape":list(cert["matrix"].shape),
      "operator_low_to_high":[str(a) for a in cert["operator"]],
      "primitive":str(cert["primitive"]),"primitive_chars":len(str(cert["primitive"])),
      "exact_residual":"0","seconds":seconds}


def main():
    cases=[("tetrahedral",sp.S.Zero),
           ("tetra_plus_z2",d.lam**2),
           ("tetra_plus_z",d.lam),
           ("tetra_plus_z_z2",d.lam+2*d.lam**2)]
    records=[]
    for name,h1 in cases:
        rec=run(name,h1);records.append(rec)
        print(name,"order",rec["actual_operator_order"],"seconds",rec["seconds"],flush=True)
    out={"method":"angle elimination, polynomial division, exact-derivative reduction, nullspace",
         "scope":"polynomial sphere Hamiltonians; these examples have one angular harmonic",
         "records":records}
    target=DATA_ROOT/"examples/sphere_curves/unrestricted_single_harmonic_benchmark.json"
    target.write_text(json.dumps(out,indent=2)+"\n")
    print("UNRESTRICTED_SINGLE_HARMONIC_BENCHMARK_PASS")

if __name__=="__main__":main()
