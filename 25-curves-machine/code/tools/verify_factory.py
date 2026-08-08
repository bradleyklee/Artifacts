#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--smoke',action='store_true',help='rerun a small representative subset')
    ap.add_argument('--full',action='store_true',help='also request long case replays')
    args=ap.parse_args()
    catalog=json.loads((REPO/'examples/catalog.json').read_text())
    ids=set()
    json_count=0
    py_count=0
    for c in catalog['cases']:
        assert c['case_id'] not in ids
        ids.add(c['case_id'])
        root=REPO/c['path']
        meta=json.loads((root/'case.json').read_text())
        reps=set(meta['representations'])
        actual={p.parent.name.split('_',1)[0] for p in (root/'representations').glob('*/representation.json')}
        assert reps==actual,(c['case_id'],reps,actual)
        for p in root.rglob('*.json'):
            json.loads(p.read_text(encoding='utf-8')); json_count+=1
    for p in (REPO/'code').rglob('*.py'):
        if '__pycache__' in p.parts: continue
        compile(p.read_text(encoding='utf-8'), str(p), 'exec'); py_count+=1
    for name in ['triangle_rectangle','circle_triangle_square','square_hexagon']:
        pdf=REPO/'showcase'/name/'certificate.pdf'
        assert pdf.is_file() and pdf.stat().st_size>10000
    smoke=[]
    if args.smoke or args.full:
        smoke=['P0001','S0003','S0004','S0005']
    if args.full:
        smoke += ['P0002','P0003','P0004','P0006','P0007']
    for cid in smoke:
        cmd=[sys.executable,str(REPO/'code/tools/run_case.py'),cid]
        if args.full: cmd.append('--full')
        subprocess.run(cmd,cwd=REPO,check=True)
    print(f'FACTORY_VERIFY_PASS cases={len(catalog["cases"])} json_files={json_count} python_files={py_count}')
    return 0
if __name__=='__main__': raise SystemExit(main())
