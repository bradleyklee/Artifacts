from pathlib import Path
import sys,json,csv
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lambda_runtime import V,L,A,app,abstract,E,N,TRUE,FALSE,normalize,boolean_value,Q,redexes,beta,prefix,pretty

# Scott unary naturals: zero=λz.λs.z, succ(n)=λz.λs.s n
Z=abstract(['z','s'],'z')
S=abstract(['n','z','s'],E('s','n'))
def sn(n):
 t=Z
 for i in range(n):t=app(S,t)
 return t
# Scott list of three symbols A,L,0; nil=λnil.λcons.nil;
# cons=λh.λt.λnil.λcons.cons h t
NIL=abstract(['nil','cons'],'nil')
CONS=abstract(['h','t','nil','cons'],E('cons','h','t'))
# Symbol equality via 3-way Scott tags; compared directly by an encoded equality table
SYM=[abstract(['a','l','v'],x) for x in ('a','l','v')]
# EQSYM x y = x (y T F F) (y F T F) (y F F T)
EQSYM=app(abstract(['TRUE','FALSE','x','y'],E('x',E('y','TRUE','FALSE','FALSE'),E('y','FALSE','TRUE','FALSE'),E('y','FALSE','FALSE','TRUE'))),TRUE,FALSE)
AND=app(abstract(['FALSE','x','y'],E('x','y','FALSE')),FALSE)
# Turing Y: strict-in-evaluation body uses Scott destructor; normal-order needed
Y=abstract(['f'],E(('lam','x',E('f',E('x','x'))),('lam','x',E('f',E('x','x')))))
# recursive equality of Scott lists: if first nil then second nil?; if cons, second must cons and check h,t
# EQ xs ys = xs (ys TRUE (λh.λt.FALSE))
#               (λh.λt.ys FALSE (λh2.λt2.AND(EQSYM h h2)(rec t t2)))
nil_case = E('ys', 'TRUE', ('lam','h',('lam','t','FALSE')))
cons_case = ('lam','h',('lam','t',
    E('ys', 'FALSE', ('lam','h2',('lam','t2',
        E('AND',E('EQSYM','h','h2'),E('rec','t','t2')))))))
EQBODY=app(abstract(['TRUE','FALSE','AND','EQSYM','rec','xs','ys'],E('xs',nil_case,cons_case)),TRUE,FALSE,AND,EQSYM)
EQLIST=app(Y,EQBODY)
# quote full prefix grammar. original clock states: stable syntactic data, no hashing.
q=[Q]
for _ in range(6):q.append(beta(q[-1],next(iter(redexes(q[-1])))))
assert q[6]==q[0] and len(set(q[:6]))==6
codes=[prefix(t) for t in q[:6]]
assert all(set(s)<={'A','L','0'} for s in codes)

def quote(s):
 t=NIL
 for c in reversed(s):t=app(CONS,SYM['AL0'.index(c)],t)
 return t
QUOTES=[quote(s) for s in codes]
# SAME input takes a syntax quotation and a Scott distance, comparing both to canonical states.
# Unique canonical distances = 0,5,4,3,2,1. Compare distance by Scott unary matching
# use EQ of Scott unary via Y recursion, similar destructor.
EQNBODY=app(abstract(['TRUE','FALSE','rec','x','y'],E('x',E('y','TRUE',('lam','p','FALSE')),('lam','p',E('y','FALSE',('lam','r',E('rec','p','r')))))),TRUE,FALSE)
EQN=app(Y,EQNBODY)
# A single term SAME = λsyntax.λdist. OR over six (EQLIST syntax quote_i && EQN dist expected_i)
OR=app(abstract(['TRUE','a','b'],E('a','TRUE','b')),TRUE)
# Compose body with terms via de Bruijn abstract expression builder using E tuples; embed exact quoted terms using closed-term placeholders.
# Avoid massive body: make a curried lambda that accepts a *canonical table* as six quote arguments.
# each branch is a lambda expression; table quotes passed once for all tests.
# Alternative direct compile using dataclass terms and index shifting.
from lambda_runtime import shift
# body reference input syntax V(1) distance V(0)
acc=FALSE
remaining=[0,5,4,3,2,1]
for i in reversed(range(6)):
 match=app(AND,app(EQLIST,V(1),shift(QUOTES[i],2)),app(EQN,V(0),shift(sn(remaining[i]),2)))
 acc=app(OR,match,shift(acc,0))
SAME=L(L(acc))

rows=[]
for i in range(6):
 for d in range(6):
  expr=app(SAME,QUOTES[i],sn(d))
  out,steps=normalize(expr,limit=100000)
  expected=d==remaining[i]
  assert out in (TRUE,FALSE),(i,d,pretty(out)[:100])
  actual=out==TRUE
  assert actual==expected,(i,d,actual,expected)
  rows.append(dict(state=f'Q{i}',distance=d,expected=expected,result=actual,beta_steps=steps))
  print('Q%d d=%d %s beta=%d'%(i,d,'T' if actual else 'F',steps),flush=True)
root=Path(__file__).resolve().parent
with (root/'same_v13_results.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
(root/'same_v13_states.json').write_text(json.dumps([dict(state=f'Q{i}',remaining=remaining[i],prefix=codes[i]) for i in range(6)],indent=2)+'\n')
print('PASS 36/36; range',min(x['beta_steps'] for x in rows),max(x['beta_steps'] for x in rows))
