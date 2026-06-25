#!/usr/bin/env python3
"""
Independent exact checker for c4-clock-mask-evolve-ledger/v1.

Consumes a persisted seed and persisted ledger only; does not invoke or import
the Go evolver. Uses Fraction arithmetic over Q(sqrt(2)) to independently
enumerate every earliest wall/pair candidate, validate strict edge overlap,
apply collision maps, and check conservation laws.
"""
from __future__ import annotations
import argparse, json, sys
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path

@dataclass(frozen=True)
class Q:
    a: F; b: F
    @staticmethod
    def parse(z): return Q(F(z["a"]), F(z["b"]))
    def add(self,o): return Q(self.a+o.a,self.b+o.b)
    def sub(self,o): return Q(self.a-o.a,self.b-o.b)
    def sc(self,c): return Q(self.a*c,self.b*c)
    def dv(self,c): return Q(self.a/c,self.b/c)
    def sign(self):
        if self.a==0: return (self.b>0)-(self.b<0)
        if self.b==0: return (self.a>0)-(self.a<0)
        if (self.a>0)==(self.b>0): return 1 if self.a>0 else -1
        d=self.a*self.a-2*self.b*self.b
        return ((d>0)-(d<0)) if self.a>0 else -((d>0)-(d<0))
    def cmp(self,o): return self.sub(o).sign()
    def eq(self,o): return self.a==o.a and self.b==o.b
    def neg(self): return Q(-self.a,-self.b)

@dataclass(frozen=True)
class VQ:
    x:Q; y:Q
    def sub(self,o): return VQ(self.x.sub(o.x),self.y.sub(o.y))
    def flow(self,v,t): return VQ(self.x.add(t.sc(v.x)),self.y.add(t.sc(v.y)))
@dataclass(frozen=True)
class VR:
    x:F; y:F
    def sub(self,o): return VR(self.x-o.x,self.y-o.y)
    def add(self,o): return VR(self.x+o.x,self.y+o.y)
    def eq(self,o): return self.x==o.x and self.y==o.y
@dataclass(frozen=True)
class Face:
    name:str; nx:int; ny:int; sup:Q
@dataclass
class Body:
    id:str; pos:VQ; vel:VR
    def cp(self): return Body(self.id,self.pos,VR(self.vel.x,self.vel.y))
@dataclass
class Event:
    t:Q; kind:str; i:int; j:int|None; f:Face; wall:str|None; corner:bool=False
    def key(self,s):
        if self.kind=="wall": return f"wall:{s[self.i].id}:{self.wall}"
        return f"pair:{s[self.i].id}:{s[self.j].id}:{self.f.name}"

R=Q(F(1,2),F(1,2))
D=Q(F(1),F(1,2))
FS=[Face("E",1,0,R),Face("NE",1,1,D),Face("N",0,1,R),Face("NW",-1,1,D),
    Face("W",-1,0,R),Face("SW",-1,-1,D),Face("S",0,-1,R),Face("SE",1,-1,D)]
FM={f.name:f for f in FS}

def dotq(f,v): return v.x.sc(F(f.nx)).add(v.y.sc(F(f.ny)))
def dotr(f,v): return v.x*f.nx+v.y*f.ny
def bound(f): return f.sup.sc(F(2))
def inside(v): return all(dotq(f,v).cmp(bound(f))<=0 for f in FS)
def active(v): return [f for f in FS if dotq(f,v).eq(bound(f))]
def qmin(a,b): return a if a.cmp(b)<=0 else b
def qmax(a,b): return a if a.cmp(b)>=0 else b

def parse_state(xs):
    ans=[]
    for x in xs:
        p=x["position"]; v=x["velocity"]
        ans.append(Body(x["id"],VQ(Q.parse(p["x"]),Q.parse(p["y"])),VR(F(v["vx"]),F(v["vy"]))))
    return ans
def state_key(s):
    return tuple((b.id,b.pos.x.a,b.pos.x.b,b.pos.y.a,b.pos.y.b,b.vel.x,b.vel.y) for b in s)
def same(a,b): return state_key(a)==state_key(b)
def advance(s,t): return [Body(b.id,b.pos.flow(b.vel,t),VR(b.vel.x,b.vel.y)) for b in s]

def pair_candidate(s,i,j):
    relp=s[j].pos.sub(s[i].pos); relv=s[j].vel.sub(s[i].vel)
    best=None; bf=None
    for f in FS:
        der=dotr(f,relv)
        if der>=0: continue
        gap=dotq(f,relp).sub(bound(f))
        if gap.sign()<=0: continue
        t=gap.dv(-der)
        if t.sign()<=0: continue
        loc=relp.flow(relv,t)
        if not inside(loc) or not dotq(f,loc).eq(bound(f)): continue
        if best is None or t.cmp(best)<0: best,bf=t,f
    if best is None: return None
    n=len(active(relp.flow(relv,best)))
    if n not in (1,2): raise ValueError("multi_face_pair")
    return Event(best,"pair",i,j,bf,None,n==2)

def wall_candidates(s,i,box):
    p=s[i]; neg=box.neg(); ans=[]
    def add(f,w,gap,speed):
        if speed>0 and gap.sign()>0:
            t=gap.dv(speed)
            if t.sign()>0: ans.append(Event(t,"wall",i,None,f,w))
    if p.vel.x>0: add(FM["E"],"E",box.sub(p.pos.x).sub(R),p.vel.x)
    if p.vel.x<0: add(FM["W"],"W",p.pos.x.sub(neg).sub(R),-p.vel.x)
    if p.vel.y>0: add(FM["N"],"N",box.sub(p.pos.y).sub(R),p.vel.y)
    if p.vel.y<0: add(FM["S"],"S",p.pos.y.sub(neg).sub(R),-p.vel.y)
    return ans

def next_batch(s,box):
    es=[]
    for i in range(len(s)):
        es.extend(wall_candidates(s,i,box))
        for j in range(i+1,len(s)):
            e=pair_candidate(s,i,j)
            if e: es.append(e)
    if not es: return []
    t=es[0].t
    for e in es[1:]:
        if e.t.cmp(t)<0: t=e.t
    return [e for e in es if e.t.eq(t)]

def edge_vertices(f):
    k=FS.index(f); ans=[]
    for g in (FS[(k-1)%8], FS[(k+1)%8]):
        det=f.nx*g.ny-f.ny*g.nx
        x=(f.sup.sc(F(g.ny)).sub(g.sup.sc(F(f.ny)))).dv(F(det))
        y=(g.sup.sc(F(f.nx)).sub(f.sup.sc(F(g.nx)))).dv(F(det))
        ans.append(VQ(x,y))
    return ans

def tangent_interval(pos,edge_face,tangent_face):
    # Both opposing contact edges must be projected onto one common tangent
    # orientation, chosen from the first body's contact face.
    values=[]
    for p in edge_vertices(edge_face):
        x=pos.x.add(p.x); y=pos.y.add(p.y)
        values.append(x.sc(F(-tangent_face.ny)).add(y.sc(F(tangent_face.nx))))
    return qmin(values[0],values[1]),qmax(values[0],values[1])

def edge_overlap(contact,e):
    fa=e.f; fb=FS[(FS.index(fa)+4)%8]
    a=tangent_interval(contact[e.i].pos,fa,fa)
    b=tangent_interval(contact[e.j].pos,fb,fa)
    return qmin(a[1],b[1]).sub(qmax(a[0],b[0]))

def resolve(s,events):
    out=[b.cp() for b in s]
    for e in events:
        if e.kind!="pair": continue
        a,b=out[e.i],out[e.j]; n2=e.f.nx*e.f.nx+e.f.ny*e.f.ny
        c=dotr(e.f,b.vel.sub(a.vel))/F(n2)
        a.vel=VR(a.vel.x+c*e.f.nx,a.vel.y+c*e.f.ny)
        b.vel=VR(b.vel.x-c*e.f.nx,b.vel.y-c*e.f.ny)
    for e in events:
        if e.kind!="wall": continue
        p=out[e.i]
        p.vel=VR(-p.vel.x if e.f.nx else p.vel.x,-p.vel.y if e.f.ny else p.vel.y)
    return out

def energy(s): return sum((b.vel.x*b.vel.x+b.vel.y*b.vel.y for b in s),F(0))
def momentum(s): return VR(sum((b.vel.x for b in s),F(0)),sum((b.vel.y for b in s),F(0)))

def valid_state(s,box):
    neg=box.neg()
    for p in s:
        if p.pos.x.sub(R).cmp(neg)<0 or p.pos.x.add(R).cmp(box)>0 or p.pos.y.sub(R).cmp(neg)<0 or p.pos.y.add(R).cmp(box)>0:
            return "wall_escape:"+p.id
    for i in range(len(s)):
        for j in range(i+1,len(s)):
            d=s[j].pos.sub(s[i].pos)
            if inside(d):
                ac=active(d)
                if not ac: return f"overlap:{s[i].id}:{s[j].id}"
                rel=s[j].vel.sub(s[i].vel)
                for f in ac:
                    if dotr(f,rel)<0: return f"approaching:{s[i].id}:{s[j].id}:{f.name}"
    return None

def batch_class(events):
    if any(e.kind=="pair" and e.corner for e in events): return "unknown_pair_corner"
    use={}
    for e in events:
        use.setdefault(e.i,[]).append(e)
        if e.kind=="pair": use.setdefault(e.j,[]).append(e)
    for hits in use.values():
        if any(e.kind=="pair" for e in hits) and len(hits)>1: return "shared_body_batch"
        ws=[e for e in hits if e.kind=="wall"]
        if len(ws)>2: return "three_wall_batch"
        if len(ws)==2 and ws[0].f.nx*ws[1].f.nx+ws[0].f.ny*ws[1].f.ny!=0:
            return "nonperpendicular_double_wall"
    return "resolvable"


def frac_bits(x:F): return max(abs(x.numerator).bit_length(), x.denominator.bit_length())
def state_complexity_bits(s):
    return max((frac_bits(z) for b in s for z in (b.pos.x.a,b.pos.x.b,b.pos.y.a,b.pos.y.b,b.vel.x,b.vel.y)), default=0)

def check_data(seed, run, source='embedded'):
    initial=parse_state(seed["state"]); box=Q.parse(seed["container"]["half_box"])
    cur=initial; prev_t=Q(F(0),F(0)); seen={state_key(initial):0}; cycle=None
    errs=[]; rows=[]; pair_count=wall_count=mixed_count=0; max_bits=state_complexity_bits(initial); cutoff=int(run.get("complexity_cutoff_bits",0) or 0); cutoff_witness=None
    for row in run["ledger"]:
        i=row["index"]; pre=parse_state(row["pre"]); post=parse_state(row["post"]); now=Q.parse(row["time"]); dt=now.sub(prev_t)
        bad=[]
        if i!=len(rows)+1: bad.append("nonconsecutive_index")
        if not same(pre,cur): bad.append("pre_state_discontinuity")
        if now.cmp(prev_t)<=0: bad.append("nonincreasing_time")
        pre_bits=state_complexity_bits(pre); post_bits=state_complexity_bits(post)
        max_bits=max(max_bits,pre_bits,post_bits)
        if cutoff and (pre_bits>cutoff or post_bits>cutoff): bad.append("recorded_state_exceeds_complexity_cutoff")
        e=valid_state(pre,box)
        if e: bad.append("invalid_pre:"+e)
        contact=advance(pre,dt); batch=next_batch(pre,box)
        if not batch:
            bad.append("no_future_event")
        else:
            if sorted(row["events"])!=sorted(e.key(pre) for e in batch): bad.append("event_set_mismatch")
            if batch_class(batch)!="resolvable": bad.append("recorded_unresolvable:"+batch_class(batch))
            for ev in batch:
                if ev.kind=="pair":
                    pair_count+=1
                    if ev.corner: bad.append("pair_corner")
                    if edge_overlap(contact,ev).sign()<=0: bad.append("nonpositive_edge_overlap")
                    if len(active(contact[ev.j].pos.sub(contact[ev.i].pos)))!=1: bad.append("pair_not_single_face")
                    if dotr(ev.f,contact[ev.j].vel.sub(contact[ev.i].vel))>=0: bad.append("pair_not_approaching")
                else:
                    wall_count+=1
                    p=contact[ev.i]; want=box if ev.wall in ("E","N") else box.neg()
                    if ev.wall=="E": got=p.pos.x.add(R)
                    elif ev.wall=="W": got=p.pos.x.sub(R)
                    elif ev.wall=="N": got=p.pos.y.add(R)
                    else: got=p.pos.y.sub(R)
                    if not got.eq(want): bad.append("wall_location_mismatch")
            if any(e.kind=="pair" for e in batch) and any(e.kind=="wall" for e in batch): mixed_count+=1
            if not same(resolve(contact,batch),post): bad.append("post_state_mismatch")
            if energy(pre)!=energy(post): bad.append("energy_not_conserved")
            p0,p1=momentum(pre),momentum(post)
            if all(e.kind=="pair" for e in batch) and not p0.eq(p1): bad.append("pair_momentum_not_conserved")
            wd=VR(F(0),F(0))
            for ev in batch:
                if ev.kind=="wall":
                    v=contact[ev.i].vel
                    after=VR(-v.x if ev.f.nx else v.x,-v.y if ev.f.ny else v.y)
                    wd=wd.add(VR(after.x-v.x,after.y-v.y))
            if (p1.x-p0.x,p1.y-p0.y)!=(wd.x,wd.y): bad.append("wall_impulse_balance_failure")
        e=valid_state(post,box)
        if e: bad.append("invalid_post:"+e)
        k=state_key(post)
        if k in seen and cycle is None:
            cycle={"first_post_index":seen[k],"repeat_post_index":i,"period_batches":i-seen[k]}
        else: seen.setdefault(k,i)
        rows.append({"index":i,"ok":not bad,"errors":bad})
        errs += [f"row_{i}:{x}" for x in bad]
        cur=post; prev_t=now
    if len(run["ledger"])!=run["completed_batches"]: errs.append("completed_batch_count_mismatch")
    if run["stop_class"]=="return":
        terminal="return" if same(cur,initial) else "return_state_mismatch"
        if terminal!="return": errs.append(terminal)
    elif run["stop_class"]=="completed_budget":
        terminal="completed_budget"
    elif run["stop_class"]=="complexity_cutoff":
        tail=next_batch(cur,box)
        terminal="complexity_cutoff"
        if not cutoff: errs.append("missing_complexity_cutoff_bits")
        elif not tail: errs.append("complexity_cutoff_without_next_event")
        elif batch_class(tail)!="resolvable": errs.append("complexity_cutoff_preempted_by_"+batch_class(tail))
        else:
            now=advance(cur,tail[0].t); nxt=resolve(now,tail); nb=state_complexity_bits(nxt)
            cutoff_witness={"next_batch_time":{"a":str(tail[0].t.a),"b":str(tail[0].t.b)},"next_state_complexity_bits":nb}
            if nb<=cutoff: errs.append("complexity_cutoff_not_exceeded")
            if int(run.get("next_complexity_bits",0) or 0)!=nb: errs.append("next_complexity_bits_mismatch")
    else:
        tail=next_batch(cur,box)
        terminal=batch_class(tail) if tail else "no_future_event"
        if terminal!=run["stop_class"]: errs.append(f"terminal_mismatch:{run['stop_class']}:{terminal}")
    if int(run.get("max_complexity_bits_observed",max_bits) or 0)!=max_bits: errs.append("max_complexity_bits_observed_mismatch")
    retain=not errs and run["stop_class"] in ("completed_budget","complexity_cutoff") and cycle is None and pair_count>0
    return {
      "schema":"c4-clock-independent-check/v1","seed":source,"run":source,"mask_bits":run["mask_bits"],
      "completed_batches":run["completed_batches"],"stop_class_claimed":run["stop_class"],"terminal_class_independent":terminal,
      "all_completed_rows_ok":not errs,"errors":errs,"cycle":cycle,"pair_contacts":pair_count,"wall_contacts":wall_count,
      "mixed_batches":mixed_count,"complexity_cutoff_bits":cutoff,"max_complexity_bits_observed":max_bits,"complexity_cutoff_witness":cutoff_witness,"retained_for_ternary_comparison":retain,
      "retention_reason":"eligible" if retain else ("cycle_detected" if cycle else ("no_pair_contacts" if pair_count==0 else "terminal_"+run["stop_class"])),
      "rows":rows
    }

def check(seed_path, run_path):
    return check_data(json.loads(Path(seed_path).read_text()), json.loads(Path(run_path).read_text()), f'{seed_path}|{run_path}')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--seed",type=Path,required=True); ap.add_argument("--run",type=Path,required=True); ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); report=check(a.seed,a.run)
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(report,indent=2)+"\n")
    print(f"mask={report['mask_bits']:03d} rows={report['completed_batches']} ok={report['all_completed_rows_ok']} stop={report['terminal_class_independent']} retain={report['retained_for_ternary_comparison']}")
    if not report["all_completed_rows_ok"]: sys.exit(1)
if __name__=="__main__": main()
