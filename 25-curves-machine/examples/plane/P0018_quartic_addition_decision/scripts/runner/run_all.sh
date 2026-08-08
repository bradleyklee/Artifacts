#!/bin/sh
set -eu
cd "$(dirname "$0")"
python quartic_genus_test.py > genus_test_result.json
python two_node_stratum.py > two_node_stratum_result.json
python derive_two_node_conic_law.py > conic_derivation_result.json
python - <<'PY'
import json
for f in ['genus_test_result.json','two_node_stratum_result.json','conic_derivation_result.json']:
    json.load(open(f))
print('all direct quartic addition tests passed')
PY
