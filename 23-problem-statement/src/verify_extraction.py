#!/usr/bin/env python3
from pathlib import Path
import csv,json,sys
from generate_reports import grid_code
root=Path(__file__).resolve().parents[1]
checks=[]
def ok(name,cond):
    checks.append((name,bool(cond))); print(('PASS' if cond else 'FAIL'),name)
manifest=root/'results/n5_manifest.tsv'
with manifest.open() as f: rows=list(csv.DictReader(f,delimiter='\t'))
ok('manifest has 31,968 classes',len(rows)==31968)
ids={int(r['class_id']) for r in rows}
unres={int(x) for x in (root/'results/n5_record6_unresolved_ids.txt').read_text().split()}
ok('unresolved count is 2,811',len(unres)==2811)
ok('all unresolved IDs occur in manifest',unres<=ids)
r=json.loads((root/'results/n5_record_14974_direct_optimum.json').read_text())['record']
code=grid_code(r['base_label_grid'])
ok('record brace code stable',code=='{0,4,0,{0,0,{0,3,0,5},{1,0,0,2}}}')
ok('record exact length 48',r.get('taxicab_length',r.get('length'))==48)
ok('level reports 1-5 exist',all((root/'reports'/('level_5_checkpoint.md' if n==5 else f'level_{n}.md')).exists() for n in range(1,6)))
print(f"SUMMARY {sum(v for _,v in checks)}/{len(checks)}")
sys.exit(0 if all(v for _,v in checks) else 1)
