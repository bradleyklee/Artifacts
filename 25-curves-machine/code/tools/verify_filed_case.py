#!/usr/bin/env python3
from __future__ import annotations
import csv
import json
import sys
from pathlib import Path
import sympy as sp

REPO = Path(__file__).resolve().parents[2]

def main() -> int:
    if len(sys.argv) != 2:
        print('usage: verify_filed_case.py CASE_ID', file=sys.stderr)
        return 2
    case_id = sys.argv[1]
    catalog = json.loads((REPO/'examples/catalog.json').read_text())
    rows = [x for x in catalog['cases'] if x['case_id'] == case_id]
    if not rows:
        raise SystemExit(f'unknown case {case_id}')
    root = REPO/rows[0]['path']
    result_root = root/'results'
    files = [p for p in result_root.rglob('*') if p.is_file()]
    assert files, f'no filed results for {case_id}'
    parsed = 0
    operator_blocks = 0
    alpha = sp.symbols('alpha')
    for path in files:
        assert path.stat().st_size > 0
        if path.suffix == '.json':
            data = json.loads(path.read_text())
            parsed += 1
            if isinstance(data, dict):
                for key in ('operator_coefficients','operator_coefficients_low_to_high','operator_low_to_high','operator'):
                    vals = data.get(key)
                    if isinstance(vals, list) and vals and all(isinstance(v, str) for v in vals):
                        for v in vals:
                            sp.sympify(v.replace('^','**'), locals={'alpha': alpha})
                        operator_blocks += 1
        elif path.suffix == '.csv':
            with path.open(newline='') as f:
                assert list(csv.reader(f)), f'empty CSV {path}'
    print(f'FILED_CASE_VERIFY_PASS case_id={case_id} files={len(files)} json={parsed} operator_blocks={operator_blocks}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
