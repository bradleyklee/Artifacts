"""Measured release candidate: six-phase Scott-tag λ controller with searchable real E(P).
Python is the β-evaluator and observation/IO boundary, not an action dispatcher.
The six Scott phases are NOT the six literal reductions of the raw quine.
"""
import argparse, csv, json, resource, time, pathlib
from lambda_runtime import *

# PHASE tags: Scott-encoded choice, λh0...h5.hi.
def tag(i):
    assert 0 <= i < 6
    t=V(5-i)
    for _ in range(6): t=L(t)
    return t
TAGS=tuple(tag(i) for i in range(6))
ADD=abstract(['m','n','f','x'],E('m','f',E('n','f','x')))
STEP=L(app(V(0),L(L(app(shift(PAIR,2),V(0),app(shift(ADD,2),V(1),V(0)))))))
EXPORT_ID=L(V(0))
# Each handler produces (next phase, product), with Q2 improving, Q4 exporting.
handlers=[]
for i in range(6):
    p=(app(shift(STEP,1),V(0)) if i==2 else
       app(shift(EXPORT_ID,1),V(0)) if i==4 else V(0))
    handlers.append(L(app(shift(PAIR,1),shift(TAGS[(i+1)%6],1),p)))
DISPATCH=L(L(app(V(1),*[shift(h,2) for h in handlers],V(0))))

CLOCK=[]
q=Q
for i in range(6):
    CLOCK.append(q)
    _,q=cpu_tick(q)
assert q==Q and len(set(CLOCK))==6

def named_clock(t):
    for i,q in enumerate(CLOCK):
        if q==t:return f'Q{i}'
    return '?'

def decode_tag(t):
    for i,q in enumerate(TAGS):
        if q==t:return i
    raise ValueError('invalid λ clock tag')

def pair_values(t):
    a=numeral_value(app(FST,t)); b=numeral_value(app(SND,t))
    return a,b

def count_nodes(t):
    if isinstance(t,V):return 1
    if isinstance(t,L):return 1+count_nodes(t.body)
    return 1+count_nodes(t.f)+count_nodes(t.x)

def eval_step(term, limit=200000, track_export=False, history=None, cycle=None, phase=None):
    # One deterministic leftmost-outermost reducer, no host-side phase dispatch.
    n=0; seen=[]; root=None; export_before=None; export_after=None
    while n < limit:
        path=next(iter(redexes(term)),None)
        if path is None:return term,n,seen
        r=at(term,path)
        if track_export and r.f==EXPORT_ID:
            # A real beta-redex headed by E=λx.x is about to contract.
            # Only one such exported redex is expected on the Q4 branch.
            export_before=r
        updated=beta(term,path);n+=1
        if history is not None:
            history.write(json.dumps({"cycle":cycle,"phase":phase,"beta":n,"redex_path":"".join(path),"before_prefix":prefix(term),"after_prefix":prefix(updated)})+"\n")
        if export_before is not None and r==export_before:
            assert at(updated,path)==r.x
            seen.append((n,path,r.x))
            export_before=None
        term=updated
    raise RuntimeError('beta budget exceeded')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--cycles',type=int,default=10)
    ap.add_argument('--out',default='trace')
    ap.add_argument('--full-beta',action='store_true',help='retain every complete beta-reduction before/after term')
    args=ap.parse_args()
    out=pathlib.Path(args.out);out.mkdir(parents=True,exist_ok=True)
    q=TAGS[0]; product=pair(N(0),N(1))
    measurements=[]; exports=[]; start=time.perf_counter()
    with (out/'readable_trace.txt').open('w') as trace, (out/'events.jsonl').open('w') as evt, (out/'beta_history.jsonl').open('w') as history:
        def emit(line): trace.write(line+'\n');print(line)
        emit('Quine Fibonacci release candidate; E(P) denotes a real λ identity redex.')
        emit('NOTICE: live clock is Scott-encoded; original raw Q six-β clock verified separately.')
        for cyc in range(args.cycles):
            for phase in range(6):
                expr=app(DISPATCH,q,product)
                t0=time.perf_counter();result,n,marks=eval_step(expr,track_export=True,history=history if args.full_beta else None,cycle=cyc+1,phase=phase)
                wall=time.perf_counter()-t0
                nq,_=normalize(app(FST,result));np,_=normalize(app(SND,result))
                a,b=pair_values(np)
                actual_phase=decode_tag(q);newphase=decode_tag(nq)
                assert actual_phase==phase and newphase==(phase+1)%6
                # Inspect and reduce a real lambda event, do not infer from phase alone.
                if phase==4:
                    assert len(marks)==1, f'Q4 must contract exactly one E(P), got {len(marks)}'
                    exp_a,exp_b=pair_values(marks[0][2])
                    assert (exp_a,exp_b)==(a,b)
                    e_text=f'E(P) = E(({exp_a},{exp_b})) -> ({exp_a},{exp_b})'
                    emit(f'  {e_text}  [actual beta step {marks[0][0]} in transition]')
                    exports.append((exp_a,exp_b))
                    event={'kind':'export','cycle':cyc+1,'beta_in_dispatch':marks[0][0],'pair':[exp_a,exp_b], 'redex_path':''.join(marks[0][1])}
                    evt.write(json.dumps(event)+'\n')
                else:
                    # Identity-shaped redexes can occur inside unrelated lambda terms.
                    # Only the Q4 handler's explicit identity application is an export.
                    pass
                line=f'cycle {cyc+1:02d} Q{phase}->Q{newphase}: β[{n}] product=({a},{b}) time={wall:.6f}s'
                emit(line)
                measurements.append({'cycle':cyc+1,'phase':phase,'to':newphase,'beta_dispatch':n,'elapsed_seconds':round(wall,7),'product_a':a,'product_b':b,'input_nodes':count_nodes(expr),'output_nodes':count_nodes(result),'rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
                q,product=nq,np
            emit(f'completed cycle {cyc+1}, exported ({exports[-1][0]},{exports[-1][1]})')
    assert len(exports)==args.cycles
    expected=(0,1)
    for pair_out in exports:
        expected=(expected[1],sum(expected))
        assert pair_out==expected
    with (out/'measurements.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=measurements[0].keys());w.writeheader();w.writerows(measurements)
    total=sum(x['beta_dispatch'] for x in measurements)
    summary={'cycles':args.cycles,'exports':len(exports),'dispatch_beta':total,'dispatch_beta_by_phase':{str(i):sorted(set(x['beta_dispatch'] for x in measurements if x['phase']==i)) for i in range(6)},'seconds_total':round(time.perf_counter()-start,5),'max_rss_kib':max(x['rss_kib'] for x in measurements),'raw_clock_distinct_states':6,'raw_clock_exact_return_beta':6,'raw_clock_coupled_to_controller':False,'export_redex_observed':True,'full_beta_recorded':args.full_beta,'readout_and_normalization_beta_excluded_from_dispatch_cost':True}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
