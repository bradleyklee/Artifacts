#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
python src/verify_exact_specializations.py
python src/verify_modular_series.py
echo "All universal cubic checks passed."
