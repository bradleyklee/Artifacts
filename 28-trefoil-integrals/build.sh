#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="$ROOT/src"
DIST="$ROOT/dist"
AUDIT="$ROOT/audit"
mkdir -p "$DIST" "$AUDIT" "$SRC/.mplconfig"

cd "$SRC"
python3 make_figures.py
python3 numerical_audit.py | tee "$AUDIT/numerical_audit.log"
python3 verify_trefoil.py | tee "$AUDIT/verify.log"

# The source name inside the package is simplified, so build a temporary
# LaTeX copy with the embedded-source filename adjusted accordingly.
sed 's/{trefoil_certificate_v4.tex}/{trefoil_certificate.tex}/g' \
  trefoil_certificate.tex > trefoil_certificate_build.tex
pdflatex -interaction=nonstopmode -halt-on-error trefoil_certificate_build.tex \
  > "$AUDIT/pdflatex_pass1.log"
pdflatex -interaction=nonstopmode -halt-on-error trefoil_certificate_build.tex \
  > "$AUDIT/pdflatex_pass2.log"
cp trefoil_certificate_build.pdf "$DIST/trefoil_symplectic_period_certificate.pdf"
rm -f trefoil_certificate_build.{aux,log,out,tex,pdf}

python /home/oai/skills/pdfs/scripts/pdf_preflight.py \
  "$DIST/trefoil_symplectic_period_certificate.pdf" \
  > "$AUDIT/preflight.txt"

echo "Built: $DIST/trefoil_symplectic_period_certificate.pdf"
