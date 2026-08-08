#!/usr/bin/env python3
import pathlib
import json,glob,os,collections,statistics,math
ROOT=str(pathlib.Path(__file__).resolve().parents[1])
idx={x['example_id']:x for x in json.load(open(os.path.join(ROOT,'candidate_index.json')))}
rows=[]
for f in sorted(glob.glob(os.path.join(ROOT,'data','*_result.json'))):
 d=json.load(open(f));m=idx[d['example_id']]
 hit=d.get('first_hit') or {}; rh=d.get('reductive_first_hit') or {}
 rr=(d.get('reductive') or [{}])[0].get('records',[])
 final=rr[-1] if rr else {}
 rows.append({
  'example_id':d['example_id'],'category':d['category'],'status':d['status'],
  'signed_symmetry_count':len(m['signed_coordinate_symmetries']),
  'nontrivial_signed_symmetry':len(m['signed_coordinate_symmetries'])>1,
  'squarefree_at_infinity':d.get('quartic_infinity',{}).get('squarefree_at_infinity'),
  'inductive_order':hit.get('order'),'inductive_degree':hit.get('degree'),
  'reductive_order':rh.get('order'),'mode_agreement':d.get('mode_agreement',False),
  'deductive_bound_status':d.get('deductive_bound_status'),
  'final_rows':final.get('rows'),'final_source_columns':final.get('source_columns'),
  'final_rank_C':final.get('rank_C'),'final_rank_CW':final.get('rank_CW'),
  'seconds_total':d.get('seconds_total'),
  'support_cubic':m['support_counts']['cubic'],'support_quartic':m['support_counts']['quartic']
 })
with open(os.path.join(ROOT,'benchmark_rows.json'),'w') as f:json.dump(rows,f,indent=2);f.write('\n')

def cnt(vals):return dict(sorted(collections.Counter(vals).items(),key=lambda z:str(z[0])))
stats={
 'models_total':len(rows),
 'status_counts':cnt(r['status'] for r in rows),
 'category_counts':cnt(r['category'] for r in rows),
 'inductive_order_counts':cnt(r['inductive_order'] for r in rows),
 'inductive_order_degree_counts':cnt(f"{r['inductive_order']},{r['inductive_degree']}" for r in rows),
 'reductive_order_counts':cnt(r['reductive_order'] for r in rows),
 'mode_agreement_count':sum(r['mode_agreement'] for r in rows),
 'deductive_generic_bound_count':sum(r['deductive_bound_status']=='GENERIC_BOUND_APPLIED' for r in rows),
 'squarefree_at_infinity_count':sum(bool(r['squarefree_at_infinity']) for r in rows),
 'nontrivial_signed_symmetry_count':sum(r['nontrivial_signed_symmetry'] for r in rows),
 'generic_no_signed_symmetry_count':sum((not r['nontrivial_signed_symmetry']) and r['category'] in ('dense_generic','semidense_generic') for r in rows),
 'runtime_seconds':{
   'sum':sum(r['seconds_total'] or 0 for r in rows),
   'median':statistics.median([r['seconds_total'] for r in rows]) if rows else None,
   'max':max([r['seconds_total'] for r in rows],default=None)
 },
 'by_category':{}
}
for cat,rs in sorted(collections.defaultdict(list,((c,[r for r in rows if r['category']==c]) for c in set(r['category'] for r in rows))).items()):
 stats['by_category'][cat]={'count':len(rs),'orders':cnt(r['inductive_order'] for r in rs),'degrees':cnt(r['inductive_degree'] for r in rs),'mode_agreement':sum(r['mode_agreement'] for r in rs),'nontrivial_symmetry':sum(r['nontrivial_signed_symmetry'] for r in rs)}
with open(os.path.join(ROOT,'benchmark_statistics.json'),'w') as f:json.dump(stats,f,indent=2);f.write('\n')

md=[]
md += ['# Cubic--quartic mixed benchmark','',f"Models completed: **{len(rows)}**.",'']
md += ['## Corpus balance','',f"- Dense generic: {sum(r['category']=='dense_generic' for r in rows)}",f"- Semi-dense generic: {sum(r['category']=='semidense_generic' for r in rows)}",f"- Structured controls: {sum(r['category'] not in ('dense_generic','semidense_generic') for r in rows)}",f"- No nontrivial signed-coordinate symmetry: {sum(not r['nontrivial_signed_symmetry'] for r in rows)}",'']
md += ['## Mode status','',f"- Inductive/reductive first-order agreement: {stats['mode_agreement_count']}/{len(rows)}",f"- Generic deductive bound available: {stats['deductive_generic_bound_count']}/{len(rows)}",f"- Squarefree quartic layer: {stats['squarefree_at_infinity_count']}/{len(rows)}",'']
md += ['## First relation distribution','']
for k,v in stats['inductive_order_counts'].items():md.append(f'- Order {k}: {v}')
md += ['','## Order--degree boxes','']
for k,v in stats['inductive_order_degree_counts'].items():md.append(f'- ({k}): {v}')
md += ['','## Category table','', '| Category | Models | First-order distribution | Mode agreement | Nontrivial signed symmetry |','|---|---:|---|---:|---:|']
for cat,z in stats['by_category'].items():md.append(f"| {cat} | {z['count']} | {z['orders']} | {z['mode_agreement']}/{z['count']} | {z['nontrivial_symmetry']} |")
md += ['','## Per-model data','', '| Model | Category | Sym. | Bound | Inductive | Reductive | Rows | Source cols | Seconds |','|---|---|---:|---|---|---|---:|---:|---:|']
for r in rows:
 md.append(f"| {r['example_id']} | {r['category']} | {r['signed_symmetry_count']} | {r['deductive_bound_status']} | ({r['inductive_order']},{r['inductive_degree']}) | {r['reductive_order']} | {r['final_rows']} | {r['final_source_columns']} | {r['seconds_total']:.2f} |")
open(os.path.join(ROOT,'BENCHMARK_REPORT.md'),'w').write('\n'.join(md)+'\n')
print(json.dumps(stats,indent=2))
