#!/usr/bin/env python3
"""General v->1-v invariant chart for even sphere curves."""
from __future__ import annotations
import itertools,time
import sympy as sp

u,v,t,w,alpha=sp.symbols("u v t w alpha")
_serial=itertools.count()


def reflection_to_t(Fuv):
    rem=sp.rem(sp.Poly(sp.expand(Fuv),v,domain=sp.EX),
               sp.Poly(v**2-v+t,v,domain=sp.EX)).as_expr()
    if sp.diff(rem,v)!=0:
        raise ValueError("input is not invariant under v -> 1-v")
    return sp.expand(rem)


class ReflectionInvariantReducer:
    def __init__(self,Fut):
        self.F=sp.expand(Fut)
        self.G=w**2-u*t*(1-4*t)
        self.Fu=sp.diff(self.F,u); self.Ft=sp.diff(self.F,t)
        if self.Fu==0: raise ValueError("singular u chart")

    def reduce(self,expr):
        num,den=sp.fraction(sp.cancel(expr))
        gens=[sp.Poly(self.G,w,u,domain=sp.EX),
              sp.Poly(self.F,w,u,domain=sp.EX)]
        _,rem=sp.reduced(sp.Poly(sp.expand(num),w,u,domain=sp.EX),
                         gens,w,u,domain=sp.EX)
        return sp.cancel(rem.as_expr()/den)

    def Da(self,expr):
        ua=1/self.Fu; wa=t*(1-4*t)/(2*w*self.Fu)
        return sp.cancel(sp.diff(expr,alpha)+ua*sp.diff(expr,u)+wa*sp.diff(expr,w))

    def Dt(self,expr):
        ut=-self.Ft/self.Fu
        wt=(ut*t*(1-4*t)+u*(1-8*t))/(2*w)
        return sp.cancel(sp.diff(expr,t)+ut*sp.diff(expr,u)+wt*sp.diff(expr,w))

    def tower(self,order):
        out=[-1/(4*w*self.Fu)]
        for _ in range(order): out.append(self.Da(out[-1]))
        return out

    def bounded_matrix(self,order,operator_alpha_degree,max_t,
                       primitive_alpha_degree):
        max_u=int(sp.degree(self.F,u))-1; serial=next(_serial)
        width=operator_alpha_degree+1
        au=sp.symbols(f"reflection_{serial}_op__0:{(order+1)*width}")
        op=[sum(au[width*k+j]*alpha**j for j in range(width))
            for k in range(order+1)]
        basis=[alpha**a*u**i*t**j for a in range(primitive_alpha_degree+1)
               for i in range(max_u+1) for j in range(max_t+1)]
        pu=sp.symbols(f"reflection_{serial}_prim__0:{len(basis)}")
        P=sum(c*z for c,z in zip(pu,basis))
        Xi=P/(w**(2*order-1)*self.Fu**(2*order-1))
        residual=sum(a*z for a,z in zip(op,self.tower(order)))-self.Dt(Xi)
        num=sp.together(self.reduce(residual)).as_numer_denom()[0]
        eq=sp.Poly(sp.expand(num),w,u,t,alpha).coeffs()
        U=list(au)+list(pu); M,_=sp.linear_eq_to_matrix(eq,U)
        return M,U,Xi

    def search(self,order,operator_alpha_degree,primitive_alpha_degree,
               start_t=0,max_t=None,time_limit=None):
        history=[]; started=time.monotonic(); degree=start_t
        while True:
            if max_t is not None and degree>max_t:
                return {"status":"blocked","blocker":"max_t","next_t":degree,
                        "history":history}
            if time_limit is not None and time.monotonic()-started>time_limit:
                return {"status":"blocked","blocker":"time_limit","next_t":degree,
                        "history":history}
            tick=time.monotonic();M,U,Xi=self.bounded_matrix(
                order,operator_alpha_degree,degree,primitive_alpha_degree)
            width=operator_alpha_degree+1
            rel=[z for z in M.nullspace()
                 if any(z[i] for i in range((order+1)*width))]
            history.append({"t_degree":degree,"matrix_shape":list(M.shape),
                "rank":M.rank(),"nullity":len(M.nullspace()),
                "operator_relations":len(rel),"seconds":time.monotonic()-tick})
            if rel:
                z=rel[0];sub=dict(zip(U,list(z)))
                op=[sp.factor(sum(z[width*k+j]*alpha**j for j in range(width)))
                    for k in range(order+1)]
                Xi0=sp.factor(Xi.subs(sub))
                residual=self.reduce(sum(a*x for a,x in zip(op,self.tower(order)))-
                                     self.Dt(Xi0))
                if residual!=0: raise AssertionError("reflection certificate failed")
                return {"status":"closed","t_degree":degree,"history":history,
                        "operator":op,"primitive":Xi0,"exact_residual":residual}
            degree+=1

    def verify_derivations(self):
        assert self.reduce(self.Da(self.F))==0
        assert self.reduce(self.Da(self.G))==0
        assert self.reduce(self.Dt(self.F))==0
        assert self.reduce(self.Dt(self.G))==0


def self_check():
    Foct=4*(1-t)*u**2+4*(2*t-1)*u+2-4*t-alpha
    r=ReflectionInvariantReducer(Foct);r.verify_derivations()
    print("REFLECTION_INVARIANT_REDUCER_PASS")


if __name__=="__main__": self_check()
