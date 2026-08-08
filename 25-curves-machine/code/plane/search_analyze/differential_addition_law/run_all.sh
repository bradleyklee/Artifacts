#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 derive_cubic_addition.py
python3 verify_edwards_quartic.py
python3 quartic_addition_search.py > quartic_search_pseudocode.txt
