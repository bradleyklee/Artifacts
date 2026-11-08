"""Constant-size Scott-tag lambda dispatch benchmark.
Pure lambda decides branch and Fibonacci improvement; Python only reduces and decodes.
Not a raw Q clock integration.
"""
import argparse, csv, json, time, tracemalloc, resource
from pathlib import Path
from lambda_runtime import *

# All tags are closed lambda terms representing each known canonical quotation.
def tag(i):
    x=V(5-i)
    for _ in range(6): x=L(x)
    return x
TAGS=[tag(i) for i in range(6)]
ADD=abstract(['m','n','f','x'],E('m','f',E('n','f','x')))
STEP=L(app(V(0),L(L(app(shift(PAIR,2),V(0),app(shift(ADD,2),V(1),V(0)))))) )
IDENTITY=L(V(0))
# One closed 6-way dispatcher: λq.λp. q handler0...handler5 p
# Handlers return pair(next_tag, product), with STEP only at Q2.
handlers=[]
for i in range(6):
    # λp. PAIR tag_next (STEP p)   or   λp. PAIR tag_next p
    prod=app(shift(STEP,1),V(0)) if i==2 else V(0)
    handlers.append(L(app(shift(PAIR,1),shift(TAGS[(i+1)%6],1),prod)))
DISPATCH=L(L(app(V(1),*[shift(h,2) for h in handlers],V(0))))

# Quotations independently correspond to original raw Q clock states:
Q_STATES=[]
cur=Q
for _ in range(6):
    Q_STATES.append(cur)
    _,cur=cpu_tick(cur)
assert cur==Q and len(set(map(prefix,Q_STATES)))==6

def decode_state(t):
    # Scott tag observer supplied only after lambda reduction has normalized t.
    # Observer is a test assertion, not an action selector.
    for i in range(6):
        if t==TAGS[i]: return i
    raise AssertionError('unknown state')

def sample_step(q,p,iteration,stats):
    expr=app(DISPATCH,q,p)
    start=time.perf_counter()
    out,n=normalize(expr,limit=100000)
    dt=time.perf_counter()-start
    qout,_=normalize(app(FST,out))
    pout,_=normalize(app(SND,out))
    newq=decode_state(qout)
    # decode an already-normalized Church-encoded product; this measures reader cost separately
    a=numeral_value(app(FST,pout)); b=numeral_value(app(SND,pout))
    record={'transition':iteration,'from':decode_state(q),'to':newq,'beta':n,'seconds':round(dt,6),'product_a':a,'product_b':b,'term_nodes_input':node_count(expr),'term_nodes_output':node_count(out),'ru_maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    stats.append(record)
    return qout,pout

def node_count(t):
    if isinstance(t,V):return 1
    if isinstance(t,L):return 1+node_count(t.body)
    return 1+node_count(t.f)+node_count(t.x)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cycles',type=int,default=4);ap.add_argument('--output',default='measurements.csv');args=ap.parse_args()
    q=TAGS[0];p=pair(N(0),N(1)); rows=[]
    for n in range(args.cycles*6):
        old=decode_state(q)
        q,p=sample_step(q,p,n,rows)
        assert decode_state(q)==(old+1)%6
        if decode_state(q)==0:
            print(f"cycle {(n+1)//6}: Fibonacci pair=({rows[-1]['product_a']},{rows[-1]['product_b']})")
    path=Path(args.output); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    from collections import defaultdict
    groups=defaultdict(list)
    for r in rows:groups[r['from']].append(r)
    for phase in range(6):
        samples=groups[phase]
        print(f'Q{phase}: beta={[r["beta"] for r in samples]}, seconds={[r["seconds"] for r in samples]}')
    print('total_beta',sum(r['beta'] for r in rows),'peak_ru_maxrss_kib',max(r['ru_maxrss_kib'] for r in rows))
if __name__=='__main__':main()
