#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HERE/audit"
python3 "$HERE/src/derive_implicit_surfaces.py" | tee "$HERE/audit/implicit.log"
python3 "$HERE/src/verify_geometry.py" | tee "$HERE/audit/symbolic.log"
python3 "$HERE/src/numerical_check.py" | tee "$HERE/audit/numerical.log"
