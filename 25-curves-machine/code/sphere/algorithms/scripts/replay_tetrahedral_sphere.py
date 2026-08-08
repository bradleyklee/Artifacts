#!/usr/bin/env python3
"""Independently derive the Chapter-4 tetrahedral period certificate."""
from __future__ import annotations
import os
import json,pathlib,sys,time
import sympy as sp

ROOT=pathlib.Path(__file__).resolve().parents[2]
DATA_ROOT=pathlib.Path(os.environ.get('CURVES_MACHINE_DATA_ROOT', str(ROOT/'data')))
sys.path.insert(0,str(ROOT/"algorithms/src/core"))
import dihedral_ode_sphere as d


def main():
    model=d.tetrahedral()
    kernel=d.dissertation_kernel(model)
    started=time.monotonic()
    result=d.adaptive_numerator_search(
        model,order=2,operator_alpha_degree=3,numerator_alpha_degree=3,
        start_lambda_degree=0,max_lambda_degree=12,time_limit_seconds=180)
    seconds=time.monotonic()-started
    if result["status"]!="closed":
        payload={"status":"blocked","model":"tetrahedral",
                 "hamiltonian":"3*sqrt(3)*Jx*Jy*Jz",
                 "kernel_shape":list(kernel["G"].shape),
                 "kernel_determinant":str(kernel["determinant"]),
                 "history":result["history"],"seconds":seconds}
    else:
        target=[8*d.alpha,-9*(1-3*d.alpha**2),
                -9*d.alpha*(1-d.alpha**2)]
        ratios=[sp.cancel(a/b) for a,b in zip(result["operator"],target)]
        assert ratios[0]==ratios[1]==ratios[2]
        common_ratio=ratios[0]
        op=target
        normalized_R=sp.factor(result["R"]/common_ratio)
        payload={"status":"exact_closed","model":"tetrahedral",
          "hamiltonian":"3*sqrt(3)*Jx*Jy*Jz",
          "angle_form":"(3*sqrt(3)/2)*lambda*(1-lambda^2)*cos(2*phi)",
          "operator_order":2,"operator_low_to_high":[str(a) for a in op],
          "raw_operator_common_ratio_to_chapter4":str(common_ratio),
          "primitive_R":str(normalized_R),"primitive":"lambda_dot*R",
          "exact_residual":"0","closing_lambda_degree":result["lambda_degree"],
          "matrix_shape":list(result["matrix"].shape),
          "kernel_shape":list(kernel["G"].shape),
          "kernel_determinant":str(kernel["determinant"]),
          "history":result["history"],"seconds":seconds}
    target_path=DATA_ROOT/"examples/sphere_curves/tetrahedral_exact_certificate.json"
    target_path.write_text(json.dumps(payload,indent=2)+"\n")
    print("TETRAHEDRAL_SPHERE",payload["status"])
    print("seconds",seconds)
    if payload["status"]=="exact_closed":
        print("matrix",payload["matrix_shape"],"lambda_degree",payload["closing_lambda_degree"])
        print("operator",payload["operator_low_to_high"])
        print("exact_residual=0")

if __name__=="__main__":main()
