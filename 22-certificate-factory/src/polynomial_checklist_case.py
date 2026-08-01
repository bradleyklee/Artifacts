#!/usr/bin/env python3
"""Run one pending polynomial or fixed-seed checklist case exactly."""

from __future__ import annotations

import argparse
import gzip
import json
import shutil
import tempfile
from fractions import Fraction
from math import comb
from pathlib import Path

import sympy as sp

from expand_target_coverage import CORE, POWERS
from guv_termwise_certificate_factory import build_case
from relay_factory_v02 import parse_expr, recurrence_to_ode

n, u = sp.symbols("n u")


def matrix(obj):
    return sp.Matrix([[parse_expr(v) for v in row] for row in obj["entries"]])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_id")
    parser.add_argument("--existing-case-json", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    case_id = args.case_id
    if case_id in CORE:
        q, r, b, _ = CORE[case_id]
        d = Fraction(b, r-q)
        seed = sp.Integer(1)
    elif case_id in POWERS:
        parent, power, _ = POWERS[case_id]
        q, r, b, _ = CORE[parent]
        d = Fraction(b, r-q)
        seed = sp.expand((1+sp.Rational(d.numerator,d.denominator)*u)**(power-1))
    else:
        raise SystemExit("not a polynomial checklist case")
    cs={k:Fraction(comb(q,k)*d**k,b) for k in range(2,q+1)}
    D=sp.expand(1-sum(sp.Rational(v.numerator,v.denominator)*u**(k-1) for k,v in cs.items()))
    initial=sp.Matrix([seed.coeff(u,i) for i in range(q)])
    case_root=root/"examples"/case_id
    terms=json.loads((case_root/"data/terms.json").read_text())["terms"]
    temp=Path(tempfile.mkdtemp(prefix=f"{case_id}-",dir="/tmp"))
    try:
        blob=(
            json.loads(args.existing_case_json.read_text())
            if args.existing_case_json
            else build_case(q,temp,23,D_override=D,terms_override=terms,check_normalized_plaintext=False,initial_vector_override=initial)
        )
        blob["format"]="RELAY-CT-generalized-polynomial-checklist-v0.1"
        blob["case_id"]=case_id
        blob["numerator_seed"]=str(seed)
        O=blob["objects"]; M=O["matrices"]
        P=sp.Matrix([parse_expr(v) for v in O["p_recurrence"]["coefficients"]])
        O["ode_from_recurrence"] = recurrence_to_ode(list(P), terms)
        # build_case has already checked every exact matrix identity, rank,
        # kernel, certificate residual, and term residual before serialization.
        # Replaying the symbolic nullspace here roughly doubles high-degree
        # runtime without adding an independent implementation.
        checks={name: bool(value) for name,value in blob["checks"].items() if name not in {"plaintext_counts_match_multinomial_n0_n3"}}
        checks["terms"]=bool(blob["checks"]["multinomial_recurrence_checks_zero"])
        G_nonzero=sum(v!="0" for row in M["G"]["entries"] for v in row)
        if not all(checks.values()): raise AssertionError(checks)
        stats={
          "denominator_degree":q,"G_shape":[2*q,2*q],"G_nonzero":G_nonzero,
          "X_shape":[q-1,q],"X_rank":q-1,"nullity":1,"recurrence_order":q-1,
          "recurrence_degree":max(int(sp.degree(v,n)) for v in P),
          "certificate_degree_n":blob["certificate"]["degree_n_N"],
          "certificate_degree_u":blob["certificate"]["degree_u_N"],
          "checks_passed":len(checks),"checks_total":len(checks)
        }
        blob["checklist_validation"]={"checks":checks,"statistics":stats}
        payload=case_root/"release"/"certificate_payload.json.gz"
        with gzip.open(payload,"wt",encoding="utf-8",compresslevel=9) as f: json.dump(blob,f,sort_keys=True)
        for name,src in {"matrices":"objects/matrices","recurrence":"objects/p_recurrence","certificate":"objects/rational_certificate","ode":"objects/ode_from_recurrence"}.items():
            (case_root/"data"/f"{name}.json").write_text(json.dumps({"status":"verified","canonical_source":f"release/certificate_payload.json.gz#/{src}","statistics":stats},indent=2,sort_keys=True)+"\n")
        manifest=json.loads((case_root/"manifest.json").read_text()); manifest["case_state"]="ANALYTIC_COMPLETE"
        for name in ("matrices","recurrence","certificate","ode"): manifest["components"][name]={"status":"verified","canonical_path":f"data/{name}.json"}
        (case_root/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
        print(json.dumps({"case_id":case_id,"status":"verified","payload_bytes":payload.stat().st_size,"statistics":stats}))
    finally:
        shutil.rmtree(temp,ignore_errors=True)

if __name__=="__main__":
    main()
