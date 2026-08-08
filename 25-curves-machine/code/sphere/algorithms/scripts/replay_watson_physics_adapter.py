#!/usr/bin/env python3
from __future__ import annotations
import os
import json,pathlib,sys
import sympy as sp

ROOT=pathlib.Path(__file__).resolve().parents[2]
DATA_ROOT=pathlib.Path(os.environ.get('CURVES_MACHINE_DATA_ROOT', str(ROOT/'data')))
sys.path.insert(0,str(ROOT/"algorithms/src/core"))
import watson_physics_adapter as w


def main():
    w.self_check()
    cases={
      "A_through_quartic":w.combine(w.rigid_harmonics(),w.A_reduction_quartic_harmonics()),
      "A_through_sextic":w.combine(w.rigid_harmonics(),w.A_reduction_quartic_harmonics(),w.A_reduction_sextic_harmonics()),
      "S_through_quartic":w.combine(w.rigid_harmonics(),w.S_reduction_quartic_harmonics()),
      "S_through_sextic":w.combine(w.rigid_harmonics(),w.S_reduction_quartic_harmonics(),w.S_reduction_sextic_harmonics())}
    out={"fixed_J_convention":"J^2=L2, p=J_a, transverse ladder J_+=J_b+iJ_c",
         "quantum_to_classical":"anticommutators replaced by twice the commuting product; this is the principal symbol",
         "watson_1968":w.watson_1968_parent_hamiltonian_metadata(),
         "cases":{name:{"harmonic_support":sorted(tab),
                         "algorithm_class":"DihedralODE" if set(tab)<={0,2}
                                           else "general implicit-angle reduction",
                         "coefficients":{str(k):str(v) for k,v in tab.items()}}
                  for name,tab in cases.items()}}
    path=DATA_ROOT/"examples/sphere_curves/watson_physics_adapter.json"
    path.write_text(json.dumps(out,indent=2)+"\n")
    print("WATSON_PHYSICS_REPLAY_PASS")
    for k,v in out["cases"].items(): print(k,v["harmonic_support"],v["algorithm_class"])


if __name__=="__main__": main()
