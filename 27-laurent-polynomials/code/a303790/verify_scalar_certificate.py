"""Exact verification of the scalar period certificate.

The proof uses explicit differentiation, denominator clearing, and polynomial
remainder modulo K-E.  It does not call sympy.simplify.
"""
import sympy as sp

p, q, E = sp.symbols("p q E")

K = p**2 + q**2 + p**3 + q**3
Kp = sp.diff(K, p)
Kq = sp.diff(K, q)

A2 = E*(27*E - 8)*(27*E - 4)
A1 = 2187*E**2 - 648*E + 32
A0 = 15*(27*E - 4)

V = -2*(
    2187*E**2*p*q + 729*E**2*p + 729*E**2*q
    + 243*E*p**2*q + 81*E*p**2
    - 3645*E*p*q**4 - 4860*E*p*q**3
    - 1215*E*p*q**2 - 216*E*p*q - 153*E*p
    - 1215*E*q**4 - 1134*E*q**3 + 81*E*q**2
    - 72*E*q - 15*E
    + 324*p**2*q**4 + 432*p**2*q**3
    - 132*p**2*q - 17*p**2
    + 324*p*q**5 + 1296*p*q**4 + 1269*p*q**3
    + 201*p*q**2 - 96*p*q
    - 243*q**6 - 378*q**5 + 189*q**4 + 387*q**3
    + 31*q**2 - 32*q
)

Xi = sp.cancel(V / Kp**3)

def D_E(expr):
    return sp.cancel(sp.diff(expr, p) / Kp)

f = sp.cancel(2 / Kp)

left = sp.cancel(A2*D_E(D_E(f)) + A1*D_E(f) + A0*f)
right = sp.cancel(sp.diff(Xi, q) - Kq*sp.diff(Xi, p)/Kp)

numerator, denominator = sp.fraction(sp.cancel(left-right))
remainder = sp.Poly(sp.expand(numerator), p).rem(sp.Poly(K-E, p))

assert remainder.as_expr() == 0
print("scalar certificate residual: 0 modulo K-E")
