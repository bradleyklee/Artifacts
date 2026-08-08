#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, csv
from fractions import Fraction
from pathlib import Path
from typing import Any

# Slot order matches the solver and all frozen grids.
QUADRANT_ORDER = ("NW", "SW", "SE", "NE")

def grid_code(grid: list[list[int]]) -> str:
    n=len(grid)
    assert n and all(len(r)==n for r in grid) and (n & (n-1))==0
    def rec(x0:int,y0:int,s:int)->str:
        vals={grid[y][x] for y in range(y0,y0+s) for x in range(x0,x0+s)}
        if len(vals)==1:
            v=next(iter(vals))
            return str(v) if v else "0"
        h=s//2
        # NW, SW, SE, NE
        return "{"+",".join([
            rec(x0,y0,h), rec(x0,y0+h,h),
            rec(x0+h,y0+h,h), rec(x0+h,y0,h)
        ])+"}"
    return rec(0,0,n)

def load(path:Path)->Any:
    return json.loads(path.read_text())

def fraction_text(x: float)->str:
    return str(Fraction(x).limit_denominator())

def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    args=ap.parse_args(); root=args.root
    results=root/'results'; reports=root/'reports'
    reports.mkdir(exist_ok=True)
    exact=load(results/'exact_terms.json')
    summaries={r['n']:r for r in exact['exact_first_resolution_terms']}

    index=[]
    # Level 1 is a single occupied leaf; no nondegenerate simple cycle is defined.
    code='1'
    text=f'''# Level 1 report\n\nPrimary labeled-leaf code: `{code}`.\n\nConvention: `0` is an empty leaf, a positive integer is an occupied leaf carrying that cyclic label, and `{{NW,SW,SE,NE}}` is an internal quadtree node.\n\nThere is one typogeometry at level 1. A nondegenerate simple cycle through only one labeled region is outside the present solver's n >= 2 definition.\n'''
    (reports/'level_1.md').write_text(text); index.append((1,code,'not defined'))

    for n in (2,3,4):
        recs=load((results/'small_levels'/f'n{n}_class_records.json') if n<4 else (results/'n4_class_records.json'))
        best=max(r['normalized_value'] for r in recs)
        bests=[r for r in recs if r['normalized_value']==best]
        rows=[]
        for r in bests:
            c=grid_code(r['base_label_grid'])
            rows.append((c,r['inflation'],r['taxicab_length'],r['grid_width'],r.get('normalized_value_fraction', fraction_text(r['normalized_value']))))
        s=summaries[n]
        lines=[f'# Level {n} report','',
               'Coding convention: `0` is empty, integer `k` is the occupied leaf labeled `k`, and `{a,b,c,d}` lists children in `NW,SW,SE,NE` order.','',
               f"- Typogeometries: {s['typogeometry_count']:,}",
               f"- Raw labeled instances: {s['raw_labeled_instances']:,}",
               f"- Symmetry classes: {s['global_symmetry_classes']:,}",
               f"- Exact first-resolution value: {s['first_resolution_value_fraction']}",'',
               '## Extremal labeled-leaf codes','']
        for c,l,L,W,C in rows:
            lines += [f'`{c}`', '', f'- first feasible inflation: {l}', f'- width: {W}', f'- exact shortest length: {L}', f'- normalized value: {C}', '']
        (reports/f'level_{n}.md').write_text('\n'.join(lines)+'\n')
        index.append((n,rows[0][0],s['first_resolution_value_fraction']))

    r5=load(results/'n5_record_14974_direct_optimum.json')
    rec=r5.get('record',r5)
    c5=grid_code(rec['base_label_grid'])
    summ=load(results/'n5_record6_blast_summary.json')
    period=[(1,8,48,'6'),(2,16,32,'2'),(3,24,44,'11/6'),(4,32,56,'7/4'),(5,40,68,'17/10')]
    lines=['# Level 5 checkpoint','',
           'This is a checkpoint, not a completed exact level.', '',
           'Coding convention: `0` is empty, integer `k` is the occupied leaf labeled `k`, and `{a,b,c,d}` lists children in `NW,SW,SE,NE` order.','',
           '## Current exact record','',f'`{c5}`','',
           f"- manifest lookup ID: {rec.get('representative_index', rec.get('class_id',14974))}",
           '- first feasible inflation: 1','- width: 8','- exact shortest length: 48','- normalized value: 6','',
           '## Search coverage','',
           f"- total symmetry classes: {summ['total_classes']:,}",
           f"- closed classes: {summ['closed_classes']:,}",
           f"- unresolved classes: {summ['unresolved_classes']:,}",
           f"- closed fraction: {100*summ['closed_classes']/summ['total_classes']:.2f}%",'',
           '## Refinement data for the same labeled tree','',
           '| inflation l | width | exact L_min | normalized C |','|---:|---:|---:|---:|']
    lines += [f'| {l} | {w} | {L} | {C} |' for l,w,L,C in period]
    lines += ['', 'The drop from 6 at l=1 to 2 at l=2 is the corner-trap phenomenon that motivates distinguishing the first-resolution invariant from refinement-stable alternatives.','']
    (reports/'level_5_checkpoint.md').write_text('\n'.join(lines))
    index.append((5,c5,'>= 6; incomplete'))

    with (reports/'level_summary.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['level','primary_labeled_leaf_code','status_or_value']); w.writerows(index)
    (reports/'README_DIGEST.md').write_text('''# Report digest\n\nHuman-facing identities use compact labeled-leaf brace notation. Numeric representative IDs appear only as machine lookup handles.\n\n- `level_1.md` through `level_4.md` are regenerated from exact frozen data.\n- `level_5_checkpoint.md` records the current exact lower bound, refinement table, coverage, and survivor status.\n- Run `python src/generate_reports.py` after updating result files.\n''')
    print("[reports] regenerated levels 1-5 checkpoint")

if __name__=='__main__': main()
