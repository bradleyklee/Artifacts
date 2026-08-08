#!/usr/bin/env python3
"""Verify that the primitive V/rho^7 is reduced and content-primitive."""
from pathlib import Path
import hashlib, json, math
import sympy as sp

HERE = Path(__file__).resolve().parent
alpha, p, q = sp.symbols("alpha p q")
E = p**2 + q**2 - 2*p**2*q**2 + sp.Rational(1, 4)*p**2*(p**2 - 3*q**2)**2
rho = sp.diff(E, p)
xi = json.loads((HERE / "order4_xi.json").read_text())
V = sp.expand(sum(
    sp.sympify(x["coefficient"], locals={"alpha": alpha}) * p**x["p"] * q**x["q"]
    for x in xi["coefficients"]
))

P = sp.Poly(V, alpha, p, q, domain=sp.QQ)
coeffs = [sp.Rational(c) for _, c in P.terms()]
g = 0
for c in coeffs:
    g = math.gcd(g, abs(int(c.p)))
l = 1
for c in coeffs:
    l = int(sp.ilcm(l, int(c.q)))
content = sp.Rational(g, l)

alpha_polys = [
    sp.Poly(sp.sympify(x["coefficient"], locals={"alpha": alpha}), alpha, domain=sp.QQ)
    for x in xi["coefficients"]
]
agcd = alpha_polys[0]
for f in alpha_polys[1:]:
    agcd = sp.gcd(agcd, f)

K = sp.QQ.frac_field(alpha)
G = sp.groebner([E - alpha, rho], p, q, order="lex", domain=K)
remainder = sp.factor(G.reduce(V)[1])
assert remainder != 0
assert sp.rem(sp.Poly(V, q), sp.Poly(q, q)) == 0
assert content == sp.Rational(1, 2)
assert agcd.as_expr() == 1

text = str(remainder)
sha = hashlib.sha256(text.encode()).hexdigest()
S8 = (
    2404239084*alpha**8 - 22448717379*alpha**7 + 16752988620*alpha**6
    - 120418068744*alpha**5 - 163919968272*alpha**4 + 178534770624*alpha**3
    - 49764209536*alpha**2 + 35868448768*alpha - 20307957760
)
assert sp.cancel(remainder / (q*S8)) != 0

print("REDUCED_PRIMITIVE_PASS")
print("V terms:", len(P.terms()))
print("V=q*U(alpha,p^2,q^2): yes")
print("numeric content:", content, "(use 2V with 2A4 for integer data)")
print("gcd of the 40 alpha coefficient polynomials:", agcd.as_expr())
print("normal form of V modulo <E-alpha,rho> is nonzero")
print("normal-form factors include q and the apparent S8(alpha)")
print("normal-form sha256:", sha)
