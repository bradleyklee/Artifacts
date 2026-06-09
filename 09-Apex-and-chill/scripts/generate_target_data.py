#!/usr/bin/env python3
"""Generate DH12/ordinary/tree/split target data from the bundled C6 REPHEX target catalogue.

The bundled mechanics file reads REPHEX replacement-rule target data from
mechanics/c6_rephex_catalogues_v2/raw_targets/F_L*. The script normalizes that
into JSON/CSV files that are easy for downstream search/render scripts to use.
"""
import argparse, csv, json, importlib.util
from pathlib import Path

def load_mechanics(root: Path):
    path=root/'mechanics'/'generic_c6_bootstrap_shot.py'
    spec=importlib.util.spec_from_file_location('generic_c6_bootstrap_shot', path)
    g=importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
    g.BASE=root/'mechanics'/'c6_rephex_catalogues_v2'
    return g

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root', default=Path(__file__).resolve().parents[1], type=Path)
    ap.add_argument('--model', default='dh12', choices=['dh12','ordinary','tree','split'])
    ap.add_argument('--level', default=5, type=int)
    ap.add_argument('--outdir', default=None)
    args=ap.parse_args()
    root=args.root.resolve(); outdir=Path(args.outdir) if args.outdir else root/'data'/'targets'
    outdir.mkdir(parents=True, exist_ok=True)
    g=load_mechanics(root)
    target=g.target_for(args.model,args.level)
    rows=[{'q':q,'r':r,'label':lab} for (q,r),lab in sorted(target.items(), key=lambda x:(x[0][1],x[0][0]))]
    stem=f'{args.model}_target_L{args.level}'
    (outdir/f'{stem}.json').write_text(json.dumps({'model':args.model,'level':args.level,'cells':len(rows),'target':rows}, indent=2))
    with open(outdir/f'{stem}.csv','w',newline='') as f:
        w=csv.DictWriter(f, fieldnames=['q','r','label']); w.writeheader(); w.writerows(rows)
    print(json.dumps({'model':args.model,'level':args.level,'cells':len(rows),'json':str(outdir/f'{stem}.json'),'csv':str(outdir/f'{stem}.csv')}, indent=2))
if __name__=='__main__': main()
