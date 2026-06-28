#!/usr/bin/env python3
"""Exact-rational four-quadrant square control.

Outer container: [-2,2]^2 (edge 4). Movers: axis-aligned squares, edge 1.
Allowed start centres: (±1,±1). Velocities: cardinal unit vectors.
The finite initial atlas is reduced by D4. Pair corners and multi-contact
batches are terminally classified rather than resolved.
"""
from __future__ import annotations
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
import argparse, json

BOX=Q(2); HALF=Q(1,2); EDGE=Q(1)
SITES={'Q[-1,+1]':(-1,1),'Q[+1,+1]':(1,1),'Q[-1,-1]':(-1,-1),'Q[+1,-1]':(1,-1)}
SITE_LOOKUP={v:k for k,v in SITES.items()}
VELS={'+x':(Q(1),Q(0)),'-x':(Q(-1),Q(0)),'+y':(Q(0),Q(1)),'-y':(Q(0),Q(-1))}
VEL_LOOKUP={v:k for k,v in VELS.items()}
D4=(lambda x,y:(x,y),lambda x,y:(y,-x),lambda x,y:(-x,-y),lambda x,y:(-y,x),lambda x,y:(-x,y),lambda x,y:(x,-y),lambda x,y:(y,x),lambda x,y:(-y,-x))

def canonical(state):
    forms=[]
    for tf in D4:
        out=[]
        for site,vel in state:
            x,y=SITES[site]; vx,vy=VELS[vel]
            ns=tf(x,y); nv=tf(int(vx),int(vy))
            out.append((SITE_LOOKUP[ns],VEL_LOOKUP[(Q(nv[0]),Q(nv[1]))]))
        forms.append(tuple(sorted(out)))
    return min(forms)

class P:
    def __init__(self, identity, site, vel):
        self.identity=identity; self.pos=[Q(v) for v in SITES[site]]; self.vel=list(VELS[vel])

def key(ps): return tuple((p.identity,p.pos[0],p.pos[1],p.vel[0],p.vel[1]) for p in ps)

def wall_events(ps):
    out=[]
    for i,p in enumerate(ps):
        x,y=p.pos; vx,vy=p.vel
        if vx>0: out.append(((BOX-x-HALF)/vx,'wallx',i,None))
        if vx<0: out.append(((x+BOX-HALF)/(-vx),'wallx',i,None))
        if vy>0: out.append(((BOX-y-HALF)/vy,'wally',i,None))
        if vy<0: out.append(((y+BOX-HALF)/(-vy),'wally',i,None))
    return [e for e in out if e[0]>0]

def pair_events(ps):
    out=[]
    for i,j in combinations(range(len(ps)),2):
        a,b=ps[i],ps[j]
        dx=b.pos[0]-a.pos[0]; dy=b.pos[1]-a.pos[1]
        dvx=b.vel[0]-a.vel[0]; dvy=b.vel[1]-a.vel[1]
        candidates=[]
        if dvx:
            for target in (EDGE,-EDGE):
                t=(target-dx)/dvx
                if t>0:
                    y=dy+dvy*t
                    if abs(y)<EDGE: candidates.append((t,'pairx',i,j))
                    elif abs(y)==EDGE: candidates.append((t,'corner',i,j))
        if dvy:
            for target in (EDGE,-EDGE):
                t=(target-dy)/dvy
                if t>0:
                    x=dx+dvx*t
                    if abs(x)<EDGE: candidates.append((t,'pairy',i,j))
                    elif abs(x)==EDGE: candidates.append((t,'corner',i,j))
        if candidates:
            t=min(x[0] for x in candidates)
            same=[x for x in candidates if x[0]==t]
            kinds={x[1] for x in same}
            out.append((t,'corner' if 'corner' in kinds or len(kinds)>1 else same[0][1],i,j))
    return out

def run(state, cap):
    ps=[P(f'P{k}',s,v) for k,(s,v) in enumerate(state)]
    seen={key(ps):0}; clock=Q(0); pairs=walls=0
    for step in range(1,cap+1):
        events=wall_events(ps)+pair_events(ps)
        t=min(e[0] for e in events); batch=[e for e in events if e[0]==t]
        if any(e[1]=='corner' for e in batch): return {'status':'CORNER','batches':step,'time':str(clock+t),'pair_events':pairs,'wall_events':walls}
        hit={}
        for _,kind,i,j in batch:
            hit[i]=hit.get(i,0)+1
            if j is not None: hit[j]=hit.get(j,0)+1
        if any(n>1 for n in hit.values()): return {'status':'SIMULTANEOUS','batches':step,'time':str(clock+t),'pair_events':pairs,'wall_events':walls}
        for p in ps:
            p.pos[0]+=p.vel[0]*t; p.pos[1]+=p.vel[1]*t
        clock+=t
        for _,kind,i,j in batch:
            if kind=='pairx': ps[i].vel[0],ps[j].vel[0]=ps[j].vel[0],ps[i].vel[0]; pairs+=1
            elif kind=='pairy': ps[i].vel[1],ps[j].vel[1]=ps[j].vel[1],ps[i].vel[1]; pairs+=1
        for _,kind,i,j in batch:
            if kind=='wallx': ps[i].vel[0]=-ps[i].vel[0]; walls+=1
            if kind=='wally': ps[i].vel[1]=-ps[i].vel[1]; walls+=1
        k=key(ps)
        if k in seen: return {'status':'RETURN','batches':step,'period_batches':step-seen[k],'time':str(clock),'pair_events':pairs,'wall_events':walls}
        seen[k]=step
    return {'status':'EVENT_CAP','batches':cap,'time':str(clock),'pair_events':pairs,'wall_events':walls}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--event-cap',type=int,default=20000); ap.add_argument('--output',type=Path,required=True); ns=ap.parse_args()
    levels=[]
    for n in (2,3):
        raw=[]
        for sites in combinations(sorted(SITES),n):
            for vels in product(sorted(VELS),repeat=n): raw.append(tuple(sorted(zip(sites,vels))))
        reps=sorted({canonical(x) for x in raw})
        trials=[]; counts={}
        for k,st in enumerate(reps,1):
            r=run(st,ns.event_cap); counts[r['status']]=counts.get(r['status'],0)+1
            trials.append({'class':k,'initial':['%s %s'%x for x in st],**r})
        levels.append({'bodies':n,'raw_initials':len(raw),'d4_classes':len(reps),'status_counts':counts,'trials':trials})
    doc={'schema':'four-quadrant-quarter-edge-squares/v1','geometry':{'container_edge':'4','square_edge':'1','center_sites':'(±1,±1)','velocity_atlas':['+x','-x','+y','-y'],'arithmetic':'Fraction / Q'},'event_cap':ns.event_cap,'levels':levels}
    ns.output.write_text(json.dumps(doc,indent=2)+'\n')
if __name__=='__main__': main()
