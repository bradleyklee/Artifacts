#!/bin/sh
set -eu
PYTHON=${PYTHON:-.venv/bin/python}
"$PYTHON" pierre_periods_comparison/lairez_port.py \
  pierre_periods_comparison/cases/triangle_square.json --max-order 5
"$PYTHON" pierre_periods_comparison/lairez_port.py \
  pierre_periods_comparison/cases/square_hexagon.json --max-order 6

