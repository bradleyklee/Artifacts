#!/usr/bin/env python3
"""Merge the independently verified A244856 order-4 certificate."""
from __future__ import annotations
import json,shutil
from pathlib import Path
import sympy as sp
from relay_factory_v02 import recurrence_to_ode
n=sp.symbols("n")
def main():
 root=Path(__file__).resolve().parents[1]
 attached=Path("/tmp/a244856-attached/A244856_typogeometry_certificate_v1")
 case=root/"examples/A244856"; prov=case/"provenance/attached_typogeometry_certificate_v1"
 if prov.exists(): shutil.rmtree(prov)
 shutil.copytree(attached,prov)
 cert=json.loads((attached/"payload/certificate.json").read_text())
 P=[sp.sympify(v,locals={"n":n}) for v in cert["recurrence"]["p"]]
 terms=json.loads((case/"data/terms.json").read_text())["terms"]
 residuals=[sum(int(P[j].subs(n,k))*terms[k+j] for j in range(5)) for k in range(len(terms)-4)]
 assert all(v==0 for v in residuals)
 ode=recurrence_to_ode(P,terms)
 merged={
  "status":"verified","source":"attached A244856_typogeometry_certificate_v1",
  "attachment_checks":"7 verifier groups passed",
  "recurrence":cert["recurrence"],"certificate":cert["certificate"],
  "ode_from_recurrence":ode,
  "independent_direct_x_crosscheck":"runs/A244856-direct-x-pilot/case.json",
  "claim_boundary":"order 4 is shorter than the direct-x order-5 recurrence; minimality is not claimed"
 }
 out=case/"release/attached_order4_certificate.json";out.write_text(json.dumps(merged,indent=2,sort_keys=True)+"\n")
 for name,fragment in {"recurrence":"recurrence","certificate":"certificate","ode":"ode_from_recurrence"}.items():
  (case/"data"/f"{name}.json").write_text(json.dumps({"status":"verified","canonical_source":f"release/attached_order4_certificate.json#/{fragment}","independent_crosscheck":"runs/A244856-direct-x-pilot/case.json"},indent=2,sort_keys=True)+"\n")
 print(json.dumps({"case_id":"A244856","attached_recurrence_order":4,"direct_x_recurrence_order":5,"stored_term_residuals":max(map(abs,residuals),default=0)}))
if __name__=="__main__":main()
