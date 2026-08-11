#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/src"
python3 numerical_audit.py
python3 verify_trefoil.py
