#!/usr/bin/env python3
"""Time and save each reduced derivative column separately."""
from __future__ import annotations
import os
import argparse,json,pathlib,signal,sys,time
import sympy as sp
ROOT=pathlib.Path(__file__).resolve().parents[2]
DATA_ROOT=pathlib.Path(os.environ.get('CURVES_MACHINE_DATA_ROOT', str(ROOT/'data')))
sys.path.insert(0,str(ROOT/"algorithms/src/core"))
import icosahedral_sphere as ico
from hyperelliptic_period_reduction import HyperellipticPeriodReducer,even_power_substitution,x,alpha

PERT={"z2":ico.lam**2,"z":ico.lam,"z_plus_2z2":ico.lam+2*ico.lam**2}

def save(path,out):path.write_text(json.dumps(out,indent=2)+"\n")

def main():
    ap=argparse.ArgumentParser();ap.add_argument("model",choices=PERT);ap.add_argument("--max-order",type=int,default=6);a=ap.parse_args()
    h1=sp.expand(ico.h1()+PERT[a.model]);h2sq=4*ico.lam**2*(1-ico.lam**2)**5
    P=sp.expand(-25*((alpha-h1)**2-h2sq)).subs(ico.lam,x)
    even=all(m[0]%2==0 for m,c in sp.Poly(P,x,alpha).terms() if c)
    R=even_power_substitution(P) if even else P
    reducer=HyperellipticPeriodReducer(R);forms=reducer.raw_tower_forms(a.max_order)
    path=DATA_ROOT/f"examples/sphere_curves/icosahedral_perturbation_{a.model}_columns.json"
    out={"status":"running","model":a.model,"even_power_substitution":even,
         "reduction_degree":reducer.degree,"requested_max_order":a.max_order,"columns":[]}
    save(path,out)
    def stop(signum,frame):
        out["status"]="blocked_external_time_limit";out["blocked_during_order"]=len(out["columns"]);save(path,out);raise SystemExit(124)
    signal.signal(signal.SIGTERM,stop)
    vectors=[]
    for order,(k,f) in enumerate(forms):
        tick=time.monotonic();v,_=reducer.reduce_form(k,f,track_primitive=False);seconds=time.monotonic()-tick
        vectors.append(v);M=sp.Matrix.hstack(*(sp.Matrix(q) for q in vectors))
        rank=M.rank();rec={"order":order,"seconds":seconds,"matrix_shape":list(M.shape),"rank":rank,"nullity":M.cols-rank}
        out["columns"].append(rec);save(path,out);print(rec,flush=True)
        if rank<M.cols:
            out["status"]="relation_detected_operator_pending";out["first_relation_order"]=order;save(path,out)
            tick=time.monotonic();relation=M.nullspace()[0];null_seconds=time.monotonic()-tick
            out["status"]="relation_detected"
            out["raw_null_relation_low_to_high"]=[str(sp.factor(q)) for q in relation]
            out["nullspace_seconds"]=null_seconds;save(path,out);break
    else:out["status"]="no_relation_through_requested_order";save(path,out)
    print("COLUMN_SCREEN",out["status"])

if __name__=="__main__":main()
