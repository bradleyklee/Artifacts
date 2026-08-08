#!/usr/bin/env python3
from __future__ import annotations
import sympy as sp
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple

p,q,z,alpha=sp.symbols('p q z alpha')


def total_multiplicity(f, x, y):
    P=sp.Poly(sp.expand(f),x,y, extension=True)
    if P.is_zero:
        raise ValueError('zero local equation')
    return min(sum(mon) for mon, coeff in P.terms() if coeff!=0)


def homogeneous_piece(f,x,y,deg):
    P=sp.Poly(sp.expand(f),x,y, extension=True)
    out=0
    for mon,c in P.terms():
        if sum(mon)==deg:
            out += c*x**mon[0]*y**mon[1]
    return sp.expand(out)


def _distinct_roots(poly, var):
    poly=sp.Poly(poly,var,extension=True)
    if poly.degree()<=0:
        return []
    sq=sp.Poly(sp.sqf_part(poly.as_expr()),var,extension=True)
    roots=sp.roots(sq.as_expr(),var)
    if sum(roots.values())==sq.degree():
        return list(roots.keys())
    return list(sp.polys.polytools.all_roots(sq))


def delta_by_blowup(f, x, y, depth=0, trace=None, max_depth=12):
    """Delta invariant of a reduced isolated plane singularity at (0,0).

    Uses delta = sum_Q binomial(m_Q,2) over proper and infinitely-near
    singular points in an embedded resolution. Exact for the low-degree
    singularities occurring in the quartic tests here.
    """
    if trace is None: trace=[]
    f=sp.cancel(sp.expand(f))
    m=total_multiplicity(f,x,y)
    T0=homogeneous_piece(f,x,y,m)
    trace.append({'depth':depth,'multiplicity':int(m),'tangent_cone':str(sp.factor(T0)),'equation':str(f)})
    if m<=1:
        return 0,trace
    if depth>=max_depth:
        raise RuntimeError('blowup depth exceeded')
    delta=m*(m-1)//2
    T=T0

    # finite tangent directions [1:v], y=v*x
    v,w=sp.symbols(f'v{depth} w{depth}')
    tv=sp.expand(T.subs({x:1,y:v}))
    finite_roots=_distinct_roots(tv,v) if tv!=0 else []
    for r in finite_roots:
        transformed=sp.expand(f.subs({y:x*(r+w)}))/x**m
        transformed=sp.cancel(transformed)
        # exact divisibility should hold
        transformed=sp.expand(transformed)
        mm=total_multiplicity(transformed,x,w)
        if mm>1:
            subtrace=[]
            d,subtrace=delta_by_blowup(transformed,x,w,depth+1,subtrace,max_depth)
            delta+=d
            trace.append({'tangent':str(r),'chart':'y=xv','subtrace':subtrace})

    # vertical tangent [0:1], covered by x=u*y; occurs iff T(0,1)=0
    if sp.simplify(T.subs({x:0,y:1}))==0:
        u=sp.symbols(f'u{depth}')
        transformed=sp.expand(f.subs({x:y*u}))/y**m
        transformed=sp.cancel(transformed)
        transformed=sp.expand(transformed)
        mm=total_multiplicity(transformed,y,u)
        if mm>1:
            subtrace=[]
            d,subtrace=delta_by_blowup(transformed,y,u,depth+1,subtrace,max_depth)
            delta+=d
            trace.append({'tangent':'vertical','chart':'x=yu','subtrace':subtrace})
    return int(delta),trace


def homogenize_level(H):
    P=sp.Poly(sp.expand(H-alpha),p,q)
    d=max(sum(mon) for mon,c in P.terms())
    F=0
    for mon,c in P.terms():
        i,j=mon
        F += c*p**i*q**j*z**(d-i-j)
    return sp.expand(F),d


def singularities_at_infinity(F):
    """Return exact singular points [1:r:0] and possibly [0:1:0]."""
    out=[]
    # chart p=1: coordinate r=q/p
    r=sp.symbols('r')
    f=sp.expand(F.subs({p:1,q:r}))
    A=sp.expand(f.subs(z,0))
    B=sp.expand(sp.diff(f,z).subs(z,0))
    g=sp.gcd(sp.Poly(A,r,extension=True),sp.Poly(sp.diff(A,r),r,extension=True))
    g=sp.gcd(g,sp.Poly(B,r,extension=True))
    for rr in _distinct_roots(g.as_expr(),r):
        out.append(('pchart',rr))
    # point [0:1:0]
    vals=[F,sp.diff(F,p),sp.diff(F,q),sp.diff(F,z)]
    if all(sp.simplify(v.subs({p:0,q:1,z:0}))==0 for v in vals):
        out.append(('qchart',sp.Integer(0)))
    return out


def classify_generic_quartic(H):
    F,d=homogenize_level(H)
    if d!=4:
        raise ValueError(f'expected quartic degree, got {d}')
    sing=singularities_at_infinity(F)
    details=[]
    delta_total=0
    u,v=sp.symbols('u v')
    for chart,r in sing:
        if chart=='pchart':
            local=sp.expand(F.subs({p:1,q:r+u,z:v}))
        else:
            local=sp.expand(F.subs({q:1,p:u,z:v}))
        delta,trace=delta_by_blowup(local,u,v)
        delta_total+=delta
        details.append({'point':f'[1:{r}:0]' if chart=='pchart' else '[0:1:0]',
                        'delta':delta,'trace':trace})
    genus=3-delta_total
    if genus==1:
        verdict='geometrically_genus_one_base_point_required'
    elif genus!=1:
        verdict='no_binary_elliptic_addition_on_original_curve'
    else:
        verdict='unknown'
    return {
        'H':str(H), 'F_homogeneous':str(F), 'degree':d,
        'singularities_at_infinity':details,
        'delta_total':delta_total,'geometric_genus':genus,
        'verdict':verdict,
        'note':'generic alpha: affine critical fibers excluded because alpha is transcendental'
    }


def derive_edwards_from_ansatz():
    """Derive, rather than insert, the Edwards law from a six-parameter ansatz."""
    x1,y1,x2,y2,d=sp.symbols('x1 y1 x2 y2 d')
    A,B,C,D,E,G=sp.symbols('A B C D E G')
    X=(A*x1*y2+B*y1*x2)/(1+C*x1*x2*y1*y2)
    Y=(D*y1*y2+E*x1*x2)/(1+G*x1*x2*y1*y2)
    # identity (0,1) forces A=B=D=1
    X=sp.simplify(X.subs({A:1,B:1,D:1}))
    Y=sp.simplify(Y.subs(D,1))
    # solve by evaluating exact closure/differential residuals at enough rational samples
    # on curve x^2+y^2=1+d*x^2*y^2. We derive symbolic equations by reducing y_i^2.
    rel1=1-x1**2-y1**2+d*x1**2*y1**2
    rel2=1-x2**2-y2**2+d*x2**2*y2**2

    def reduce_even(expr):
        num=sp.together(expr).as_numer_denom()[0]
        # Groebner reduce polynomial numerator by the two curve equations
        Gbasis=sp.groebner([rel1,rel2],y1,y2,x1,x2,order='lex')
        return sp.expand(Gbasis.reduce(sp.expand(num))[1])

    curve=sp.together(X**2+Y**2-1-d*X**2*Y**2)
    # invariant differential dx/[y(1-d x^2)] (constant factor ignored)
    # Pullback coefficient in dx1 and dx2 after restricting dy via tangent equation.
    # dy/dx = -x(1-d*y^2)/(y*(1-d*x^2))
    dy1dx=-x1*(1-d*y1**2)/(y1*(1-d*x1**2))
    dy2dx=-x2*(1-d*y2**2)/(y2*(1-d*x2**2))
    dX1=sp.diff(X,x1)+sp.diff(X,y1)*dy1dx
    dX2=sp.diff(X,x2)+sp.diff(X,y2)*dy2dx
    diff1=sp.together(dX1/(Y*(1-d*X**2))-1/(y1*(1-d*x1**2)))
    diff2=sp.together(dX2/(Y*(1-d*X**2))-1/(y2*(1-d*x2**2)))

    # Instead of giant symbolic solve, substitute a collection of exact points generated
    # from rational parametrizations at several d values, yielding polynomial equations.
    eqs=[]
    # Rational points on Edwards curve from line through (0,1): y=1+t*x.
    def point_from_t(dv,tv):
        xx=sp.symbols('xx')
        yy=1+tv*xx
        pol=sp.factor(xx**2+yy**2-1-dv*xx**2*yy**2)
        quot=sp.cancel(pol/xx)
        roots=sp.solve(sp.Eq(quot,0),xx)
        for xr in roots:
            if xr!=0 and xr.is_rational:
                return sp.Rational(xr),sp.simplify(1+tv*xr)
        return None
    samples=[]
    for dv in [sp.Rational(-1),sp.Rational(2),sp.Rational(3)]:
        pts=[]
        for tv in [sp.Rational(i) for i in range(-4,5) if i!=0]:
            pt=point_from_t(dv,tv)
            if pt and pt not in pts: pts.append(pt)
        for i in range(min(3,len(pts))):
            for j in range(i+1,min(4,len(pts))):
                samples.append((dv,*pts[i],*pts[j]))
    for dv,xa,ya,xb,yb in samples:
        sub={d:dv,x1:xa,y1:ya,x2:xb,y2:yb}
        for expr in [curve,diff1,diff2]:
            n=sp.factor(sp.together(expr.subs(sub)).as_numer_denom()[0])
            eqs.append(n)
    sol=sp.solve(eqs,[C,E,G],dict=True)
    return {'solutions':[ {str(k):str(v) for k,v in s.items()} for s in sol],
            'sample_count':len(samples),
            'derived_law': None if not sol else {
                'X':str(sp.factor(X.subs(sol[0]))),
                'Y':str(sp.factor(Y.subs(sol[0])))
            }}


def main():
    examples={
        'generic_maximal_quartic': p**2+q**2+p**3-2*p**2*q+3*p*q**2-q**3 + p**4+2*p**3*q+3*p**2*q**2+5*p*q**3+7*q**4,
        'generic_even_quartic_original_curve': p**2+q**2+p**4+2*p**3*q+3*p**2*q**2+5*p*q**3+7*q**4,
        'edwards_two_node_quartic': p**2+q**2-p**2*q**2,
        'mechanical_tacnode_quartic': p**2+q**2+q**4,
        'cubic_terms_destroy_edwards_nodes': p**2+q**2-p**2*q**2+p**3+q**3,
    }
    import json
    report={'classifications':{}}
    for name,H in examples.items():
        try: report['classifications'][name]=classify_generic_quartic(H)
        except Exception as exc: report['classifications'][name]={'error':repr(exc)}
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
