import json, csv, itertools, time, sys
from pathlib import Path
from collections import defaultdict, Counter

BASE=Path('/mnt/data/c6_rephex_catalogues_v2')
DIRS=[(1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)]
SEED=[(1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)]
BLOCK={(0,0)}

def parse_dat(path):
    cells={}
    for line in Path(path).read_text().splitlines():
        if not line.strip() or line.startswith('#'): continue
        q,r,state,ori,ci,dc,leaf=line.split()[:7]
        cells[(int(q),int(r))]={'state':state,'ori':int(ori)%6,'color':int(ci),'dark':int(dc),'leaf':leaf}
    return cells

def make_labeler(model):
    def dh12(c):
        s=c['state']
        if s=='F': return None
        if s=='0': return f'D.{c["ori"]%6}'
        if s=='1': return f'D.{(c["ori"]+3)%6}'
        return f'H.{c["ori"]%6}'
    def ordinary(c):
        s=c['state']
        if s=='F': return None
        if s=='0': return f'D0.{c["ori"]%6}'
        if s=='1': return f'D1.{(c["ori"]+3)%6}'
        return f'H.{c["ori"]%6}'
    def tree(c):
        s=c['state']
        if s=='F': return None
        if s=='0': return f'D0.{c["ori"]%6}'
        if s=='1': return f'D1.{(c["ori"]+3)%6}'
        name={'B':'PASS','C':'CAP','G':'LEAF'}.get(s,s)
        return f'{name}.{c["ori"]%6}'
    def split(c):
        s=c['state']
        if s=='F': return None
        if s=='G':
            if c['leaf']=='U': return None
            name={'T':'TRI','P':'PAR'}.get(c['leaf'],'LEAF')
            return f'{name}.{c["ori"]%6}'
        if s=='0': return f'D0.{c["ori"]%6}'
        if s=='1': return f'D1.{(c["ori"]+3)%6}'
        name={'B':'PASS','C':'CAP'}.get(s,s)
        return f'{name}.{c["ori"]%6}'
    return {'dh12':dh12,'ordinary':ordinary,'tree':tree,'split':split}[model]

def target_for(model,level=4):
    source='split' if model=='split' else 'ordinary'
    cells=parse_dat(BASE/f'raw_targets/F_L{level}.{source}.current.dat')
    lab=make_labeler(model)
    return {p:x for p,c in cells.items() if (x:=lab(c)) is not None}

def rot_pos(p,k):
    q,r=p
    for _ in range(k%6): q,r=q+r,-q
    return (q,r)

def rot_label(label,k):
    typ,ori=label.rsplit('.',1)
    return f'{typ}.{(int(ori)-k)%6}'

def c6_state_ok(state):
    for p,lab in state.items():
        for k in range(1,6):
            rp=rot_pos(p,k)
            if rp not in state or state[rp]!=rot_label(lab,k): return False
    return True

def canon_visible(neigh):
    best=None; best_k=0
    for k in range(6):
        arr=['*']*6
        for i,lab in enumerate(neigh):
            if lab!='*': arr[(i+k)%6]=rot_label(lab,k)
        tup=tuple(arr)
        if best is None or tup<best: best=tup; best_k=k
    return best,best_k

def to_canon(label,k): return rot_label(label,k)
def to_phys(label,k): return rot_label(label,-k)

def nbrs(p):
    q,r=p
    for dq,dr in DIRS: yield (q+dq,r+dr)

def boundary(state):
    occ=set(state)|BLOCK; fr=set()
    for p in occ:
        for n in nbrs(p):
            if n not in occ: fr.add(n)
    return fr

def visible_for(pos,state):
    q,r=pos; arr=[]; vis=0
    for dq,dr in DIRS:
        n=(q+dq,r+dr)
        if n in state: arr.append(state[n]); vis+=1
        else: arr.append('*')
    return arr if vis else None

def orbit_frontier_escape(state,TARGET):
    for pos in boundary(state):
        for k in range(6):
            rp=rot_pos(pos,k)
            if rp!=(0,0) and rp not in TARGET:
                return ('ESCAPE', {'pos':pos,'rpos':rp})
    return None

def collect_event(node,TARGET):
    esc=orbit_frontier_escape(node[0],TARGET)
    if esc: return esc
    state,outmap,blank,depth,hist=node
    known=[]; unknown=defaultdict(list); forced=[]
    for pos in sorted(boundary(state), key=lambda p:(p[1],p[0])):
        if pos not in TARGET: return 'ESCAPE', {'pos':pos}
        vis=visible_for(pos,state)
        if vis is None: continue
        key,k=canon_visible(vis)
        if key in blank: continue
        if key in outmap:
            lab=to_phys(outmap[key],k)
            if lab!=TARGET[pos]: return 'DEAD', {'pos':pos,'got':lab,'target':TARGET[pos]}
            known.append((pos,lab,key))
        else:
            canon_t=to_canon(TARGET[pos],k)
            unknown[key].append((pos,k,canon_t,TARGET[pos]))
    U={}
    for key,uses in unknown.items():
        outs={u[2] for u in uses}
        if len(outs)!=1: forced.append(key)
        else: U[key]={'out':next(iter(outs)),'uses':uses}
    if not known and not U and not forced: return 'CHILL', {}
    return 'BRANCH', {'known':known,'U':U,'forced_blank':forced}

def c6_birth_packet_ok(old_state, bypos):
    for pos,lab in bypos.items():
        for k in range(6):
            rp=rot_pos(pos,k); rlab=rot_label(lab,k)
            if rp==(0,0): continue
            if rp in old_state:
                if old_state[rp]!=rlab: return False
            elif rp in bypos:
                if bypos[rp]!=rlab: return False
            else: return False
    return True

def apply_subset(node,data,sub):
    state,outmap,blank,depth,hist=node
    ns=dict(state); no=dict(outmap); nb=set(blank); sub=set(sub); U=data['U']
    for k in data.get('forced_blank',[]):
        if k in no: return None,'forced_blank_conflict'
        nb.add(k)
    for k,info in U.items():
        if k in sub:
            if k in nb: return None,'accept_blank'
            if k in no and no[k]!=info['out']: return None,'out_conflict'
            no[k]=info['out']
        else:
            if k in no: return None,'reject_accepted'
            nb.add(k)
    births=list(data['known'])
    for k in sub:
        for pos,rot,canon,target in U[k]['uses']:
            phys=to_phys(canon,rot)
            if phys!=target: return None,'target_mismatch'
            births.append((pos,phys,k))
    bypos={}
    for pos,lab,k in births:
        if pos in bypos and bypos[pos]!=lab: return None,'two_labels'
        bypos[pos]=lab
    if not c6_birth_packet_ok(state,bypos): return None,'c6_birth_packet_break'
    for pos,lab in bypos.items():
        if pos in ns and ns[pos]!=lab: return None,'overwrite'
        ns[pos]=lab
    entry={'t':depth,'U':len(U),'known_births':len(data['known']),'accepted':len(sub),'rejected':len(U)-len(sub),'forced_blank':len(data.get('forced_blank',[])),'births':len(bypos),'placed':len(ns)}
    return (ns,no,frozenset(nb),depth+1,hist+(entry,)),None

def exact(model,max_depth=5,max_power=12,level=4):
    TARGET=target_for(model,level)
    root=({p:TARGET[p] for p in SEED}, {}, frozenset(),0,tuple())
    ok=c6_state_ok(root[0])
    stack=[root]; seen=0; terms=Counter(); bydepth=Counter(); raw=defaultdict(lambda:Counter()); best=root; rejects=Counter()
    t0=time.time()
    while stack:
        node=stack.pop(); seen+=1; d=node[3]; bydepth[d]+=1
        if len(node[0])>len(best[0]): best=node
        if d>=max_depth: terms['DEPTH_LIMIT']+=1; continue
        st,data=collect_event(node,TARGET)
        if st!='BRANCH': terms[st]+=1; continue
        U=data['U']; n=len(U); raw[d]['U_sum']+=n; raw[d]['frontier_nodes']+=1
        if n>max_power: terms['TOO_WIDE']+=1; continue
        keys=sorted(U.keys()); total=0; valid=0
        for r in range(n+1):
            for sub in itertools.combinations(keys,r):
                total+=1
                ch,err=apply_subset(node,data,sub)
                if ch is None: rejects[err]+=1; raw[d]['invalid_'+str(err)]+=1
                else: valid+=1; stack.append(ch)
        raw[d]['raw_powerset_children']+=total; raw[d]['valid_children']+=valid
    return {'model':model,'level':level,'max_depth':max_depth,'max_power':max_power,'seed_c6_ok':ok,'seen':seen,'nodes_by_depth':dict(bydepth),'terminal_counts':dict(terms),'best_cells':len(best[0]),'best_depth':best[3],'best_accept':len(best[1]),'best_blank':len(best[2]),'rejects':dict(rejects),'raw':{str(k):dict(v) for k,v in raw.items()},'elapsed':time.time()-t0}

if __name__=='__main__':
    out=Path('/mnt/data/c6_short_shots')
    out.mkdir(exist_ok=True)
    rows=[]
    for model in ['ordinary','tree','split']:
        # conservative short shot
        r=exact(model,max_depth=int(sys.argv[1]) if len(sys.argv)>1 else 5,max_power=12,level=4)
        rows.append(r); (out/f'{model}_summary.json').write_text(json.dumps(r,indent=2)); print(json.dumps(r,indent=2), flush=True)
    (out/'combined.json').write_text(json.dumps(rows,indent=2))
