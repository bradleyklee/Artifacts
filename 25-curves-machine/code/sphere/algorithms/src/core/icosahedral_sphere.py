#!/usr/bin/env python3
"""Classical normalized sixth-rank icosahedral sphere Hamiltonian."""
from __future__ import annotations
import sympy as sp

lam,phi,alpha=sp.symbols("lambda phi alpha")
jx,jy,jz=sp.symbols("Jx Jy Jz",real=True)


def h1():
    return 11*lam**6-15*lam**4+5*lam**2


def h2():
    return 2*lam*(1-lam**2)**sp.Rational(5,2)


def cartesian():
    re_fifth=jx**5-10*jx**3*jy**2+5*jx*jy**4
    J2=jx**2+jy**2+jz**2
    # Chapter-4 normalization is (16*H_HarterWeeks+5)/21 on J2=1.
    return sp.expand(sp.Rational(1,21)*(
        231*jz**6-315*jz**4*J2+105*jz**2*J2**2-5*J2**3
        +42*jz*re_fifth+5*J2**3))


def eliminated_P():
    """dot(lambda)^2 after eliminating cos(5 phi) from H=alpha."""
    h2sq=4*lam**2*(1-lam**2)**5
    return sp.factor(-25*((alpha-h1())**2-h2sq))


def chapter4_operator():
    return [5*(5-21*alpha),4*(5+44*alpha-81*alpha**2),
            4*alpha*(5+27*alpha)*(1-alpha)]


def self_check():
    H=cartesian()
    assert sp.Poly(H,jx,jy,jz).total_degree()==6
    pole=sp.factor(H.subs({jx:0,jy:0,jz:1}))
    assert pole==1
    assert h1().subs(lam,1)==1 and h2().subs(lam,1)==0
    assert sp.degree(eliminated_P(),lam)==12
    print("ICOSAHEDRAL_SPHERE_MODEL_PASS",sp.factor(eliminated_P()))

if __name__=="__main__":self_check()
