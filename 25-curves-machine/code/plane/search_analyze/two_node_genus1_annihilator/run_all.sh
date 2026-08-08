#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python two_node_annihilator.py --verify | tee verification.json
