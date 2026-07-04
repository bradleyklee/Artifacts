#!/usr/bin/env python3
"""Seal one completed exact 1,000-event run into a self-describing tar.gz block.

The input run directory must have been produced by v2 `burner run`; it provides
explicit start_state.json and end_state.json.  The sealed archive intentionally
contains only evidence needed to inspect this one block, not campaign logs or
live reporting artifacts.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, os, shutil, subprocess, sys, tarfile, tempfile
from pathlib import Path

KEEP = ("start_state.json", "end_state.json", "ledger.ndjson.gz", "pair_faces.csv", "manifest.json", "summary.json")

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20), b''): h.update(b)
    return h.hexdigest()

def run_checked(cmd: list[str], cwd: Path) -> None:
    p=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True)
    if p.returncode:
        raise RuntimeError(f"failed: {' '.join(cmd)}\n{p.stdout}\n{p.stderr}")

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('run_dir',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--name',required=True,help='e.g. d12_000001_001000')
    ap.add_argument('--repo',type=Path,default=Path('.'))
    ap.add_argument('--expect-events',type=int,default=1000)
    args=ap.parse_args()
    repo=args.repo.resolve(); run=args.run_dir.resolve()
    missing=[x for x in KEEP if not (run/x).exists()]
    if missing: raise SystemExit(f"missing required v2 run artifacts: {missing}")
    summary=json.loads((run/'summary.json').read_text())
    if summary.get('event_batches') != args.expect_events:
        raise SystemExit(f"expected {args.expect_events} events, found {summary.get('event_batches')}")
    with tempfile.TemporaryDirectory(prefix='.seal-',dir=args.out.parent.resolve()) as td:
        root=Path(td)/args.name; root.mkdir(parents=True)
        for rel in KEEP: shutil.copy2(run/rel,root/rel)
        # Dense complexity is derived once at seal time, and becomes a portable
        # data product.  It contains no display-only decimal time column.
        run_checked([sys.executable,'tools/time_parts_series.py',str(root/'ledger.ndjson.gz'),'--csv',str(root/'complexity.csv')],repo)
        # Remove the noncanonical decimal display column for a smaller, exact-only block.
        rows=[]
        with (root/'complexity.csv').open(newline='',encoding='utf-8') as f:
            for row in csv.DictReader(f):
                row.pop('physical_time_display',None); rows.append(row)
        with gzip.open(root/'complexity.csv.gz','wt',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        (root/'complexity.csv').unlink()
        run_checked([sys.executable,'tools/audit_single_surface.py',str(root/'ledger.ndjson.gz'),str(root/'summary.json'),'--expect-batches',str(args.expect_events),'--out',str(root/'single_surface_audit.json')],repo)
        manifest=json.loads((root/'manifest.json').read_text())
        start=json.loads((root/'start_state.json').read_text())
        end=json.loads((root/'end_state.json').read_text())
        block={
          'schema':'exact-two-body-block/v2', 'name':args.name,
          'events':args.expect_events,
          'geometry':{'model':manifest['model'],'container':manifest['container'],'physics':manifest['physics'],'stopping_rule':manifest['stopping_rule']},
          'start':{'step':start['step'],'exact_T':start['exact_T'],'state_hash':start['state_hash']},
          'end':{'step':end['step'],'exact_T':end['exact_T'],'state_hash':end['state_hash']},
          'canonical_evidence':['start_state.json','end_state.json','ledger.ndjson.gz','pair_faces.csv','complexity.csv.gz','single_surface_audit.json'],
          'note':'This archive is self-describing. Verify checksums and replay/audit it without any campaign-wide index.'
        }
        (root/'BLOCK.json').write_text(json.dumps(block,indent=2,sort_keys=True)+'\n')
        names=sorted(p.name for p in root.iterdir() if p.is_file())
        sums=''.join(f'{sha256(root/n)}  {n}\n' for n in names)
        (root/'SHA256SUMS').write_text(sums)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        with tarfile.open(args.out,'w:gz') as tf: tf.add(root,arcname=args.name)
    print(json.dumps({'block':str(args.out),'name':args.name,'events':args.expect_events},sort_keys=True))
    return 0
if __name__=='__main__': raise SystemExit(main())
