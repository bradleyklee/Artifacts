#!/usr/bin/env python3
"""Run one icosahedral perturbation and save every completed order test."""
from __future__ import annotations
import os
import argparse,json,pathlib,signal,sys,time
import sympy as sp

ROOT=pathlib.Path(__file__).resolve().parents[2]
DATA_ROOT=pathlib.Path(os.environ.get('CURVES_MACHINE_DATA_ROOT', str(ROOT/'data')))
sys.path.insert(0,str(ROOT/"algorithms/src/core"))
import icosahedral_sphere as ico
from hyperelliptic_period_reduction import (HyperellipticPeriodReducer,
    even_power_substitution,x,alpha)

PERTURBATIONS={
  "z2":ico.lam**2,
  "z":ico.lam,
  "z_plus_2z2":ico.lam+2*ico.lam**2,
}


def save(path,payload):
    path.write_text(json.dumps(payload,indent=2)+"\n")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("model",choices=PERTURBATIONS)
    ap.add_argument("--orders",default="2,4,6")
    args=ap.parse_args()
    addition=PERTURBATIONS[args.model]
    h1=sp.expand(ico.h1()+addition)
    h2sq=4*ico.lam**2*(1-ico.lam**2)**5
    P=sp.expand(-25*((alpha-h1)**2-h2sq)).subs(ico.lam,x)
    reduction_P=P; substitution="none"
    if all(m[0]%2==0 for m,c in sp.Poly(P,x,alpha).terms() if c):
        reduction_P=even_power_substitution(P)
        substitution="u=lambda^2; Q(u)=u*P(sqrt(u))"
    out={"status":"running","base":"normalized icosahedral sextic",
      "perturbation":args.model,"addition":str(addition),"h1":str(h1),
      "h2_squared":str(h2sq),"eliminated_P":str(P),
      "P_degree_lambda":int(sp.degree(P,x)),
      "reduction_method":"two pass: relation first, one exact derivative second",
      "reduction_substitution":substitution,
      "reduction_P":str(reduction_P),
      "reduction_P_degree":int(sp.degree(reduction_P,x)),"completed_order_tests":[]}
    target=DATA_ROOT/f"examples/sphere_curves/icosahedral_perturbation_{args.model}.json"
    save(target,out)
    def stop_handler(signum,frame):
        out["status"]="blocked_external_time_limit"
        out["blocker"]="process stopped during the next requested order; completed tests retained"
        save(target,out)
        raise SystemExit(124)
    signal.signal(signal.SIGTERM,stop_handler)
    for cap in [int(z) for z in args.orders.split(",")]:
        started=time.monotonic()
        cert=HyperellipticPeriodReducer(reduction_P).two_pass_polynomial_certificate(max_order=cap)
        seconds=time.monotonic()-started
        rec={"tested_through_order":cap,"status":cert["status"],
             "matrix_shape":list(cert["matrix"].shape),"seconds":seconds}
        if cert["status"]=="closed":
            rec.update({"actual_operator_order":cert["order"],
              "operator_low_to_high":[str(a) for a in cert["operator"]],
              "primitive":str(cert["primitive"]),
              "primitive_chars":len(str(cert["primitive"])),"exact_residual":"0"})
        out["completed_order_tests"].append(rec)
        out["status"]="exact_closed" if cert["status"]=="closed" else "running"
        save(target,out)
        print(args.model,rec,flush=True)
        if cert["status"]=="closed":break
    if out["status"]!="exact_closed":out["status"]="blocked_at_requested_order_cap"
    save(target,out)
    print("ICOSAHEDRAL_PERTURBATION",out["status"],target)

if __name__=="__main__":main()
