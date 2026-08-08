#!/usr/bin/env python3
"""Emit Pierre Lairez `periods` inputs from Klee plane-curve case JSON.

Lairez attribution: the generated Magma scripts call Pierre Lairez's
Rham--Koszul/Griffiths--Dwork `Periods` implementation (2014 repository;
Math. Comp. 85 (2016), 1719--1752).
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def magma_expr(expr: str) -> str:
    """Translate the deliberately small case-expression dialect to Magma."""
    if not re.fullmatch(r"[A-Za-z0-9_+*/^(). -]+", expr):
        raise ValueError(f"unsupported character in expression: {expr!r}")
    return expr.replace("^", "^")


def load_case(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "name", "variables", "parameter", "energy_E_equals_2H",
        "lairez_input",
    }
    missing = sorted(required - data.keys())
    if missing:
        raise ValueError(f"{path}: missing {missing}")
    if data["variables"] != ["p", "q"] or data["parameter"] != "alpha":
        raise ValueError("current adapter expects parameter alpha and variables p,q")
    return data


def emit_magma(case: dict) -> str:
    E = magma_expr(case["energy_E_equals_2H"])
    name = case["name"]
    order = case.get("known_operator_order", "UNKNOWN")
    free = case.get("free_coefficients", [])
    if free:
        coefficient_setup = (f'K<{",".join(free)}> := FunctionField(Rationals(), {len(free)});\n'
                             'A<alpha,p,q> := FunctionField(K, 3);')
    else:
        coefficient_setup = 'A<alpha,p,q> := FunctionField(Rationals(), 3);'
    return f'''// Generated comparison input for {name}.
// Pierre Lairez attribution: Periods/Rham-Koszul/Picard-Fuchs machinery,
// https://github.com/lairez/periods ; Math. Comp. 85 (2016), 1719-1752.
// Research case and action-period normalization: Bradley Klee.

spec := GetEnv("PERIODS_SPEC");
require #spec gt 0: "Set PERIODS_SPEC to periods/src/PF.spec";
AttachSpec(spec);
SetVerbose("User2", true);
SetAssertions(2);

{coefficient_setup}
E := {E};

// Poincare-residue bridge:
// rho=(2H)_p=2H_p; Res_{{2H=alpha}} 2 dp dq/(2H-alpha)
// equals 2 dq/rho = dq/H_p.
f := 2/(E-alpha);

printf "CASE {name} KNOWN_ORDER {order}\\n";
for r in [1..4] do
    printf "TRY_R %o\\n", r;
    time L := Periods(f : r := r);
    printf "RESULT_R %o OPERATOR %o\\n", r, L;
    printf "RESULT_R %o ORDER %o\\n", r, Degree(L);
end for;

// The public interface accepts \"cert\", but currently returns only L.
// This run is retained because it exercises the certificate-carrying reducer.
time Lcertpath := Periods(f : r := 2, variant := {{"cert"}});
printf "CERT_PATH_OPERATOR %o\\n", Lcertpath;
'''


def write_case(path: Path, outdir: Path) -> Path:
    case = load_case(path)
    outdir.mkdir(parents=True, exist_ok=True)
    target = outdir / f"{case['name']}.m"
    target.write_text(emit_magma(case), encoding="utf-8")
    return target


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("case", nargs="?", type=Path)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", type=Path, default=ROOT / "generated")
    ns = ap.parse_args()
    paths = sorted((ROOT / "cases").glob("*.json")) if ns.all else [ns.case]
    if not paths or paths == [None]:
        ap.error("give a case JSON or --all")
    for path in paths:
        print(write_case(path, ns.out))


if __name__ == "__main__":
    main()
