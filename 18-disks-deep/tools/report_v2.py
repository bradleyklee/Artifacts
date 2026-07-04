#!/usr/bin/env python3
"""Read-only standard-library reporter for sealed v2 blocks."""
from __future__ import annotations
import argparse,csv,gzip,html,json,math,os,shutil,subprocess,sys,tarfile,time,signal
from datetime import datetime,timezone
from pathlib import Path
from v2_common import LANES,atomic_json,atomic_text,contiguous_frontier


def read_complexity(block:Path):
 with tarfile.open(block,'r:gz') as tf:
  n=[x for x in tf.getnames() if x.endswith('/complexity.csv.gz')][0]
  with gzip.open(tf.extractfile(n),'rt',newline='') as f:return list(csv.DictReader(f))

def total(row):
 cols=['T_common_denominator_bits','T_common_a_numerator_bits','T_common_b_numerator_bits','T_common_c_numerator_bits','T_common_d_numerator_bits']
 if all(c in row for c in cols):return sum(int(row[c]) for c in cols)
 return int(row.get('T_sum_component_bits',0))

def linear_slope(points):
 if len(points)<2:return None
 xs=[float(x) for x,_ in points];ys=[float(y) for _,y in points]
 mx=sum(xs)/len(xs);my=sum(ys)/len(ys)
 den=sum((x-mx)**2 for x in xs)
 return None if den==0 else sum((x-mx)*(y-my) for x,y in zip(xs,ys))/den

def svg_line(points,title,footer,path):
 W,H,L,R,T,B=1100,600,80,35,55,65
 xs=[p[0] for p in points];ys=[p[1] for p in points];xmin,xmax=min(xs),max(xs);ymin,ymax=min(ys),max(ys)
 if xmin==xmax:xmax+=1
 if ymin==ymax:ymax+=1
 def X(x):return L+(x-xmin)*(W-L-R)/(xmax-xmin)
 def Y(y):return H-B-(y-ymin)*(H-T-B)/(ymax-ymin)
 pts=' '.join(f'{X(x):.2f},{Y(y):.2f}' for x,y in points)
 ticks=[]
 for i in range(6):
  x=xmin+(xmax-xmin)*i/5;xx=X(x);ticks.append(f'<line x1="{xx:.1f}" y1="{T}" x2="{xx:.1f}" y2="{H-B}" stroke="#ddd"/><text x="{xx:.1f}" y="{H-B+22}" text-anchor="middle">{x:,.0f}</text>')
 for i in range(6):
  y=ymin+(ymax-ymin)*i/5;yy=Y(y);ticks.append(f'<line x1="{L}" y1="{yy:.1f}" x2="{W-R}" y2="{yy:.1f}" stroke="#ddd"/><text x="{L-10}" y="{yy+4:.1f}" text-anchor="end">{y:,.0f}</text>')
 s=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/><style>text{{font:14px sans-serif;fill:#222}}.title{{font-size:20px;font-weight:bold}}.foot{{font-size:13px;fill:#555}}</style><text class="title" x="{L}" y="30">{html.escape(title)}</text>{''.join(ticks)}<polyline fill="none" stroke="#1769aa" stroke-width="1.4" points="{pts}"/><text x="{(L+W-R)/2:.0f}" y="{H-18}" text-anchor="middle">accepted collision count</text><text class="foot" x="{L}" y="{H-42}">{html.escape(footer)}</text></svg>'''
 atomic_text(path,s)

def refresh(root,lane, emit_png=True):
 front,chain=contiguous_frontier(root,lane);rows=[]
 for _,p in chain:
  for r in read_complexity(p):rows.append({'collision':int(r['step']),'total_bits':total(r)})
 rows.sort(key=lambda r:r['collision'])
 out=root/'campaign'/'live'/lane;out.mkdir(parents=True,exist_ok=True)
 csvpath=out/'total_bits.csv';tmp=csvpath.with_suffix('.next')
 with tmp.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['collision','total_bits']);w.writeheader();w.writerows(rows)
 os.replace(tmp,csvpath)
 if rows:
  pts=[(r['collision'],r['total_bits']) for r in rows]
  svg_line(pts,f'{lane}: exact clock total bitcount',f'Coverage: accepted exact collisions {pts[0][0]:,}–{pts[-1][0]:,}; sealed blocks: {len(chain)}',out/'total_bits.svg')
  if emit_png:
   for cmd in (['rsvg-convert','-o',str(out/'total_bits.png'),str(out/'total_bits.svg')],['convert',str(out/'total_bits.svg'),str(out/'total_bits.png')]):
    if shutil.which(cmd[0]):subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);break
 latest=rows[-1]['total_bits'] if rows else None
 slope1000=linear_slope(pts[-1000:]) if rows else None
 status={'lane':lane,'accepted_collision':front,'blocks':len(chain),'coverage':[rows[0]['collision'],rows[-1]['collision']] if rows else None,'latest_total_bits':latest,'slope_1000_bits_per_collision':slope1000,'updated_utc':datetime.now(timezone.utc).isoformat()}
 atomic_json(out/'report_status.json',status);return status
STOP=False
def _stop(*_):
 global STOP;STOP=True
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--lanes',nargs='+',default=list(LANES));ap.add_argument('--root',type=Path,default=Path('.'));ap.add_argument('--poll',type=float,default=5);ap.add_argument('--once',action='store_true');ap.add_argument('--no-png',action='store_true');args=ap.parse_args();root=args.root.resolve();seen={}
 signal.signal(signal.SIGINT,_stop);signal.signal(signal.SIGTERM,_stop)
 while not STOP:
  now={}
  for lane in args.lanes:
   s=refresh(root,lane,emit_png=not args.no_png);now[lane]=s
   if seen.get(lane)!=s['accepted_collision']:print(f'[report] {lane}: coverage through {s["accepted_collision"]:,}',flush=True)
  seen={k:v['accepted_collision'] for k,v in now.items()};atomic_json(root/'campaign'/'live'/'reporter_status.json',{'lanes':now,'updated_utc':datetime.now(timezone.utc).isoformat()})
  if args.once:break
  time.sleep(args.poll)
if __name__=='__main__':main()
