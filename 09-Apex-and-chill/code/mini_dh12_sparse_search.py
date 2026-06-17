#!/usr/bin/env python3
import json, random, hashlib, argparse, time, os, collections
from pathlib import Path
DIRS=[(1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)]
SEED={(1,0):'H.3',(1,-1):'H.2',(0,-1):'H.1',(-1,0):'H.0',(-1,1):'H.5',(0,1):'H.4'}
BLOCKED={(0,0)}

def rot_state(st,k):
    if st=='*': return '*'
    t,i=st.split('.'); return f'{t}.{(int(i)-k)%6}'
def inv_rot_state(st,k):
    if st=='*': return '*'
    t,i=st.split('.'); return f'{t}.{(int(i)+k)%6}'
def rotate_key(raw,k):
    out=['*']*6
    for p,st in enumerate(raw): out[(p+k)%6]=rot_state(st,k)
    return tuple(out)
def canon(raw):
    c=[rotate_key(tuple(raw),k) for k in range(6)]
    b=min(c); return b,c.index(b)
def frontier(state):
    out=set()
    for q,r in state:
        for dq,dr in DIRS:
            c=(q+dq,r+dr)
            if c not in state and c not in BLOCKED: out.add(c)
    return out

def replay(acc, rej, max_steps=300):
    state=dict(SEED); hist=[]; useda=set(); usedr=set(); unknown=[]
    for t in range(max_steps):
        births={}; unknown=[]; rejc=0
        for q,r in sorted(frontier(state)):
            raw=tuple(state.get((q+dq,r+dr),'*') for dq,dr in DIRS)
            key,k=canon(raw)
            if key in acc:
                births[(q,r)]=inv_rot_state(acc[key],k); useda.add(key)
            elif key in rej:
                rejc+=1; usedr.add(key)
            else:
                unknown.append((q,r,key,k))
        hist.append({'t':t,'births':len(births),'placed':len(state)+len(births),'unknown_frontier':len(unknown),'rejected_frontier':rejc})
        if not births:
            break
        state.update(births)
    return {'cells':len(state),'terminal_step':hist[-1]['t'],'terminal_births':hist[-1]['births'],'unknown':hist[-1]['unknown_frontier'],'rejected_frontier':hist[-1]['rejected_frontier'],'used_accept':len(useda),'used_reject':len(usedr),'state':state,'history':hist}

def parse_record(rec):
    acc={tuple(x['key']):x['out'] for x in rec['output']}
    rej={tuple(x) for x in rec['blank_keys'] if tuple(x) not in acc}
    return acc,rej

def digest(acc,rej):
    rows=[]
    for k,v in sorted(acc.items()): rows.append('A|'+'|'.join(k)+'->'+v)
    for k in sorted(rej): rows.append('R|'+'|'.join(k))
    return hashlib.sha256('\n'.join(rows).encode()).hexdigest()[:16]

def materialize(acc,rej,evalr,op,parents,seed):
    return {
        'format':'mini_dh12_sparse_candidate_v1', 'model':'dh12', 'operator':op, 'parents':parents, 'search_seed':seed,
        'rule_hash':digest(acc,rej), 'cells':evalr['cells'], 'status':'CLOSED_CHILL' if evalr['terminal_births']==0 and evalr['unknown']==0 else 'PARTIAL_OR_OPEN',
        'depth':evalr['terminal_step'], 'accept':len(acc), 'reject':len(rej), 'used_accept':evalr['used_accept'], 'used_reject':evalr['used_reject'],
        'terminal_unknown_frontier':evalr['unknown'], 'terminal_rejected_frontier':evalr['rejected_frontier'],
        'output':[{'key':list(k),'out':v} for k,v in sorted(acc.items())],
        'blank_keys':[list(k) for k in sorted(rej)],
        'state':[[q,r,s] for (q,r),s in sorted(evalr['state'].items())],
        'history':evalr['history'],
    }

def load_records(paths):
    out=[]
    for path in paths:
        p=Path(path)
        if p.suffix=='.jsonl':
            with p.open() as f:
                for i,line in enumerate(f,1):
                    if not line.strip(): continue
                    rec=json.loads(line); acc,rej=parse_record(rec); ev=replay(acc,rej)
                    rec['_loaded_from']=str(p); rec['_line']=i; rec['_eval']=ev; rec['_digest']=digest(acc,rej); rec['_acc']=acc; rec['_rej']=rej
                    out.append(rec)
        elif p.suffix=='.json':
            rec=json.loads(p.read_text()); acc,rej=parse_record(rec); ev=replay(acc,rej)
            rec['_loaded_from']=str(p); rec['_line']=1; rec['_eval']=ev; rec['_digest']=digest(acc,rej); rec['_acc']=acc; rec['_rej']=rej
            out.append(rec)
    return out

def status_of(acc,rej,key):
    if key in acc: return ('A',acc[key])
    if key in rej: return ('R',None)
    return ('B',None)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--records', nargs='+', required=True)
    ap.add_argument('--outdir', required=True)
    ap.add_argument('--seed', type=int, default=2026061609)
    ap.add_argument('--mutations', type=int, default=2000)
    ap.add_argument('--mates', type=int, default=1000)
    ap.add_argument('--keep-min', type=int, default=800)
    ns=ap.parse_args()
    random.seed(ns.seed)
    outdir=Path(ns.outdir); outdir.mkdir(parents=True,exist_ok=True)
    recs=load_records(ns.records)
    parents=[]
    for r in recs:
        ev=r['_eval']
        if ev['terminal_births']==0 and ev['unknown']==0:
            parents.append(r)
    # observed output prior by key, and key universe
    out_counts=collections.defaultdict(collections.Counter); key_counts=collections.Counter(); key_status_counts=collections.defaultdict(collections.Counter)
    for r in parents:
        acc,rej=r['_acc'],r['_rej']
        for k,v in acc.items(): out_counts[k][v]+=1; key_counts[k]+=1; key_status_counts[k]['A']+=1
        for k in rej: key_counts[k]+=1; key_status_counts[k]['R']+=1
    universe=sorted(key_counts)
    def default_out(k):
        return out_counts[k].most_common(1)[0][0] if out_counts[k] else 'H.0'
    parent_weight=[max(1,r['_eval']['cells']-600) for r in parents]
    seen={r['_digest'] for r in recs}; found=[]; trials=[]
    best_by_hash={r['_digest']: {'source':'seed','hash':r.get('rule_hash',r['_digest']),'cells':r['_eval']['cells'],'unknown':r['_eval']['unknown'],'status':r.get('status'),'operator':r.get('operator')} for r in recs}
    def maybe_store(acc,rej,ev,op,parents_ids):
        h=digest(acc,rej)
        recsum={'hash':h,'cells':ev['cells'],'unknown':ev['unknown'],'step':ev['terminal_step'],'status':'CLOSED_CHILL' if ev['terminal_births']==0 and ev['unknown']==0 else 'PARTIAL_OR_OPEN','operator':op,'parents':parents_ids,'used_accept':ev['used_accept'],'used_reject':ev['used_reject'],'accept':len(acc),'reject':len(rej)}
        trials.append(recsum)
        old=best_by_hash.get(h)
        if old is None or ev['cells']>old.get('cells',-1): best_by_hash[h]=recsum
        if h not in seen and ev['terminal_births']==0 and ev['unknown']==0 and ev['cells']>=ns.keep_min:
            seen.add(h)
            cand=materialize(acc,rej,ev,op,parents_ids,ns.seed)
            found.append(cand)
            (outdir/f'candidate_{len(found):04d}_{ev["cells"]:05d}_{h}.json').write_text(json.dumps(cand,indent=2,sort_keys=True)+'\n')
    # mutation search: small edits around good parents
    for t in range(ns.mutations):
        p=random.choices(parents, weights=parent_weight, k=1)[0]
        acc=dict(p['_acc']); rej=set(p['_rej'])
        n_edits=random.choice([1,1,1,2,2,3,4])
        for _ in range(n_edits):
            mode=random.random()
            if mode<0.35 and rej:
                k=random.choice(sorted(rej)); rej.discard(k)
                # often accept with observed output, sometimes drop to blank
                if out_counts[k] and random.random()<0.75: acc[k]=default_out(k)
            elif mode<0.65 and acc:
                k=random.choice(sorted(acc)); acc.pop(k,None)
                if random.random()<0.65: rej.add(k)
            else:
                # add high frequency absent key as accept/reject
                k=random.choice(universe)
                if k not in acc and k not in rej:
                    if key_status_counts[k]['A']>=key_status_counts[k]['R'] and out_counts[k]: acc[k]=default_out(k)
                    else: rej.add(k)
        # avoid overlaps
        rej={k for k in rej if k not in acc}
        ev=replay(acc,rej)
        maybe_store(acc,rej,ev,'MINI_MUTATE',[p.get('rule_hash',p['_digest'])])
    # pair mating: choose per-key statuses from parents and sprinkle blanks
    top=sorted(parents,key=lambda r:r['_eval']['cells'],reverse=True)
    for t in range(ns.mates):
        a,b=random.sample(top[:min(len(top),40)],2)
        keys=set(a['_acc'])|set(a['_rej'])|set(b['_acc'])|set(b['_rej'])
        acc={}; rej=set()
        bias=random.random()
        for k in keys:
            choices=[status_of(a['_acc'],a['_rej'],k), status_of(b['_acc'],b['_rej'],k)]
            # maybe blank rare disagreements
            if choices[0]!=choices[1] and random.random()<0.12:
                continue
            st,out=random.choice(choices if random.random()<0.5 else [choices[0] if a['_eval']['cells']>=b['_eval']['cells'] else choices[1]])
            if st=='A': acc[k]=out
            elif st=='R': rej.add(k)
        # small mutation after mating
        for _ in range(random.choice([0,1,1,2])):
            k=random.choice(universe)
            if random.random()<0.5 and out_counts[k]: acc[k]=default_out(k); rej.discard(k)
            else: acc.pop(k,None); rej.add(k)
        rej={k for k in rej if k not in acc}
        ev=replay(acc,rej)
        maybe_store(acc,rej,ev,'MINI_MATE',[a.get('rule_hash',a['_digest']),b.get('rule_hash',b['_digest'])])
    summary={
        'seed':ns.seed,'loaded_records':len(recs),'valid_parent_records':len(parents),'input_records_by_cells':collections.Counter(str(r['_eval']['cells']) for r in recs),
        'trials':len(trials),'mutations':ns.mutations,'mates':ns.mates,'new_closed_chill_ge_keep_min':len(found),
        'found_by_cells':collections.Counter(str(r['cells']) for r in found),
        'best_trial_cells':max([x['cells'] for x in trials], default=0),'best_new_cells':max([r['cells'] for r in found], default=0),
        'top_trials':sorted(trials,key=lambda x:(x['cells'],-x['unknown']),reverse=True)[:20],
        'found_index':[{'file':f'candidate_{i+1:04d}_{r["cells"]:05d}_{r["rule_hash"]}.json','hash':r['rule_hash'],'cells':r['cells'],'step':r['depth'],'op':r['operator'],'parents':r['parents'],'used_accept':r['used_accept'],'used_reject':r['used_reject'],'accept':r['accept'],'reject':r['reject']} for i,r in enumerate(found)]
    }
    (outdir/'mini_search_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True,default=dict)+'\n')
    (outdir/'mini_search_trials_top.jsonl').write_text('\n'.join(json.dumps(x,sort_keys=True) for x in sorted(trials,key=lambda x:x['cells'],reverse=True)[:200])+'\n')
    print(json.dumps(summary,indent=2,sort_keys=True,default=dict))
if __name__=='__main__': main()
