#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
AUDIT="$ROOT/audit"
mkdir -p "$AUDIT"
cd "$ROOT/src"
python3 numerical_audit.py | tee "$AUDIT/numerical_audit.log"
python3 curved_area_audit.py | tee "$AUDIT/curved_area_audit.log"
python3 mesh_area_audit.py | tee "$AUDIT/mesh_area_audit.log"
python3 verify_trefoil.py | tee "$AUDIT/verify.log"
"$ROOT/geometries/cyclic_R3_trefoil/verify.sh"
