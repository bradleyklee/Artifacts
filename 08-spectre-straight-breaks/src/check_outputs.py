#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from spectre_straight import ROOT

summary = json.loads((ROOT / 'data' / 'straight_local_join_summary.json').read_text(encoding='utf-8'))
expected = {
    'straight_path_records': 76,
    'valid_positioned_joins': 288,
    'breaking_inflated_joins': 288,
    'nonbreaking_inflated_joins': 0,
    'immediate_breaks': 25,
    'pathology_groups': 48,
}
for key, value in expected.items():
    actual = summary.get(key)
    if actual != value:
        raise SystemExit(f'FAIL: {key}: expected {value}, got {actual}')
for output in ['spectre_straight_path_rule_tables.pdf', 'spectre_straight_join_audit_5page.pdf']:
    path = ROOT / 'docs' / output
    if not path.exists() or path.stat().st_size == 0:
        raise SystemExit(f'FAIL: missing output {path}')
print('check passed:', ', '.join(f'{key}={value}' for key, value in expected.items()))
