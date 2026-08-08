#!/usr/bin/env python3
"""Polynomial reduction and exact certificate search for z^2=P(x,alpha)."""
from __future__ import annotations
import itertools,time
import sympy as sp

x,z,alpha=sp.symbols("x z alpha")
_serial=itertools.count()


class HyperellipticPeriodReducer:
    def __init__(self,P):
        self.P=sp.expand(P);self.G=z**2-self.P
        self.K=sp.QQ.frac_field(alpha)
        self.Ppoly=sp.Poly(self.P,x,domain=self.K)

    @property
    def degree(self): return int(sp.degree(self.P,x))

    @property
    def genus(self): return (self.degree-1)//2

    @property
    def order_ceiling(self): return 2*self.genus

    def reduce(self,expr):
        num,den=sp.fraction(sp.cancel(expr))
        _,rem=sp.div(sp.Poly(sp.expand(num),z,domain=sp.EX),
                     sp.Poly(self.G,z,domain=sp.EX))
        return sp.cancel(rem.as_expr()/den)

    def Da(self,expr):
        za=sp.diff(self.P,alpha)/(2*z)
        return sp.cancel(sp.diff(expr,alpha)+za*sp.diff(expr,z))

    def Dx(self,expr):
        zx=sp.diff(self.P,x)/(2*z)
        return sp.cancel(sp.diff(expr,x)+zx*sp.diff(expr,z))

    def tower(self,order):
        out=[1/(4*z)]
        for _ in range(order):out.append(self.Da(out[-1]))
        return out

    def raw_tower_forms(self,order):
        """Return (pole_index,numerator) for D_alpha^k(1/(4z))."""
        forms=[(0,sp.Rational(1,4))]
        for _ in range(order):
            k,f=forms[-1]
            n=2*k+1
            forms.append((k+1,sp.cancel(sp.diff(f,alpha)*self.P-
                                        sp.Rational(n,2)*f*sp.diff(self.P,alpha))))
        return forms

    def reduce_form(self,k,f,track_primitive=True):
        """Hermite-reduce f dx/z^(2k+1); return basis vector and primitive."""
        fpoly=sp.Poly(f,x,domain=self.K);primitive=sp.S.Zero
        Pp=self.Ppoly.diff()
        inv=sp.invert(Pp,self.Ppoly)
        while k>0:
            A=(fpoly*inv).rem(self.Ppoly)
            B=(fpoly-A*Pp).exquo(self.Ppoly)
            n=2*k-1
            if track_primitive:
                primitive += -sp.Rational(2,n)*A.as_expr()/z**n
            fpoly=B+A.diff().mul_ground(self.K.convert(sp.Rational(2,n)))
            k-=1
        # Reduce polynomial degree modulo d(Q*z).
        degP=self.degree;lc=self.Ppoly.LC()
        while fpoly.degree()>degP-2:
            m=fpoly.degree();e=m-degP+1;lead=fpoly.LC()
            c=lead/(lc*self.K.convert(sp.Rational(2*e+degP,2)))
            Q=sp.Poly.from_dict({(e,):c},(x,),domain=self.K)
            L=Q.diff()*self.Ppoly+(Q*Pp).mul_ground(self.K.convert(sp.Rational(1,2)))
            fpoly=fpoly-L
            if track_primitive: primitive+=Q.as_expr()*z
        vec=[fpoly.coeff_monomial(x**j).as_expr() for j in range(degP-1)]
        return vec,primitive

    def cohomology_certificate(self,max_order=None):
        """Compatibility name for polynomial_reduction_certificate()."""
        if max_order is None:max_order=self.order_ceiling
        reduced=[];primitives=[]
        for k,f in self.raw_tower_forms(max_order):
            v,q=self.reduce_form(k,f);reduced.append(v);primitives.append(q)
        M=sp.Matrix.hstack(*(sp.Matrix(v) for v in reduced))
        null=M.nullspace()
        if not null:return {"status":"incomplete","matrix":M}
        c=null[0]
        # Normalize to primitive polynomial coefficients in alpha.
        denpoly=sp.Poly(1,alpha,domain=sp.QQ)
        for v in c:
            dv=sp.Poly(sp.denom(sp.together(v)),alpha,domain=sp.QQ)
            denpoly=denpoly.lcm(dv)
        den=denpoly.as_expr()
        coeff=[sp.factor(sp.cancel(v*den)) for v in c]
        polys=[sp.Poly(v,alpha,domain=sp.QQ) for v in coeff if v!=0]
        content=polys[0]
        for p0 in polys[1:]:content=content.gcd(p0)
        if content.degree()>0 or content.LC()!=1:
            coeff=[sp.factor(sp.cancel(v/content.as_expr())) for v in coeff]
        while len(coeff)>1 and coeff[-1]==0:
            coeff.pop()
            primitives.pop()
            reduced.pop()
        Xi=sp.factor(sum(a*q for a,q in zip(coeff,primitives)))
        residual=self.reduce(sum(a*w for a,w in zip(coeff,self.tower(len(coeff)-1)))-
                             self.Dx(Xi))
        if residual!=0:raise AssertionError("cohomology certificate replay failed")
        # Clear the remaining numeric denominators as one scalar operation.
        # Scaling Xi by the same number preserves the exact certificate.
        numeric_lcm=1
        for a in coeff:
            for q in sp.Poly(a,alpha,domain=sp.QQ).all_coeffs():
                numeric_lcm=sp.ilcm(numeric_lcm,int(sp.denom(q)))
        integer_coeff=[sp.expand(numeric_lcm*a) for a in coeff]
        integer_content=0
        for a in integer_coeff:
            for q in sp.Poly(a,alpha,domain=sp.ZZ).all_coeffs():
                integer_content=sp.igcd(integer_content,abs(int(q)))
        multiplier=sp.Rational(numeric_lcm,integer_content or 1)
        coeff=[sp.factor(multiplier*a) for a in coeff]
        Xi=sp.factor(multiplier*Xi)
        return {"status":"closed","order":len(coeff)-1,"matrix":M,
                "operator":coeff,"primitive":Xi,"exact_residual":residual,
                "reduced_vectors":reduced,
                "normalization_multiplier":multiplier}

    def polynomial_reduction_certificate(self,max_order=None):
        """Differentiate, reduce polynomials, find a null relation, rebuild Xi."""
        return self.cohomology_certificate(max_order=max_order)

    def two_pass_polynomial_certificate(self,max_order=None):
        """Find the relation without primitives, then rebuild only its combination."""
        if max_order is None:max_order=self.order_ceiling
        forms=self.raw_tower_forms(max_order)
        reduced=[self.reduce_form(k,f,track_primitive=False)[0] for k,f in forms]
        M=sp.Matrix.hstack(*(sp.Matrix(v) for v in reduced))
        null=M.nullspace()
        if not null:return {"status":"incomplete","matrix":M,"reduced_vectors":reduced}
        c=list(null[0])
        while len(c)>1 and c[-1]==0:c.pop()
        denpoly=sp.Poly(1,alpha,domain=sp.QQ)
        for v in c:
            denpoly=denpoly.lcm(sp.Poly(sp.denom(sp.together(v)),alpha,domain=sp.QQ))
        coeff=[sp.factor(sp.cancel(v*denpoly.as_expr())) for v in c]
        polys=[sp.Poly(v,alpha,domain=sp.QQ) for v in coeff if v!=0]
        gcdpoly=polys[0]
        for p0 in polys[1:]:gcdpoly=gcdpoly.gcd(p0)
        coeff=[sp.factor(sp.cancel(v/gcdpoly.as_expr())) for v in coeff]
        numeric_lcm=1
        for a in coeff:
            for q in sp.Poly(a,alpha,domain=sp.QQ).all_coeffs():
                numeric_lcm=sp.ilcm(numeric_lcm,int(sp.denom(q)))
        ints=[sp.expand(numeric_lcm*a) for a in coeff];content=0
        for a in ints:
            for q in sp.Poly(a,alpha,domain=sp.ZZ).all_coeffs():
                content=sp.igcd(content,abs(int(q)))
        scale=sp.Rational(numeric_lcm,content or 1)
        coeff=[sp.factor(scale*a) for a in coeff]
        K=len(coeff)-1
        combined=sp.cancel(sum(coeff[j]*forms[j][1]*self.P**(K-forms[j][0])
                               for j in range(K+1)))
        vec,Xi=self.reduce_form(K,combined,track_primitive=True)
        if any(sp.cancel(v)!=0 for v in vec):
            raise AssertionError("two-pass relation did not reduce to zero")
        residual=self.reduce(sum(a*w for a,w in zip(coeff,self.tower(K)))-self.Dx(Xi))
        if residual!=0:raise AssertionError("two-pass certificate replay failed")
        return {"status":"closed","order":K,"matrix":M,"operator":coeff,
                "primitive":sp.factor(Xi),"exact_residual":residual,
                "reduced_vectors":reduced}

    def bounded_matrix(self,order,operator_alpha_degree,
                       primitive_x_degree,primitive_alpha_degree):
        serial=next(_serial);width=operator_alpha_degree+1
        au=sp.symbols(f"hyper_{serial}_op__0:{(order+1)*width}")
        op=[sum(au[width*k+j]*alpha**j for j in range(width))
            for k in range(order+1)]
        basis=[alpha**a*x**j for a in range(primitive_alpha_degree+1)
               for j in range(primitive_x_degree+1)]
        pu=sp.symbols(f"hyper_{serial}_prim__0:{len(basis)}")
        Q=sum(c*m for c,m in zip(pu,basis))
        Xi=Q/z**(2*order-1)
        residual=sum(a*w for a,w in zip(op,self.tower(order)))-self.Dx(Xi)
        num=sp.together(self.reduce(residual)).as_numer_denom()[0]
        eq=sp.Poly(sp.expand(num),z,x,alpha).coeffs();U=list(au)+list(pu)
        M,_=sp.linear_eq_to_matrix(eq,U)
        return M,U,Xi

    def search(self,order,operator_alpha_degree,primitive_alpha_degree,
               max_x_degree,time_limit=None):
        history=[];started=time.monotonic();width=operator_alpha_degree+1
        for xd in range(max_x_degree+1):
            if time_limit is not None and time.monotonic()-started>time_limit:
                return {"status":"blocked","blocker":"time_limit",
                        "next_x_degree":xd,"history":history}
            tick=time.monotonic();M,U,Xi=self.bounded_matrix(
                order,operator_alpha_degree,xd,primitive_alpha_degree)
            rel=[q for q in M.nullspace()
                 if any(q[i] for i in range((order+1)*width))]
            history.append({"x_degree":xd,"matrix_shape":list(M.shape),
                "rank":M.rank(),"nullity":len(M.nullspace()),
                "operator_relations":len(rel),"seconds":time.monotonic()-tick})
            if rel:
                q=rel[0];sub=dict(zip(U,list(q)))
                op=[sp.factor(sum(q[width*k+j]*alpha**j for j in range(width)))
                    for k in range(order+1)]
                Xi0=sp.factor(Xi.subs(sub))
                residual=self.reduce(sum(a*w for a,w in zip(
                    op,self.tower(order)))-self.Dx(Xi0))
                if residual!=0:raise AssertionError("hyperelliptic certificate failed")
                return {"status":"closed","x_degree":xd,"history":history,
                        "operator":op,"primitive":Xi0,"exact_residual":residual}
        return {"status":"blocked","blocker":"max_x_degree",
                "next_x_degree":max_x_degree+1,"history":history}


def from_linear_in_t(Fut,u_symbol,t_symbol):
    poly=sp.Poly(sp.expand(Fut),t_symbol)
    if poly.degree()!=1: raise ValueError("F must be linear in invariant t")
    B=poly.coeff_monomial(t_symbol);A=poly.coeff_monomial(1)
    N=-A
    P=sp.expand(u_symbol*N*(B-4*N))
    return HyperellipticPeriodReducer(P.subs(u_symbol,x)),sp.factor(N),sp.factor(B)


def even_power_substitution(P):
    """For even P(x), return Q(u)=u*P(sqrt(u)); dx/sqrt(P)=du/(2sqrt(Q))."""
    poly=sp.Poly(sp.expand(P),x,domain=sp.EX)
    if any(m[0]%2 for m,c in poly.terms() if c):
        raise ValueError("P contains an odd power of x")
    Pu=sum(c*x**(m[0]//2) for m,c in poly.terms())
    return sp.expand(x*Pu)


def self_check():
    P=x*(alpha-10*x**2+11*x-6)*(
        (x-1)**2-4*(alpha-10*x**2+11*x-6))
    r=HyperellipticPeriodReducer(P)
    assert r.degree==5 and r.genus==2 and r.order_ceiling==4
    assert r.reduce(r.Da(r.G))==0 and r.reduce(r.Dx(r.G))==0
    print("HYPERELLIPTIC_PERIOD_REDUCER_PASS",r.degree,r.genus)


if __name__=="__main__":self_check()
