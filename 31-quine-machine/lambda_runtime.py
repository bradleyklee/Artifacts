"""Pure untyped lambda term construction and capture-avoiding normal-order β evaluator.
No host-language computation is permitted as a beta reduction.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class V: i:int
@dataclass(frozen=True)
class L: body:object
@dataclass(frozen=True)
class A: f:object; x:object

def app(f,*args):
    for x in args: f=A(f,x)
    return f

def lam(*names_body):
    *names,body=names_body
    for name in reversed(names): body=L(body)
    return body

def shift(t,d,c=0):
    if isinstance(t,V):
        if t.i>=c:
            assert t.i+d>=0
            return V(t.i+d)
        return t
    if isinstance(t,L): return L(shift(t.body,d,c+1))
    return A(shift(t.f,d,c),shift(t.x,d,c))

def subst(t,j,r,depth=0):
    if isinstance(t,V): return shift(r,depth) if t.i==j+depth else t
    if isinstance(t,L): return L(subst(t.body,j,r,depth+1))
    return A(subst(t.f,j,r,depth),subst(t.x,j,r,depth))

def contract(t):
    assert isinstance(t,A) and isinstance(t.f,L)
    return shift(subst(t.f.body,0,shift(t.x,1)),-1)

def redexes(t,path=()):
    if isinstance(t,A):
        if isinstance(t.f,L): yield path
        yield from redexes(t.f,path+('f',))
        yield from redexes(t.x,path+('x',))
    elif isinstance(t,L): yield from redexes(t.body,path+('b',))

def at(t,path):
    for p in path: t=getattr(t,{'f':'f','x':'x','b':'body'}[p])
    return t

def replace(t,path,r):
    if not path:return r
    p,*rest=path
    if isinstance(t,L):assert p=='b';return L(replace(t.body,rest,r))
    if p=='f':return A(replace(t.f,rest,r),t.x)
    assert p=='x';return A(t.f,replace(t.x,rest,r))

def beta(t,path=None):
    if path is None:
        path=next(iter(redexes(t)),None)
        if path is None:return None
    return replace(t,path,contract(at(t,path)))

def normalize(t,limit=30000,trace=None,tag=''):
    for i in range(limit):
        path=next(iter(redexes(t)),None)
        if path is None:return t,i
        u=beta(t,path)
        if trace is not None:trace.record(tag,path,t,u)
        t=u
    raise RuntimeError(f'beta budget exhausted for {tag}: {limit}')

def pretty(t,env=()):
    if isinstance(t,V):return env[t.i] if t.i<len(env) else f'free[{t.i-len(env)}]'
    if isinstance(t,L):
        name=f'v{len(env)}';return f'(λ{name}.{pretty(t.body,(name,)+env)})'
    return f'({pretty(t.f,env)} {pretty(t.x,env)})'

def prefix(t):
    if isinstance(t,V):return f'{t.i}'
    if isinstance(t,L):return 'L'+prefix(t.body)
    return 'A'+prefix(t.f)+prefix(t.x)

def abstract(names,expr):
    """Construct named lambda terms from ('app', f,x) and named strings, avoiding capture."""
    def rec(e,env):
        if isinstance(e,str):
            if e not in env:raise KeyError(e)
            return V(env.index(e))
        if isinstance(e,tuple) and e[0]=='app':return A(rec(e[1],env),rec(e[2],env))
        if isinstance(e,tuple) and e[0]=='lam':return L(rec(e[2],(e[1],)+env))
        raise TypeError(e)
    e=expr
    for name in reversed(names):e=('lam',name,e)
    return rec(e,())

def E(f,*xs):return ('app',E(f,*xs[:-1]) if len(xs)>1 else f,xs[-1]) if xs else f

def N(n):
    b=V(0)
    for _ in range(n):b=A(V(1),b)
    return L(L(b))

TRUE=abstract(['t','f'],'t')
FALSE=abstract(['t','f'],'f')
SUCC=abstract(['n','f','x'],E('f',E('n','f','x')))
ISZERO=L(app(V(0),L(FALSE),TRUE))
PAIR=abstract(['a','b','k'],E('k','a','b'))
FST=L(app(V(0),TRUE))
SND=L(app(V(0),FALSE))
Y=abstract(['f'],E(('lam','x',E('f',E('x','x'))),('lam','x',E('f',E('x','x')))))

# Church encodings used as public interface to product and state.
def pair(a,b):return app(PAIR,a,b)

def pair_first(t):return app(FST,t)
def pair_second(t):return app(SND,t)

def numeral_value(t,limit=20000):
    """Decode only after reducing a *closed* lambda term."""
    n, _=normalize(t,limit)
    assert isinstance(n,L) and isinstance(n.body,L)
    x=n.body.body;k=0
    while isinstance(x,A) and x.f==V(1):k+=1;x=x.x
    assert x==V(0),f'not a Church numeral: {pretty(n)[:200]}'
    return k

def boolean_value(t):
    n,_=normalize(t,20000)
    assert n in (TRUE,FALSE),f'not boolean {pretty(n)[:200]}'
    return n==TRUE

# Six step CPU from earlier construction.
DELTA=L(A(V(0),V(0)))
H=L(DELTA)
G=L(A(A(V(0),H),V(0)))
Q=A(DELTA,G)

def cpu_tick(t):
    p=next(iter(redexes(t)),None)
    assert p is not None
    return p,beta(t,p)

# State is Church 7-tuple: phase, published, candidate, checked,
# export_count, report_count, listen_count.
FIELDS=('phase','published','candidate','checked','exports','reports','listens')

def state_expr(values):
    return abstract([*FIELDS,'k'],E('k',*[values[x] for x in FIELDS]))

def transition(updates):
    vals={x:x for x in FIELDS}; vals.update(updates)
    # λs. s (λphase.λpublished ... . State(...))
    body=E('s',('lam',FIELDS[0],_nested_lam(FIELDS[1:],state_expr(vals))))
    return abstract(['s'],body)

def _nested_lam(names,body):
    for name in reversed(names):body=('lam',name,body)
    return body

def whole_state(phase=0,published=0,candidate=0,checked=False,exports=0,reports=0,listens=0):
    items=[N(phase),N(published),N(candidate),TRUE if checked else FALSE,N(exports),N(reports),N(listens)]
    return abstract(['k'],E('k',*[f'x{i}' for i in range(7)])) if False else _state_terms(items)

def _state_terms(items):
    # Build a closed Church 7-tuple directly.
    out=V(0)
    for item in items:out=A(out,shift(item,1))
    return L(out)

# Select a field from a Church-encoded seven-tuple.
def project(t,index):
    sel=abstract([f'x{i}' for i in range(7)],f'x{index}')
    return app(t,sel)

# Build transition terms using explicit nested destructuring.
def make_op(replace_field):
    e={x:x for x in FIELDS}
    e.update(replace_field)
    vals=[e[x] for x in FIELDS]
    mk=('lam','k',E('k',*vals))
    return abstract(['s'],E('s',_nested_lam(FIELDS,mk)))

# Construct operations with closed prelude terms by explicit AST substitution
# Here the named constant references are closed terms and inserted after abstraction.
def make_op_constants(updates,constants):
    def build(e):
        if isinstance(e,str):
            if e in constants:return ('CONST',e)
            return e
        if isinstance(e,tuple):return tuple([e[0],*[build(x) for x in e[1:]]])
        return e
    vals={x:x for x in FIELDS}; vals.update(updates)
    raw=E('s',_nested_lam(FIELDS,('lam','k',E('k',*[vals[x] for x in FIELDS]))))
    # Recursively compile with env and closed constants; unlike named expression
    # these constants can be placed freely under binders.
    def compile(e,env):
        if isinstance(e,str):
            if e in constants:return shift(constants[e],0)
            return V(env.index(e))
        if e[0]=='app':return A(compile(e[1],env),compile(e[2],env))
        if e[0]=='lam':return L(compile(e[2],(e[1],)+env))
        raise TypeError(e)
    return L(compile(raw,('s',)))

NOT=L(app(V(0),FALSE,TRUE))
AND=L(L(app(V(1),V(0),FALSE)))
ZERO=N(0)
OPS={
 'TICK':make_op_constants({'phase':E('SUCC','phase')},{'SUCC':SUCC}),
 'RESET':make_op_constants({'phase':'ZERO'},{'ZERO':ZERO}),
 'IMPROVE':make_op_constants({'candidate':E('SUCC','published'),'checked':'FALSE'}, {'SUCC':SUCC,'FALSE':FALSE}),
 'VERIFY':make_op_constants({'checked':E('AND',E('ISZERO','phase'),E('NOT',E('ISZERO','candidate')))}, {'AND':AND,'NOT':NOT,'ISZERO':ISZERO}),
 'EXPORT':None,
 'REPORT':make_op_constants({'reports':E('SUCC','reports')},{'SUCC':SUCC}),
 'LISTEN':make_op_constants({'listens':E('SUCC','listens')},{'SUCC':SUCC}),
}
# EXPORT only modifies state if verified; alternative stays unchanged.
export_ok=make_op_constants({'published':'candidate','exports':E('SUCC','exports'),'checked':'FALSE'}, {'SUCC':SUCC,'FALSE':FALSE})
OPS['EXPORT']=abstract(['s'],E(E('s',_nested_lam(FIELDS,'checked')),E('export_ok','s'),'s')) if False else None
# λs. ((s SELECT_CHECKED) (export_ok s) s)
select_checked=abstract(FIELDS,'checked')
OPS['EXPORT']=L(app(app(app(V(0),select_checked),app(shift(export_ok,1),V(0))),V(0)))

# Scott action list (not Church list): Nil = λempty.λcons.empty
# Cons a tail = λempty.λcons.cons a tail
NIL=abstract(['nil','cons'],'nil')
CONS=abstract(['h','t','nil','cons'],E('cons','h','t'))

def script(actions):
    out=NIL
    for op in reversed(actions):out=app(CONS,OPS[op],out)
    return out

# FIXED-POINT CONTROLLER:
# Φ = λself.λactions.λstate. actions state
#                          (λop.λrest. self rest (op state))
# CTRL = Y Φ; normal-order reduction expands only on demand.
PHI=abstract(['self','actions','state'],
    E('actions','state',('lam','op',('lam','rest',E('self','rest',E('op','state'))))))
CTRL=app(Y,PHI)

if __name__=='__main__':
    for k in ['TICK','RESET','IMPROVE','VERIFY','EXPORT','REPORT','LISTEN']:
        assert not any(isinstance(at(OPS[k],p),V) for p in ())
    print('lambda reducer module loaded')
