#!/usr/bin/env python3
from __future__ import annotations

from functools import lru_cache
from itertools import product
from pathlib import Path
import json
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]

n, t, x = sp.symbols("n t x")
Q = 1 - 6*t - 4*t**2 - t**3
Phi = (1+t)/Q
R = Phi/t

p = [
    3*(n+1)*(3*n-1)*(3*n+7),
    -15*(2*n+3)*(18*n**2+54*n+29),
    75*(n+2)*(54*n**2+216*n+209),
    -6750*(n+2)*(n+3)*(2*n+5),
    491*(n+2)*(n+3)*(n+4),
]

c = [
    -491*n*(n+1)*(n+2),
    4*n*(n+1)*(1411*n+2791),
    n*(11394*n**2+34382*n+23093),
    15004*n**3+47764*n**2+31584*n-21,
    16447*n**3+56569*n**2+42180*n+378,
    6*(2644*n**3+9656*n**2+7971*n-336),
    7*(1812*n**3+6940*n**2+6463*n+225),
    4*(2094*n**3+8438*n**2+9116*n+1827),
    4611*n**3+19393*n**2+23539*n+7812,
    15*(132*n**3+568*n**2+730*n+287),
    198*(n+1)**2*(3*n+7),
    36*(n+1)**2*(3*n+7),
    3*(n+1)**2*(3*n+7),
]
P = sum(c[k]*t**k for k in range(13))
C = (1+t)*P/(n*(n+1)*t**3*Q**3)


def check_telescoping_identity() -> None:
    lhs = sum(p[j]*R**j/(n+j) for j in range(5))
    rhs = sp.diff(C,t) + n*sp.diff(R,t)/R*C
    delta = sp.cancel(lhs-rhs)
    assert delta == 0, sp.factor(delta)
    print("PASS exact creative-telescoping identity")


def load_terms() -> list[int]:
    obj = json.loads((ROOT/'data'/'oeis_initial_terms.json').read_text())
    return obj['terms']


def check_oeis_algebraic_equation(terms: list[int]) -> None:
    A = sum(value*x**i for i,value in enumerate(terms))
    residual = sp.Poly(sp.expand(A**4-(5-x)*A+4),x)
    for degree in range(len(terms)):
        assert residual.coeff_monomial(x**degree) == 0
    print(f"PASS algebraic equation through x^{len(terms)-1}")


def lagrange_term(N: int) -> int:
    expansion = sp.series(Phi**N,t,0,N).removeO().expand()
    return int(expansion.coeff(t,N-1)//N)


def check_lagrange_terms(terms: list[int]) -> None:
    got = [1] + [lagrange_term(N) for N in range(1,len(terms))]
    assert got == terms, (got,terms)
    print(f"PASS Lagrange/residue terms n=0..{len(terms)-1}")


def check_recurrence(terms: list[int]) -> None:
    for N in range(len(terms)-4):
        value = sum(int(p[j].subs(n,N))*terms[N+j] for j in range(5))
        assert value == 0, (N,value)
    print(f"PASS recurrence n=0..{len(terms)-5}")


@lru_cache(None)
def members(N: int) -> tuple[str,...]:
    if N == 0:
        return ("0",)
    out: set[str] = set()
    if N == 1:
        out.add("1")
    for child in members(N-1):
        if child != "0":
            out.add("{"+child+"}")
    for sizes in product(range(N+1),repeat=4):
        if sum(sizes) != N or sum(size>0 for size in sizes) < 2:
            continue
        choices = [("0",) if size==0 else members(size) for size in sizes]
        for slots in product(*choices):
            out.add("{"+",".join(slots)+"}")
    return tuple(sorted(out))


def check_literal_enumeration() -> None:
    counts = [len(members(N)) for N in range(5)]
    assert counts == [1,1,7,95,1614], counts
    expected_n2 = {
        "{1}","{1,1,0,0}","{1,0,1,0}","{1,0,0,1}",
        "{0,1,1,0}","{0,1,0,1}","{0,0,1,1}",
    }
    assert set(members(2)) == expected_n2
    print("PASS literal grammar counts n=0..4 and exact n=2 member set")


def check_json_payload() -> None:
    obj = json.loads((ROOT/'payload'/'certificate.json').read_text())
    assert obj['sequence'] == 'A244856'
    assert len(obj['certificate']['P_coefficients_by_t_power']) == 13
    assert len(obj['recurrence']['p']) == 5
    print("PASS certificate.json schema sanity")


def main() -> None:
    terms = load_terms()
    check_json_payload()
    check_literal_enumeration()
    check_oeis_algebraic_equation(terms)
    check_lagrange_terms(terms)
    check_recurrence(terms)
    check_telescoping_identity()
    print("ALL CHECKS PASSED")

if __name__ == '__main__':
    main()
