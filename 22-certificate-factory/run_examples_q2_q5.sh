#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:-$ROOT/examples}"
mkdir -p "$OUT"
for q in 2 3 4 5; do
  echo "=== q=$q: fast path + direct Klee ODE ==="
  python3 "$ROOT/generate.py" "$q" --derive-ode-direct --output "$OUT"
done
echo "All q=2..5 examples generated and independently validated in $OUT"
