#!/usr/bin/env bash
set -euo pipefail

R="${1:-5}"
OUTDIR="${2:-out}"
SOLVER="${SOLVER:-}"

mkdir -p "$OUTDIR"

echo "Generating SAT CNF for radius $R..."
python3 spectre_sat.py cnf \
  --radius "$R" \
  --out "$OUTDIR/r${R}.cnf"

echo "Solving..."
if [[ -n "$SOLVER" ]]; then
  python3 spectre_sat.py solve \
    --solver "$SOLVER" \
    --cnf "$OUTDIR/r${R}.cnf" \
    --model "$OUTDIR/r${R}.model"
else
  python3 spectre_sat.py solve \
    --cnf "$OUTDIR/r${R}.cnf" \
    --model "$OUTDIR/r${R}.model"
fi

echo "Decoding model..."
python3 spectre_sat.py decode \
  --model "$OUTDIR/r${R}.model" \
  --map "$OUTDIR/r${R}.map" \
  --out "$OUTDIR/r${R}.dat"

echo "Drawing SVG..."
python3 spectre_sat.py draw \
  --dat "$OUTDIR/r${R}.dat" \
  --out "$OUTDIR/r${R}.svg"

echo "wrote $OUTDIR/r${R}.svg"
