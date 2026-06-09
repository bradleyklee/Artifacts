#!/usr/bin/env python3
"""Draw a final-state PNG/SVG-ish depiction from a DH12 JSON record.

This does not require replay. It reads the record's saved `state` list directly.
"""
import argparse, json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
SQRT3=math.sqrt(3)

def parse_state(rec):
    out=[]
    for item in rec.get('state',[]):
        if isinstance(item, dict):
            q=int(item.get('q', item.get('pos',[0,0])[0])); r=int(item.get('r', item.get('pos',[0,0])[1])); lab=item.get('label') or item.get('lab') or item.get('state')
        elif isinstance(item, (list,tuple)) and len(item)>=3:
            q,r,lab=int(item[0]),int(item[1]),item[2]
        else: continue
        out.append((q,r,str(lab)))
    return out

def xy(q,r,size):
    # pointy axial layout
    return (size*SQRT3*(q+r/2.0), size*1.5*r)

def poly(cx,cy,size):
    return [(cx+size*math.cos(math.pi/6+k*math.pi/3), cy+size*math.sin(math.pi/6+k*math.pi/3)) for k in range(6)]

def color(label):
    base=label.split('.')[0]
    if base=='D': return (226,115,92)
    if base.startswith('D0'): return (230,150,80)
    if base.startswith('D1'): return (90,145,225)
    if base.startswith('H'): return (98,178,105)
    return (180,180,180)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('record')
    ap.add_argument('--out', default='depiction.png')
    ap.add_argument('--size', type=float, default=7.0)
    ap.add_argument('--label', action='store_true')
    args=ap.parse_args()
    rec=json.load(open(args.record)); state=parse_state(rec)
    if not state: raise SystemExit('record has no parseable state')
    coords=[xy(q,r,args.size) for q,r,_ in state]
    minx,maxx=min(x for x,y in coords), max(x for x,y in coords); miny,maxy=min(y for x,y in coords), max(y for x,y in coords)
    pad=40; W=int(maxx-minx+2*pad+2*args.size); H=int(maxy-miny+2*pad+2*args.size+40)
    img=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(img)
    for q,r,lab in state:
        x,y=xy(q,r,args.size); x=x-minx+pad; y=y-miny+pad
        d.polygon(poly(x,y,args.size*0.96), fill=color(lab), outline=(25,25,25))
    title=f"DH12 {rec.get('cells',len(state))} cells / depth {rec.get('depth','?')} / {rec.get('status','')}"
    d.text((pad, H-30), title, fill=(0,0,0))
    img.save(args.out)
    print(args.out)
if __name__=='__main__': main()
