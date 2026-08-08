#!/usr/bin/env python3
"""Watson/PGOPHER convention adapter to classical fixed-J sphere symbols."""
from __future__ import annotations
import sympy as sp

p,phi,L2=sp.symbols("p phi L2")       # p=J_a; J_b+iJ_c transverse
A,B,C=sp.symbols("A B C")
DeltaJ,DeltaJK,DeltaK,deltaJ,deltaK=sp.symbols(
    "DeltaJ DeltaJK DeltaK deltaJ deltaK")
HJ,HJK,HKJ,HK,phiJ,phiJK,phiK=sp.symbols(
    "HJ HJK HKJ HK phiJ phiJK phiK")


def transverse_radius_squared(): return L2-p**2


def ladder_sum(power: int):
    """Classical symbol J_+^power+J_-^power."""
    return 2*transverse_radius_squared()**(power//2)*sp.cos(power*phi)


def rigid_harmonics():
    Bbar=(B+C)/2
    return {0:sp.expand(A*p**2+Bbar*(L2-p**2)),
            2:sp.expand((B-C)*(L2-p**2)/2)}


def A_reduction_quartic_harmonics():
    axial=-DeltaJ*L2**2-DeltaJK*L2*p**2-DeltaK*p**4
    # -1/2 [Q,J_+^2+J_-^2]_+ -> -Q*(J_+^2+J_-^2)
    h2=-2*(deltaJ*L2+deltaK*p**2)*(L2-p**2)
    return {0:sp.expand(axial),2:sp.expand(h2)}


def S_reduction_quartic_harmonics():
    axial=-DeltaJ*L2**2-DeltaJK*L2*p**2-DeltaK*p**4
    return {0:sp.expand(axial),
            2:sp.expand(2*deltaJ*L2*(L2-p**2)),
            4:sp.expand(2*deltaK*(L2-p**2)**2)}


def A_reduction_sextic_harmonics():
    axial=HJ*L2**3+HJK*L2**2*p**2+HKJ*L2*p**4+HK*p**6
    h2=2*(phiJ*L2**2+phiJK*L2*p**2+phiK*p**4)*(L2-p**2)
    return {0:sp.expand(axial),2:sp.expand(h2)}


def S_reduction_sextic_harmonics():
    axial=HJ*L2**3+HJK*L2**2*p**2+HKJ*L2*p**4+HK*p**6
    return {0:sp.expand(axial),
            2:sp.expand(2*phiJ*L2**2*(L2-p**2)),
            4:sp.expand(2*phiJK*L2*(L2-p**2)**2),
            6:sp.expand(2*phiK*(L2-p**2)**3)}


def combine(*tables):
    out={}
    for table in tables:
        for m,x in table.items(): out[m]=sp.expand(out.get(m,0)+x)
    return out


def expression(table):
    return sp.expand(sum(x if m==0 else x*sp.cos(m*phi)
                         for m,x in table.items()))


def direct_rigid_symbol():
    Jb=sp.sqrt(L2-p**2)*sp.cos(phi)
    Jc=sp.sqrt(L2-p**2)*sp.sin(phi)
    return sp.expand_trig(A*p**2+B*Jb**2+C*Jc**2)


def watson_1968_parent_hamiltonian_metadata():
    return {
      "rotational_term":"1/2*(Pi-pi)_alpha*mu_alpha_beta*(Pi-pi)_beta",
      "vibrational_term":"1/2*sum_k P_k^2",
      "quantum_potential":"-hbar^2/8*sum_alpha mu_alpha_alpha",
      "ordinary_potential":"V",
      "classical_scope":"sphere-curve code uses the rotational principal symbol at fixed J^2"
    }


def self_check():
    # Avoid square roots: compare after trig reduction.
    diff=sp.trigsimp(expression(rigid_harmonics())-direct_rigid_symbol())
    assert sp.expand_trig(diff)==0
    assert set(combine(rigid_harmonics(),A_reduction_quartic_harmonics(),
                       A_reduction_sextic_harmonics()))=={0,2}
    assert set(combine(rigid_harmonics(),S_reduction_quartic_harmonics()))=={0,2,4}
    assert set(combine(rigid_harmonics(),S_reduction_quartic_harmonics(),
                       S_reduction_sextic_harmonics()))=={0,2,4,6}
    print("WATSON_PHYSICS_ADAPTER_PASS")


if __name__=="__main__": self_check()
