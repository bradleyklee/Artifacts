#!/usr/bin/env python3
"""Derive and verify the icosahedral period operator by polynomial reduction."""
from __future__ import annotations
import os
import json,pathlib,sys,time
import sympy as sp

ROOT=pathlib.Path(__file__).resolve().parents[2]
DATA_ROOT=pathlib.Path(os.environ.get('CURVES_MACHINE_DATA_ROOT', str(ROOT/'data')))
sys.path.insert(0,str(ROOT/"algorithms/src/core"))
import icosahedral_sphere as ico
from hyperelliptic_period_reduction import HyperellipticPeriodReducer,x,alpha


def main():
    P=sp.expand(ico.eliminated_P().subs(ico.lam,x))
    reducer=HyperellipticPeriodReducer(P)
    started=time.monotonic()
    cert=reducer.polynomial_reduction_certificate(max_order=2)
    seconds=time.monotonic()-started
    out={"model":"icosahedral","degree_in_J":6,
      "source_formula":"Harter-Weeks sixth-rank rotational-energy surface, fivefold axis",
      "energy_convention":"alpha=(16*H_HarterWeeks+5)/21; H(north pole)=1; saddle=0; threefold=-5/27",
      "hamiltonian_cartesian":str(ico.cartesian()),
      "h1_lambda":str(ico.h1()),"h2_lambda":str(ico.h2()),
      "angular_form":"H=h1(lambda)+h2(lambda)*cos(5*phi)",
      "eliminated_P":str(P),"eliminated_P_degree":reducer.degree,
      "tested_max_order":2,"seconds":seconds}
    if cert["status"]=="closed":
        target=ico.chapter4_operator()
        ratios=[sp.cancel(a/b) for a,b in zip(cert["operator"],target)]
        assert ratios[0]==ratios[1]==ratios[2]
        common=ratios[0]
        primitive=sp.factor(cert["primitive"]/common)
        out.update({"status":"exact_closed","actual_operator_order":cert["order"],
          "operator_low_to_high":[str(a) for a in target],
          "raw_common_ratio_to_chapter4":str(common),
          "reduced_matrix_shape":list(cert["matrix"].shape),
          "primitive":str(primitive),"primitive_chars":len(str(primitive)),
          "exact_residual":"0"})
    else:
        out.update({"status":"blocked_no_relation_through_order_2",
                    "reduced_matrix_shape":list(cert["matrix"].shape)})
    target_path=DATA_ROOT/"examples/sphere_curves/icosahedral_search.json"
    target_path.write_text(json.dumps(out,indent=2)+"\n")
    print("ICOSAHEDRAL_SEARCH",out["status"])
    print("matrix",out["reduced_matrix_shape"],"seconds",seconds)
    if out["status"]=="exact_closed":
        print("operator",out["operator_low_to_high"])
        print("primitive_chars",out["primitive_chars"],"exact_residual=0")

if __name__=="__main__":main()
