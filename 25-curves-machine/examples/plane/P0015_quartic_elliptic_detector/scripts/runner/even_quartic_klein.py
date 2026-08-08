#!/usr/bin/env python3
"""Direct elliptic quotient and Klein invariant for even quartic Hamiltonians.

Family:
    H = p^2 + q^2 + a*p^4 + b*p^3*q + c*p^2*q^2 + d*p*q^3 + e*q^4.

The central involution (p,q)->(-p,-q) fixes the period form dq/H_p.
With t=p/q and s=q^2, the quotient is the binary-quartic curve

    y^2 = (t^2+1)^2 + 4*alpha*(a*t^4+b*t^3+c*t^2+d*t+e),

and dq/H_p = -dt/(2*y).

No Weierstrass conversion is used.  Classical binary-quartic invariants give
Klein J directly, and the universal elliptic Picard--Fuchs formula gives an
order-two operator.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import sympy as sp

alpha = sp.symbols("alpha")
a, b, c, d, e = sp.symbols("a b c d e")
t = sp.symbols("t")


def binary_quartic(a0=a, b0=b, c0=c, d0=d, e0=e):
    return sp.expand((t**2 + 1)**2 + 4*alpha*(a0*t**4+b0*t**3+c0*t**2+d0*t+e0))


def binary_invariants(a0=a, b0=b, c0=c, d0=d, e0=e):
    # f=A*t^4+B*t^3+C*t^2+D*t+E
    A = 1 + 4*alpha*a0
    B = 4*alpha*b0
    C = 2 + 4*alpha*c0
    D = 4*alpha*d0
    E = 1 + 4*alpha*e0
    I = sp.expand(12*A*E - 3*B*D + C**2)
    Jb = sp.expand(72*A*C*E + 9*B*C*D - 27*A*D**2 - 27*B**2*E - 2*C**3)
    disc = sp.expand((4*I**3-Jb**2)/27)
    klein_J = sp.cancel(4*I**3/(4*I**3-Jb**2))
    return I, Jb, disc, klein_J


def raw_operator(a0=a, b0=b, c0=c, d0=d, e0=e):
    I, Jb, _, _ = binary_invariants(a0,b0,c0,d0,e0)
    # This weighted choice has c4^3/(c4^3-c6^2)=Klein J.
    c4 = sp.expand(4*I)
    c6 = sp.expand(4*Jb)
    Delta = sp.expand(c4**3-c6**2)
    G = sp.expand(2*c4*sp.diff(c6,alpha)-3*c6*sp.diff(c4,alpha))
    P2 = sp.expand(144*Delta*G)
    P1 = sp.expand(144*(sp.diff(Delta,alpha)*G-Delta*sp.diff(G,alpha)))
    P0 = sp.expand(
        12*(sp.diff(Delta,alpha,2)*G-sp.diff(Delta,alpha)*sp.diff(G,alpha))
        -9*G*c4*sp.diff(c4,alpha)**2
        +4*G*sp.diff(c6,alpha)**2
    )
    return [P0,P1,P2], {"c4":c4,"c6":c6,"Delta":Delta,"G":G}


def reduced_operator(a0=a, b0=b, c0=c, d0=d, e0=e):
    op, aux = raw_operator(a0,b0,c0,d0,e0)
    g = sp.gcd(sp.Poly(op[0],alpha),sp.gcd(sp.Poly(op[1],alpha),sp.Poly(op[2],alpha))).as_expr()
    op = [sp.cancel(P/g) for P in op]
    return op, sp.factor(g), aux


def top_monic(op: Iterable[sp.Expr]):
    op=list(op)
    lc=sp.Poly(op[-1],alpha).LC()
    return [sp.expand(P/lc) for P in op]


def rat_mod(x, prime: int) -> int:
    x=sp.Rational(x)
    return int(x.p)%prime * pow(int(x.q)%prime,-1,prime)%prime


def check_series(op, terms, prime: int):
    ppolys=[]
    for P in op:
        ppolys.append({int(mon[0]):rat_mod(coeff,prime) for mon,coeff in sp.Poly(P,alpha).terms()})
    residuals=[]
    for n in range(len(terms)-2):
        total=0
        for j,P in enumerate(ppolys):
            for k,coeff in P.items():
                m=n-k
                if m<0:
                    continue
                idx=m+j
                if idx>=len(terms):
                    continue
                falling=1
                for z in range(1,j+1):
                    falling=falling*(m+z)%prime
                total=(total+coeff*falling*(terms[idx]%prime))%prime
        residuals.append(total)
    return residuals


def archived_operator(path: Path):
    obj=json.loads(path.read_text())
    out=[]
    for block in obj["coefficients"]:
        out.append(sp.expand(sum(sp.Rational(v)*alpha**int(k) for k,v in block.items())))
    return out


def verify(root: Path):
    checks={}

    # Clean exact example: H=p^2+q^2+(p^4+p^2*q^2)/4.
    simple,_g,_aux=reduced_operator(sp.Rational(1,4),0,sp.Rational(1,4),0,0)
    simple=top_monic(simple)
    expected=[sp.Rational(1,4),2*alpha+1,alpha*(alpha+1)]
    checks["simple_exact_operator"] = all(sp.expand(x-y)==0 for x,y in zip(simple,expected))

    # Fully generic central-inversion model A: exact characteristic-zero match.
    parsA=[sp.Rational(41,693),sp.Rational(-18,221),sp.Rational(-16,33),sp.Rational(86,221),sp.Rational(239,693)]
    opA=top_monic(reduced_operator(*parsA)[0])
    archA=archived_operator(root/"regression_data/even_quartic_generic_A_operator_exact.json")
    checks["generic_A_exact_operator"] = all(sp.expand(x-y)==0 for x,y in zip(opA,archA))

    # Independent generic model B: 180 modular coefficients at two primes.
    modelB=json.loads((root/"regression_data/even_quartic_generic_B.json").read_text())
    terms={(z[0],z[1]):sp.Rational(z[2]) for z in modelB["monomials"]["4"]}
    parsB=[terms[(4,0)],terms[(3,1)],terms[(2,2)],terms[(1,3)],terms[(0,4)]]
    opB=reduced_operator(*parsB)[0]
    modular={}
    for prime in (65521,65497):
        seq=json.loads((root/f"regression_data/even_quartic_generic_B_series_{prime}.json").read_text())["terms"]
        residuals=check_series(opB,seq,prime)
        modular[str(prime)]={"equations":len(residuals),"nonzero_residuals":sum(r!=0 for r in residuals)}
    checks["generic_B_modular"] = all(v["nonzero_residuals"]==0 for v in modular.values())

    I,Jb,disc,K=binary_invariants()
    result={
        "status":"PASS" if all(checks.values()) else "FAIL",
        "checks":checks,
        "generic_B_modular":modular,
        "symbolic":{
            "binary_quartic":str(binary_quartic()),
            "I":str(sp.factor(I)),
            "J_binary":str(sp.factor(Jb)),
            "discriminant":str(sp.factor(disc)),
            "Klein_J":str(K),
            "compact_operator": {
                "P2": "144*Delta*G",
                "P1": "144*(Delta_prime*G-Delta*G_prime)",
                "P0": "12*(Delta_double_prime*G-Delta_prime*G_prime)-9*G*c4*c4_prime^2+4*G*c6_prime^2",
                "definitions": "c4=4*I, c6=4*J_binary, Delta=c4^3-c6^2, G=2*c4*c6_prime-3*c6*c4_prime"
            },
            "generic_reduced_operator_degrees":[5,6,7],
        },
    }
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--verify",action="store_true")
    ap.add_argument("--json",action="store_true")
    args=ap.parse_args()
    root=Path(__file__).resolve().parent
    if args.verify:
        result=verify(root)
        print(json.dumps(result,indent=2))
        raise SystemExit(0 if result["status"]=="PASS" else 1)
    I,Jb,disc,K=binary_invariants()
    data={
        "binary_quartic":str(binary_quartic()),
        "I":str(sp.factor(I)),
        "J_binary":str(sp.factor(Jb)),
        "discriminant":str(sp.factor(disc)),
        "Klein_J":str(K),
        "compact_operator": {
            "P2": "144*Delta*G",
            "P1": "144*(Delta_prime*G-Delta*G_prime)",
            "P0": "12*(Delta_double_prime*G-Delta_prime*G_prime)-9*G*c4*c4_prime^2+4*G*c6_prime^2",
            "definitions": "c4=4*I, c6=4*J_binary, Delta=c4^3-c6^2, G=2*c4*c6_prime-3*c6*c4_prime"
        },
        "generic_reduced_operator_degrees":[5,6,7],
    }
    print(json.dumps(data,indent=2) if args.json else "\n".join(f"{k}: {v}" for k,v in data.items()))


if __name__=="__main__":
    main()
