#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

def validate_tree(case_root: Path) -> None:
    json_count = 0
    for p in case_root.rglob('*.json'):
        json.loads(p.read_text(encoding='utf-8'))
        json_count += 1
    print(f'CASE_DATA_PARSE_PASS json_files={json_count}')

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('case_id')
    ap.add_argument('--full', action='store_true')
    ap.add_argument('--list', action='store_true')
    args = ap.parse_args()
    catalog = json.loads((REPO/'examples/catalog.json').read_text())
    hits = [c for c in catalog['cases'] if c['case_id']==args.case_id]
    if not hits:
        print(f'unknown case_id: {args.case_id}', file=sys.stderr)
        return 2
    entry = hits[0]
    case_root = REPO/entry['path']
    meta = json.loads((case_root/'case.json').read_text())
    validate_tree(case_root)
    commands = meta.get('replay_commands',[])
    if args.list:
        for item in commands:
            print(item)
        return 0
    ran = 0
    for item in commands:
        if item.get('cost')=='long' and not args.full:
            print(f"SKIP_LONG {item['label']}")
            continue
        print(f"RUN {item['label']}: {item['command']}")
        proc = subprocess.run(item['command'], cwd=REPO/item['cwd'], shell=True)
        if proc.returncode:
            print(f"CASE_REPLAY_FAIL label={item['label']} returncode={proc.returncode}")
            return proc.returncode
        ran += 1
    print(f"CASE_REPLAY_PASS case_id={args.case_id} commands={ran}")
    return 0

if __name__=='__main__':
    raise SystemExit(main())
