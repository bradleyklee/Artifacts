#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, random, time
from pathlib import Path
import numpy as np
import p4_solver as p4
import random_p5_search as rhs


def edges_from_record(rec: dict) -> set[tuple[int,int]]:
    w=rec['grid_width']; E=set()
    for seg in rec['segments_xy']:
        vs=[y*w+x for x,y in seg]
        for a,b in zip(vs,vs[1:]): E.add(tuple(sorted((a,b))))
    return E


def adjacency(edges:set[tuple[int,int]], nverts:int):
    adj=[[] for _ in range(nverts)]
    for a,b in edges: adj[a].append(b); adj[b].append(a)
    return adj


def ordered_cycle(edges:set[tuple[int,int]], nverts:int) -> list[int] | None:
    if not edges: return None
    adj=adjacency(edges,nverts)
    used=[i for i,a in enumerate(adj) if a]
    if any(len(adj[v])!=2 for v in used): return None
    start=min(used); prev=-1; cur=start; cyc=[start]
    while True:
        a,b=adj[cur]; nxt=a if a!=prev else b
        if nxt==start: break
        cyc.append(nxt); prev,cur=cur,nxt
        if len(cyc)>len(used): return None
    if len(cyc)!=len(used): return None
    return cyc


def progress_for_word(word:list[int], n:int) -> tuple[int,list[int]]:
    m=len(word); best=0; bestpos=[]
    for direction in (1,-1):
        seq=word if direction==1 else list(reversed(word))
        for s,v in enumerate(seq):
            if v!=1: continue
            target=2; pos=[s]
            for step in range(1,m):
                val=seq[(s+step)%m]
                if val==target:
                    pos.append((s+step)%m); target+=1
                    if target==n+1: return n,pos
            if target-1>best: best=target-1; bestpos=pos
    return best,bestpos


def evaluate(edges:set[tuple[int,int]], labels:np.ndarray, n:int):
    w=labels.shape[1]; cyc=ordered_cycle(edges,w*w)
    if cyc is None: return None
    word=[int(labels[v//w,v%w]) for v in cyc]
    prog,pos=progress_for_word(word,n)
    # Encourage touching all missing labels, then shorter cycles after feasibility.
    touched=len({x for x in word if x>0})
    if prog==n:
        score=100000 - len(cyc)
    else:
        score=1000*prog + 50*touched - 0.05*len(cyc)
    return score,prog,touched,len(cyc),cyc,pos,word


def plaquette_edges(x:int,y:int,w:int):
    a=y*w+x; b=a+1; c=a+w; d=c+1
    return {tuple(sorted(e)) for e in ((a,b),(a,c),(b,d),(c,d))}


def rectangle_cycle(w:int, x0:int,y0:int,x1:int,y1:int):
    E=set()
    for x in range(x0,x1):
        E.add(tuple(sorted((y0*w+x,y0*w+x+1))))
        E.add(tuple(sorted((y1*w+x,y1*w+x+1))))
    for y in range(y0,y1):
        E.add(tuple(sorted((y*w+x0,(y+1)*w+x0))))
        E.add(tuple(sorted((y*w+x1,(y+1)*w+x1))))
    return E


def solution_from_cycle(cyc:list[int], labels:np.ndarray, n:int):
    w=labels.shape[1]; m=len(cyc)
    # Try both directions and all label-1 starts; greedily recover representatives.
    for direction in (1,-1):
        seq=cyc if direction==1 else list(reversed(cyc))
        for s,v in enumerate(seq):
            if int(labels[v//w,v%w])!=1: continue
            chosen=[v]; positions=[s]; target=2
            for step in range(1,m):
                q=seq[(s+step)%m]
                if int(labels[q//w,q%w])==target:
                    chosen.append(q); positions.append((s+step)%m); target+=1
                    if target==n+1: break
            if target!=n+1: continue
            # Rotate so chosen[0] starts sequence; create paths between chosen positions.
            rot=seq[s:]+seq[:s]
            rel=[(p-s)%m for p in positions]
            segs=[]
            for k in range(n-1): segs.append(rot[rel[k]:rel[k+1]+1])
            segs.append(rot[rel[-1]:]+[rot[0]])
            sol=p4.CycleSolution(length=m,chosen=chosen,segments=segs)
            p4.verify_solution(labels,n,sol)
            return sol
    return None


def search(labels:np.ndarray, starts:list[set[tuple[int,int]]], n:int, seed:int, steps:int, restarts:int):
    rng=random.Random(seed); w=labels.shape[1]
    best_valid=None; best_eval=None
    for r in range(restarts):
        current=set(rng.choice(starts)); ev=evaluate(current,labels,n)
        if ev is None: continue
        cur_score=ev[0]
        temp=200.0
        for step in range(steps):
            x=rng.randrange(w-1); y=rng.randrange(w-1)
            cand=current ^ plaquette_edges(x,y,w)
            cev=evaluate(cand,labels,n)
            if cev is None: continue
            delta=cev[0]-cur_score
            if delta>=0 or rng.random()<math.exp(max(-50.0,delta/max(temp,1e-9))):
                current=cand; ev=cev; cur_score=cev[0]
            temp*=0.99997
            if ev[1]==n:
                sol=solution_from_cycle(ev[4],labels,n)
                if sol and (best_valid is None or sol.length<best_valid.length):
                    best_valid=sol; best_eval=ev
                    print(f'[valid] restart={r} step={step} L={sol.length}',flush=True)
                    # Reheat around a valid cycle to seek shorter forms.
                    temp=max(temp,20.0)
        print(f'[restart] {r+1}/{restarts} progress={ev[1]} touched={ev[2]} L={ev[3]} best={None if best_valid is None else best_valid.length}',flush=True)
        if best_valid is not None: starts.append(set(current))
    return best_valid,best_eval


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--index',type=int,default=909); ap.add_argument('--inflation',type=int,default=2); ap.add_argument('--seed',type=int,default=9092026); ap.add_argument('--steps',type=int,default=200000); ap.add_argument('--restarts',type=int,default=12); ap.add_argument('--output',type=Path,default=Path('results/p5_cycle_flip_909.json')); args=ap.parse_args()
    inst=rhs.depth_instances(5,2)[args.index]; labels=p4.expand_labels(inst.base_labels,args.inflation); w=labels.shape[1]
    starts=[]
    # Perimeter and many random rectangles.
    starts.append(rectangle_cycle(w,0,0,w-1,w-1))
    for x0 in range(w-2):
      for y0 in range(w-2):
       for x1 in range(x0+2,w):
        for y1 in range(y0+2,w): starts.append(rectangle_cycle(w,x0,y0,x1,y1))
    # Seed with the nearby exact record 906 when available.
    try:
      data=json.load(open('results/p5_exact_top_depth2.json'))
      for row in data:
       rec=row.get('record')
       if row.get('index')==906 and rec and rec['grid_width']==w: starts.append(edges_from_record(rec))
    except FileNotFoundError: pass
    t=time.time(); sol,ev=search(labels,starts,5,args.seed,args.steps,args.restarts)
    payload={'index':args.index,'inflation':args.inflation,'seed':args.seed,'runtime_seconds':time.time()-t,'found':sol is not None,'base_label_grid':inst.base_labels.tolist(),'tree':p4.tree_notation(inst.tree),'order':list(inst.order)}
    if sol:
      payload['record']=p4.solution_to_json(inst,args.inflation,sol)
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(payload,indent=2),encoding='utf-8')
    print('[done]',payload['found'],None if sol is None else sol.length,'sec',payload['runtime_seconds'],flush=True)

if __name__=='__main__': main()
