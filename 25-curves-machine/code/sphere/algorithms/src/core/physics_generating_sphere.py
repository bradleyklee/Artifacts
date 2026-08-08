#!/usr/bin/env python3
"""Fixed-J physical generating-function models on the angular-momentum sphere.

The G operator is from Tyuterev, J. Mol. Spectrosc. 151 (1992), 97-129,
Eqs. (35)-(38).  Only even powers of angular-momentum components are used.
"""
from __future__ import annotations

from dataclasses import dataclass
import sympy as sp

p,s,energy=sp.symbols("p s energy")       # p=Jz is canonical to phi
L2,kappa,b,epsilon,eta=sp.symbols(
    "L2 kappa b epsilon eta", nonzero=True)


def square_root_relation():
    return s**2-1-kappa*p**2


def G_operator():
    return sp.cancel(2*(s-1)/kappa)


def G_taylor(z: sp.Expr, order: int=5):
    """Taylor polynomial in z=Jz^2, including powers z^1,...,z^order."""
    return sp.expand(sp.series(2*(sp.sqrt(1+kappa*z)-1)/kappa,
                               z,0,order+1).removeO())


def total_Dp(expr):
    """Derivative along s^2=1+kappa*p^2."""
    return sp.cancel(sp.diff(expr,p)+(kappa*p/s)*sp.diff(expr,s))


def reduce_s(expr):
    """Canonical rational representative with numerator degree <2 in s."""
    num,den=sp.fraction(sp.cancel(expr))
    _,rem=sp.div(sp.Poly(sp.expand(num),s,domain=sp.EX),
                 sp.Poly(square_root_relation(),s,domain=sp.EX))
    return sp.cancel(rem.as_expr()/den)


@dataclass(frozen=True)
class PhysicalPrismModel:
    """G-flattened top plus an even m-fold transverse prism harmonic."""
    m: int
    L2_value: sp.Expr=L2
    kappa_value: sp.Expr=kappa
    b_value: sp.Expr=b
    epsilon_value: sp.Expr=epsilon
    eta_value: sp.Expr=eta
    axial_polynomial: sp.Expr=sp.S.Zero

    def __post_init__(self):
        if self.m < 2 or self.m % 2:
            raise ValueError("even physical branch requires an even m >= 2")
        object.__setattr__(self,"L2_value",sp.sympify(self.L2_value))
        object.__setattr__(self,"kappa_value",sp.sympify(self.kappa_value))
        object.__setattr__(self,"b_value",sp.sympify(self.b_value))
        object.__setattr__(self,"epsilon_value",sp.sympify(self.epsilon_value))
        object.__setattr__(self,"eta_value",sp.sympify(self.eta_value))
        object.__setattr__(self,"axial_polynomial",sp.sympify(self.axial_polynomial))

    @property
    def relation(self):
        return s**2-1-self.kappa_value*p**2

    def Dp(self,expr):
        return sp.cancel(sp.diff(expr,p)+
                         (self.kappa_value*p/s)*sp.diff(expr,s))

    def reduce(self,expr):
        num,den=sp.fraction(sp.cancel(expr))
        _,rem=sp.div(sp.Poly(sp.expand(num),s,domain=sp.EX),
                     sp.Poly(self.relation,s,domain=sp.EX))
        return sp.cancel(rem.as_expr()/den)

    @property
    def h1(self):
        return sp.cancel(self.epsilon_value+
            self.axial_polynomial+
            self.b_value*G_operator().subs(kappa,self.kappa_value))

    @property
    def h2(self):
        return sp.expand(self.eta_value*(self.L2_value-p**2)**(self.m//2))

    @property
    def rho(self):
        return self.reduce(self.h2*self.Dp(self.h1)+
                           (energy-self.h1)*self.Dp(self.h2))

    @property
    def p_dot_squared(self):
        return self.reduce(-self.m**2*(energy-self.h1-self.h2)*
                           (energy-self.h1+self.h2))

    @property
    def p_ddot(self):
        return self.reduce(self.Dp(self.p_dot_squared)/2)

    def Denergy(self,expr):
        return self.reduce(sp.diff(expr,energy)+
                           (self.h2/self.rho)*self.Dp(expr))

    def density_tower(self,order):
        f=self.reduce(self.h2/self.rho); out=[f]
        for _ in range(order): out.append(self.Denergy(out[-1]))
        return [self.reduce((self.rho/self.h2)*x) for x in out]

    def time_derivative_over_pdot(self,R):
        """d_t(p_dot*R)/p_dot = p_ddot*R+p_dot^2*D_p(R)."""
        return self.reduce(self.p_ddot*R+self.p_dot_squared*self.Dp(R))

    def bounded_certificate_matrix(self,order,operator_energy_degree,
                                   numerator_p_degree,
                                   numerator_energy_degree):
        """Exact algebraic Dihedral search over Q(p,s,energy), s-degree <2."""
        tower=self.density_tower(order)
        width=operator_energy_degree+1
        au=sp.symbols(f"physics_operator__0:{(order+1)*width}")
        op=[sum(au[width*k+j]*energy**j for j in range(width))
            for k in range(order+1)]
        basis=[energy**a*p**j*s**e
               for a in range(numerator_energy_degree+1)
               for e in range(2) for j in range(numerator_p_degree+1)]
        pu=sp.symbols(f"physics_primitive__0:{len(basis)}")
        P=sum(c*z for c,z in zip(pu,basis))
        R=P/self.rho**(2*order-1)
        residual=self.reduce(sum(a*x for a,x in zip(op,tower))-
                             self.time_derivative_over_pdot(R))
        num=sp.together(residual).as_numer_denom()[0]
        equations=sp.Poly(sp.expand(num),p,s,energy).coeffs()
        unknowns=list(au)+list(pu)
        M,_=sp.linear_eq_to_matrix(equations,unknowns)
        return M,unknowns,R

    def derive_certificate(self,order,operator_energy_degree,
                           numerator_p_degree,numerator_energy_degree):
        M,U,R=self.bounded_certificate_matrix(order,operator_energy_degree,
            numerator_p_degree,numerator_energy_degree)
        width=operator_energy_degree+1
        rel=[z for z in M.nullspace()
             if any(z[i] for i in range((order+1)*width))]
        if not rel:
            return {"status":"incomplete","matrix":M}
        z=rel[0]; sub=dict(zip(U,list(z)))
        op=[sp.factor(sum(z[width*k+j]*energy**j for j in range(width)))
            for k in range(order+1)]
        R0=sp.factor(R.subs(sub))
        residual=self.reduce(sum(a*x for a,x in zip(op,self.density_tower(order)))-
                             self.time_derivative_over_pdot(R0))
        if residual != 0:
            raise AssertionError("physics generating-function certificate failed")
        return {"status":"closed","matrix":M,"operator":op,"R":R0,
                "exact_residual":residual}

    def turning_resultant(self):
        """Eliminate the article's square root from p_dot^2=0."""
        num=sp.together(self.p_dot_squared).as_numer_denom()[0]
        return sp.factor(sp.resultant(num,self.relation,s))


def watson_dictionary():
    DeltaK=sp.symbols("DeltaK")
    series=sp.expand(b*G_taylor(p**2,5).subs(kappa,4*DeltaK/b))
    return {"b_equals":"Bz^(J)","kappa_equals":"4*DeltaK^(J)/Bz^(J)",
            "bG_series":series}


def flattened_octahedral(kappa_value=kappa,b_value=b):
    """Chapter-4 octahedral model flattened along a fourfold z axis."""
    axial=sp.Rational(3,2)-3*p**2+sp.Rational(7,2)*p**4
    return PhysicalPrismModel(4,1,kappa_value,b_value,0,sp.Rational(1,2),axial)


def self_check():
    assert reduce_s(total_Dp(square_root_relation()))==0
    expected=(p**2-kappa*p**4/4+kappa**2*p**6/8
              -5*kappa**3*p**8/64+7*kappa**4*p**10/128)
    assert sp.expand(G_taylor(p**2,5)-expected)==0
    for m in (2,4,6):
        model=PhysicalPrismModel(m,1,sp.Rational(1,2),1,0,sp.Rational(1,10))
        assert model.reduce(model.Denergy(model.relation))==0
        assert model.reduce(model.Dp(model.h1)-2*p/s)==0
        print("PHYSICS_G_PASS",m,"turning_degree_p=",
              sp.degree(model.turning_resultant(),p))


if __name__=="__main__": self_check()
