#!/usr/bin/env python3
"""Read-only pair and lex-min ternary extractor for one L4,N3 certificate."""
from __future__ import annotations
import argparse, csv, itertools, json
from pathlib import Path

def pair_from_event(e: str):
    p=e.split(':')
    if len(p)==4 and p[0]=='pair':
        return tuple(sorted((p[1],p[2])))
    return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('certificate', type=Path)
    ap.add_argument('--outdir', type=Path, required=True)
    a=ap.parse_args()
    c=json.loads(a.certificate.read_text())
    if c.get('schema')!='hard-octagons-L4-N3-self-contained-certificate/v1':
        raise SystemExit('unsupported certificate schema')
    rows=c['evolution']['ledger']
    bodies=[x['id'] for x in c['instance']['initial_state']]
    if len(bodies)!=3: raise SystemExit('requires exactly three bodies')
    pairs=[]
    for row in rows:
        evs=row['events']
        ps=[pair_from_event(e) for e in evs]
        ps=[p for p in ps if p]
        if len(ps)>1:
            raise SystemExit(f"batch {row['index']} has multiple pair events; no serial word implied")
        if ps:
            pairs.append({'token_index':len(pairs)+1,'batch':row['index'],'time':row['time'],'pair':'/'.join(ps[0]),'mixed_with_wall':any(e.startswith('wall:') for e in evs),'events':evs})
    candidates=[]
    for A,B,C in itertools.permutations(bodies):
        lookup={tuple(sorted((A,B))):0,tuple(sorted((B,C))):1,tuple(sorted((C,A))):2}
        digits=[lookup[tuple(x['pair'].split('/'))] for x in pairs]
        candidates.append((tuple(digits),(A,B,C)))
    digits,mapping=min(candidates,key=lambda z:z[0])
    a.outdir.mkdir(parents=True,exist_ok=True)
    base=f"class_{c['instance']['class']}"
    with (a.outdir/f'{base}.pairs.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['token_index','batch','time_a','time_b','pair','mixed_with_wall','events'])
        for x,d in zip(pairs,digits):
            w.writerow([x['token_index'],x['batch'],x['time']['a'],x['time']['b'],x['pair'],str(x['mixed_with_wall']).lower(),'|'.join(x['events'])])
    (a.outdir/f'{base}.pairs.sequence.csv').write_text(','.join(x['pair'] for x in pairs)+'\n')
    (a.outdir/f'{base}.ternary.sequence.csv').write_text(','.join(map(str,digits))+'\n')
    summary={
      'schema':'hard-octagons-L4-N3-ternary-extraction/v1',
      'certificate':str(a.certificate), 'class':c['instance']['class'],
      'bodies':bodies, 'pair_token_count':len(pairs),
      'mixed_pair_token_count':sum(x['mixed_with_wall'] for x in pairs),
      'lex_min_mapping':{'A':mapping[0],'B':mapping[1],'C':mapping[2],'0':'AB','1':'BC','2':'CA'},
      'comma_separated_pair_sequence_file':f'{base}.pairs.sequence.csv',
      'comma_separated_ternary_file':f'{base}.ternary.sequence.csv',
      'prefix_80':','.join(map(str,digits[:80])),
    }
    (a.outdir/f'{base}.ternary.summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
