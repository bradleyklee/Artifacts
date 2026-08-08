#!/usr/bin/env python3
"""Replay fixed-J G-operator and even prism-family structural checks."""
from __future__ import annotations
import os
import json,pathlib,sys
import sympy as sp

ROOT=pathlib.Path(__file__).resolve().parents[2]
DATA_ROOT=pathlib.Path(os.environ.get('CURVES_MACHINE_DATA_ROOT', str(ROOT/'data')))
sys.path.insert(0,str(ROOT/"algorithms/src/core"))
import physics_generating_sphere as g


def main():
    assert g.reduce_s(g.total_Dp(g.square_root_relation()))==0
    series=g.G_taylor(g.p**2,5)
    expected=(g.p**2-g.kappa*g.p**4/4+g.kappa**2*g.p**6/8
              -5*g.kappa**3*g.p**8/64+7*g.kappa**4*g.p**10/128)
    assert sp.expand(series-expected)==0
    rows=[]
    for m in (2,4,6,8):
        model=g.PhysicalPrismModel(m,1,sp.Rational(1,2),1,0,sp.Rational(1,10))
        assert model.reduce(model.Denergy(model.relation))==0
        turning=model.turning_resultant()
        rows.append({"m":m,"symmetry":f"D_{m}",
            "h2_degree_p":int(sp.degree(model.h2,g.p)),
            "rho_numerator_degree_p":int(sp.degree(
                sp.together(model.rho).as_numer_denom()[0],g.p)),
            "turning_resultant_degree_p":int(sp.degree(turning,g.p)),
            "turning_resultant_degree_energy":int(sp.degree(turning,g.energy)),
            "constraint_residual":"0"})
    octa=g.flattened_octahedral(sp.Rational(1,2),sp.Rational(1,5))
    assert octa.reduce(octa.Denergy(octa.relation))==0
    octa_stats={"axis":"octahedral fourfold z axis","residual_symmetry":"D_4",
        "h1":str(octa.h1),"h2":str(octa.h2),
        "turning_resultant_degree_p":int(sp.degree(octa.turning_resultant(),g.p)),
        "rigid_limit_added_term":"b*Jz^2"}
    out={"reference":"Tyuterev, J. Mol. Spectrosc. 151 (1992), 97-129, Eqs. 35-38",
         "physics_convention":"fixed J^2=L2; canonical pair (Jz,phi); energy=H",
         "G":"2/kappa*(sqrt(1+kappa*Jz^2)-1)",
         "G_taylor_through_Jz10":str(series),
         "watson_dictionary":{k:str(v) for k,v in g.watson_dictionary().items()},
         "even_prism_family":rows,
         "flattened_octahedral":octa_stats,
         "order2_certificate_search":{
           "operator_energy_degree":5,"numerator_energy_degree":5,
           "completed_shells":[
             {"numerator_p_degree":0,"matrix_shape":[123,30],"status":"incomplete","seconds":28.12},
             {"numerator_p_degree":1,"matrix_shape":[220,42],"status":"incomplete","seconds":36.22},
             {"numerator_p_degree":2,"matrix_shape":[220,54],"status":"incomplete","seconds":54.59}],
           "status":"blocked","next_numerator_p_degree":3,
           "note":"resource boundary, not a no-relation claim"},
         "odd_m":"rejected by the present even-component branch"}
    path=DATA_ROOT/"examples/sphere_curves/physics_generating_function_stats.json"
    path.write_text(json.dumps(out,indent=2)+"\n")
    print("PHYSICS_GENERATING_SPHERE_PASS")
    print("G_series=",series)
    for r in rows: print(r)
    print("flattened_octahedral=",octa_stats)


if __name__=="__main__": main()
