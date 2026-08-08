#!/usr/bin/env python3
"""Exact comparison with Gegelia--van Straten, The Platonic Elliptic Surfaces."""

import sympy as sp

q, x3, x4, t, alpha = sp.symbols("q x3 x4 t alpha")
X, Y = sp.symbols("X Y")

# ---------------------------------------------------------------------
# The octahedral sphere energy used in the paper is
# Q = x^2 y^2 + y^2 z^2 + z^2 x^2 on P=x^2+y^2+z^2=1.
#
# Dissertation energy:
#     alpha = 2 - 4 Q.
#
# Critically scaled OEIS variables:
#     A318245 / O(4): x4 = 3 Q / 16
#     A186375 / O(3): x3 = (1 - 3 Q) / 4
# ---------------------------------------------------------------------

D4 = 1 - 48*x4 + 720*x4**2 - 3072*x4**3
X4 = sp.factor(
    1728*x4**4*(1-16*x4)**3*(3-64*x4)**2 / D4**3
)

D3 = 1 - 24*x3 + 144*x3**2 + 768*x3**3
X3 = sp.factor(
    6912*x3**3*(4*x3-1)**4*(16*x3-1)**2 / D3**3
)

x4_of_q = 3*q/16
x3_of_q = (1-3*q)/4

# The two local formulas are the same global 1728/j map.
assert sp.factor(X4.subs(x4, x4_of_q) - X3.subs(x3, x3_of_q)) == 0
X_oct_q = sp.factor(X4.subs(x4, x4_of_q))

# ---------------------------------------------------------------------
# Legendre K parameters for the two real wells.
# Put s=sqrt(1-3Q).  The two physical branches are reciprocal.
# ---------------------------------------------------------------------

s = sp.symbols("s")
m4 = sp.factor((1-s)**2*(1+2*s)/(4*s**3))
m3 = sp.factor(4*s**3/((1-s)**2*(1+2*s)))
assert sp.factor(m3*m4 - 1) == 0

def X_legendre(m):
    return sp.factor(27*m**2*(1-m)**2/(4*(1-m+m**2)**3))

# O(4): s=sqrt(1-16*x4)
assert sp.factor(
    X_legendre(m4) - X4.subs(x4, (1-s**2)/16)
) == 0

# O(3): x3=s^2/4
assert sp.factor(
    X_legendre(m3) - X3.subs(x3, s**2/4)
) == 0

# ---------------------------------------------------------------------
# The paper's octahedral quotient surface 234III and its degree-2
# isogenous Laurent-plane companion 126III.
# These are the g2,g3 entries in Table 10, using the O(3) cusp at t=0.
# ---------------------------------------------------------------------

g2_234 = 64*t**3 + 12*t**2 - 2*t + sp.Rational(1, 12)
g3_234 = (
    -128*t**4 + sp.Rational(56, 3)*t**3 - 2*t**2
    + sp.Rational(1, 6)*t - sp.Rational(1, 216)
)
Delta_234 = sp.factor(g2_234**3 - 27*g3_234**2)
j_234 = sp.factor(1728*g2_234**3/Delta_234)

g2_126 = -16*t**3 + 12*t**2 - 2*t + sp.Rational(1, 12)
g3_126 = (
    -16*t**4 + sp.Rational(28, 3)*t**3 - 2*t**2
    + sp.Rational(1, 6)*t - sp.Rational(1, 216)
)
Delta_126 = sp.factor(g2_126**3 - 27*g3_126**2)
j_126 = sp.factor(1728*g2_126**3/Delta_126)

assert Delta_234 == 4*t**3*(4*t-1)**4*(16*t-1)**2
assert Delta_126 == -16*t**6*(4*t-1)**2*(16*t-1)

# Classical level-2 modular polynomial.
Phi2 = (
    X**3 + Y**3 - X**2*Y**2
    + 1488*X*Y*(X+Y)
    - 162000*(X**2+Y**2)
    + 40773375*X*Y
    + 8748000000*(X+Y)
    - 157464000000000
)
assert sp.factor(sp.together(Phi2.subs({X:j_126, Y:j_234}))) == 0

# The A186375 rational pullback is exactly 1728/j_234.
assert sp.factor(1728/j_234 - X3.subs(x3, t)) == 0

# ---------------------------------------------------------------------
# Triangle-rectangle family.
# This comparison is deliberately kept at the family level.
# ---------------------------------------------------------------------

X_TR = sp.factor(
    -27*alpha**2*(4*alpha-1)*(9*alpha+4)**2
    / (4*(1+9*alpha**2)**3)
)
j_TR = sp.factor(1728/X_TR)

# Degrees of the three base maps.
def rational_map_degree(expr, var):
    num, den = sp.cancel(expr).as_numer_denom()
    return max(sp.degree(num, var), sp.degree(den, var))

degrees = {
    "triangle_rectangle_j_degree": rational_map_degree(j_TR, alpha),
    "octahedral_234_j_degree": rational_map_degree(j_234, t),
    "octahedral_126_j_degree": rational_map_degree(j_126, t),
}
assert degrees == {
    "triangle_rectangle_j_degree": 6,
    "octahedral_234_j_degree": 9,
    "octahedral_126_j_degree": 9,
}

# No rational base substitution can identify either degree-9 family with
# the degree-6 triangle-rectangle family.  Algebraic correspondences and
# isogenies remain possible.
#
# Verify that the 126 equality components occur inside the level-2
# comparison between triangle-rectangle and 234.
eq_126_num = sp.factor(sp.together(j_TR-j_126).as_numer_denom()[0])
phi_TR_234_num = sp.factor(
    sp.together(Phi2.subs({X:j_TR, Y:j_234})).as_numer_denom()[0]
)
assert sp.rem(phi_TR_234_num, eq_126_num, alpha) == 0

print("PASS: O(4) and O(3) are local expansions of one global octahedral J-map")
print("PASS: their Legendre parameters satisfy m3*m4 = 1")
print("PASS: both K pullbacks reproduce the same 1728/j map")
print("PASS: Table-10 discriminants for 234III and 126III")
print("PASS: Phi_2(j_126,j_234)=0, confirming the degree-2 isogeny")
print("PASS: A186375 pullback is exactly 1728/j_234")
print("PASS: family degrees are TR=6, 234III=9, 126III=9")
print("PASS: the 126III equality locus is a component of the")
print("      level-2 TR-versus-234III modular correspondence")
