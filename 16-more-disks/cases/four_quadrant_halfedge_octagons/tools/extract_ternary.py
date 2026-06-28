#!/usr/bin/env python3
"""Export/check ternary CSV from stored four-quadrant search JSON."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
SOURCES=[
    ('four_site_watch2048.json', HERE/'data/search/four_site_watch2048.json'),
    ('class_08_continuation_to_cap128.json', HERE/'data/search/class_08_continuation_to_cap128.json'),
]

def records():
    out=[]
    for label,path in SOURCES:
        doc=json.loads(path.read_text())
        for level in doc['levels']:
            for tr in level['trials']:
                word=tr.get('lex_min_ternary')
                if word is None:
                    continue
                mapping=';'.join(tr.get('lex_min_pair_map',[]))
                case=f"N{level['bodies']}_class_{tr['class']:02d}"
                for i,d in enumerate(word):
                    out.append((case,i,d,mapping,label))
    return out

def write(path):
    rows=records()
    with path.open('w',newline='') as f:
        w=csv.writer(f)
        w.writerow(['case','digit_index','digit','channel_map','source'])
        w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--check',action='store_true')
    ns=ap.parse_args()
    dest=HERE/'data/ternary/all_available_lex_min_ternary.csv'
    if ns.check:
        import tempfile
        p=Path(tempfile.mkstemp(prefix='ternary-',suffix='.csv')[1])
        try:
            write(p)
            if p.read_bytes()!=dest.read_bytes():
                raise SystemExit('FAIL: ternary CSV differs from JSON-derived export')
            print('OK: ternary CSV matches stored JSON')
        finally: p.unlink(missing_ok=True)
    else:
        write(dest)
        print(dest)
if __name__=='__main__': main()
