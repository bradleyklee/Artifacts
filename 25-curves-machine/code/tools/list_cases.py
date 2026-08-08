#!/usr/bin/env python3
import json
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
data = json.loads((repo / 'examples/catalog.json').read_text())
for c in data['cases']:
    marker = ' showcase' if c.get('showcase') else ''
    print(f"{c['case_id']:6} {c['domain']:10} {c['status']:30} {c['display_name']}{marker}")
