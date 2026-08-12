#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="$ROOT/src"
DIST="$ROOT/dist"
AUDIT="$ROOT/audit"
mkdir -p "$DIST" "$AUDIT" "$SRC/.mplconfig"

cd "$SRC"
python3 make_figures.py
cd "$ROOT"
./verify.sh
"$ROOT/geometries/cyclic_R3_trefoil/build.sh"

cd "$SRC"
sed 's/{trefoil_certificate_v4.tex}/{trefoil_certificate.tex}/g' \
  trefoil_certificate.tex > trefoil_certificate_build.tex
pdflatex -interaction=nonstopmode -halt-on-error trefoil_certificate_build.tex \
  > "$AUDIT/pdflatex_pass1.log"
pdflatex -interaction=nonstopmode -halt-on-error trefoil_certificate_build.tex \
  > "$AUDIT/pdflatex_pass2.log"
cp trefoil_certificate_build.pdf "$DIST/trefoil_symplectic_period_certificate.pdf"
rm -f trefoil_certificate_build.{aux,log,out,tex,pdf}

if command -v pdfinfo >/dev/null 2>&1; then
  pdfinfo "$DIST/trefoil_symplectic_period_certificate.pdf" > "$AUDIT/preflight.txt"
else
  echo "PDF built successfully; pdfinfo not installed." > "$AUDIT/preflight.txt"
fi

echo "Built: $DIST/trefoil_symplectic_period_certificate.pdf"
