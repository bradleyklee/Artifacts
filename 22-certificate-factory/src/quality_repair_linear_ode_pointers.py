#!/usr/bin/env python3
"""Repair canonical linear-ODE pointers for the five legacy normalized cases."""
from __future__ import annotations
import json
from pathlib import Path
CASES=("A120588","A120590","A120593","A120596","A120600")
def main():
 root=Path(__file__).resolve().parents[1]
 for a in CASES:
  cr=root/"examples"/a;blob=json.loads((cr/"case.json").read_text())
  ode=blob["objects"]["ode_from_recurrence"];assert ode["status"]=="complete"
  (cr/"data/ode.json").write_text(json.dumps({"status":"verified","canonical_source":"case.json#/objects/ode_from_recurrence","quality_repair":"replaced algebraic first-order fallback pointer with existing verified scalar linear ODE","order":ode["ordinary_derivative_form"]["order"]},indent=2,sort_keys=True)+"\n")
 print(json.dumps({"repaired_cases":list(CASES),"count":len(CASES)}))
if __name__=="__main__":main()
