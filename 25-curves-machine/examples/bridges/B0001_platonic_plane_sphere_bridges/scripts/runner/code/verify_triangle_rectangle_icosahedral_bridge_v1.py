#!/usr/bin/env python3
"""
Exact first bridge from the triangle-rectangle model to the icosahedral
sphere family.

The main result is not an octahedral-style genus-one intermediate quotient.
Instead:

  * the icosahedral Hamiltonian is written exactly in the same tetrahedral
    invariants r and s that produced the triangle-rectangle curve;
  * quotienting the genus-25 sphere curve by A4 gives a smooth genus-3
    plane quartic;
  * that genus-3 curve maps explicitly, with degree 5, to the full
    icosahedral elliptic quotient 235II;
  * the sphere Hamiltonian time form descends exactly to the quotient;
  * local cusp orders rule out a smooth unramified triangle-well to
    icosahedral C3-well identification, but ramified and elliptic-factor
    correspondences remain open.

Requires: sympy
"""

import sympy as sp

# ----------------------------------------------------------------------
# Coordinates and exact tetrahedral frame inside the icosahedral group
# ----------------------------------------------------------------------

x, y, z = sp.symbols("x y z")
a, b, c = sp.symbols("a b c")
h, A, r, s, Z = sp.symbols("h A r s Z")

rt5 = sp.sqrt(5)
sa = sp.sqrt(10 - 2*rt5)
sb = sp.sqrt(10 + 2*rt5)

# An orientation-preserving orthogonal frame whose standard tetrahedral
# A4 is a subgroup of the given icosahedral A5.
E = sp.Matrix([
    [sa/4, -3*sb/20-sa/20, sb/20+sa/10],
    [(1+rt5)/4, sp.Rational(1,2), (1-rt5)/4],
    [0, -sa/10+sb/5, sb/10+sa/5],
])

assert sp.simplify(E.T*E) == sp.eye(3)
assert sp.simplify(E.det()) == 1

v = E*sp.Matrix([a, b, c])

P = a**2 + b**2 + c**2
A4 = a**2*b**2 + b**2*c**2 + a**2*c**2
r3 = a*b*c
s6 = (a**2-b**2)*(b**2-c**2)*(c**2-a**2)

# ----------------------------------------------------------------------
# Icosahedral Goursat invariants from the paper
# ----------------------------------------------------------------------

Qi = sp.expand(
    z * (
        -5*z**3*(x**2+y**2)
        + 5*z*(x**2+y**2)**2
        - 2*x*(x**4-10*x**2*y**2+5*y**4)
        + z**5
    )
)

Ri = sp.expand(
    (4*x**2+6*x*z+z**2)
    *(
        x**4+8*x**3*z-10*x**2*y**2+14*x**2*z**2
        -8*x*z**3+5*y**4-10*y**2*z**2+z**4
    )
    *(
        x**4-2*x**3*z-10*x**2*y**2-x**2*z**2
        +30*x*y**2*z+2*x*z**3+5*y**4-25*y**2*z**2+z**4
    )
)

Si = sp.expand(
    8*y*(5*x**4-10*x**2*y**2+y**4)*(x**2-x*z-z**2)
    *(
        x**4-10*x**2*y**2+5*y**4-12*x**3*z+20*x*y**2*z
        +44*x**2*z**2-20*y**2*z**2-48*x*z**3+16*z**4
    )
    *(
        x**4-10*x**2*y**2+5*y**4+8*x**3*z-40*x*y**2*z
        +24*x**2*z**2-40*y**2*z**2+32*x*z**3+16*z**4
    )
)

subs_E = {x:v[0], y:v[1], z:v[2]}

# ----------------------------------------------------------------------
# Exact expression of the icosahedral Hamiltonian in tetrahedral
# invariants.
# ----------------------------------------------------------------------

Q_target = (
    sp.Rational(5,2)*P*A4
    - sp.Rational(55,2)*r3**2
    + sp.Rational(5,2)*rt5*s6
)

Q_diff = sp.Poly(
    sp.expand(Qi.subs(subs_E, simultaneous=True) - Q_target),
    a, b, c
)
for coefficient in Q_diff.coeffs():
    coefficient = sp.radsimp(sp.simplify(coefficient))
    coefficient = sp.simplify(coefficient.subs(sa*sb, 4*rt5))
    assert coefficient == 0

# ----------------------------------------------------------------------
# Exact expression of the degree-10 invariant R_I in the same frame.
# ----------------------------------------------------------------------

R_target = sp.Rational(25,2)*(
    12*rt5*A4*s6
    + 380*A4*r3**2
    - 20*P*A4**2
    - 3*rt5*P**2*s6
    - 95*P**2*r3**2
    + 5*P**3*A4
)

R_diff = sp.Poly(
    sp.expand(Ri.subs(subs_E, simultaneous=True) - R_target),
    a, b, c
)
for coefficient in R_diff.coeffs():
    coefficient = sp.radsimp(sp.simplify(coefficient))
    coefficient = sp.simplify(coefficient.subs(sa*sb, 4*rt5))
    assert coefficient == 0

# ----------------------------------------------------------------------
# Tetrahedral invariant relation.
#
# In the paper's homogeneous degree convention the tetrahedral generators
# have degrees P=2, Q=r3=3, R=A4=4, S=s6=6.
# ----------------------------------------------------------------------

tetra_relation = sp.factor(
    s6**2
    - (
        -4*A4**3
        + P**2*A4**2
        + 18*P*r3**2*A4
        - (4*P**3+27*r3**2)*r3**2
    )
)
assert tetra_relation == 0

# ----------------------------------------------------------------------
# A4 quotient of the icosahedral level Q_I=h on P=1.
#
# sqrt(5)*s = 2h/5 - A + 11r^2.
# ----------------------------------------------------------------------

F_A4 = sp.factor(
    125*A**3 - 25*A**2 - 5*A*h - 700*A*r**2
    + h**2 + 55*h*r**2 + 1600*r**4 + 125*r**2
)

s_on_level = (sp.Rational(2,5)*h - A + 11*r**2)/rt5

check_level = sp.factor(
    (sp.Rational(2,5)*h-A+11*r**2)**2
    - 5*(
        -4*A**3 + A**2 + 18*r**2*A - (4+27*r**2)*r**2
    )
)
assert sp.factor(check_level - sp.Rational(4,25)*F_A4) == 0

# Generic smoothness test at h=2.  The projective quartic has one point at
# infinity [A:r:Z]=[1:0:0], where dF/dZ=125 != 0.
F2 = sp.expand(F_A4.subs(h, 2))
assert sp.groebner(
    [F2, sp.diff(F2,A), sp.diff(F2,r)],
    A, r, order="lex"
).polys == [sp.Poly(1, A, r, domain=sp.ZZ)]

Fhom = (
    125*A**3*Z - 25*A**2*Z**2 - 5*A*h*Z**3
    - 700*A*r**2*Z + h**2*Z**4 + 55*h*r**2*Z**2
    + 1600*r**4 + 125*r**2*Z**2
)
assert Fhom.subs({A:1,r:0,Z:0}) == 0
assert sp.diff(Fhom,Z).subs({A:1,r:0,Z:0}) == 125

# ----------------------------------------------------------------------
# Explicit degree-5 map from the A4 quotient to the full A5 quotient.
# ----------------------------------------------------------------------

Rmap = sp.factor(
    5*(4*A-1)*(-20*A+3*h+320*r**2)
)

Cmap = (
    -24000*A**3 + 14800*A**2 - 540*A*h
    -25600*A*r**2 - 2500*A
    +33*h**2 +5440*h*r**2 +50*h
    +204800*r**4 +125
)

Smap = sp.factor(sp.Rational(8,5)*rt5*r*Cmap)

icosa_cubic = (
    -Rmap**3
    +(4-65*h)*Rmap**2
    +h*(720*h**2+200-795*h)*Rmap
    +500*h**2-2275*h**3+3440*h**4-1728*h**5
)

map_residual = sp.Poly(
    sp.expand(Smap**2 - icosa_cubic),
    A
)
map_remainder = sp.rem(map_residual, sp.Poly(F_A4,A)).as_expr()
assert sp.factor(map_remainder) == 0

# ----------------------------------------------------------------------
# Hamiltonian time differential on the full icosahedral quotient.
# ----------------------------------------------------------------------

J = sp.Matrix([x,y,z])
grad_R = sp.Matrix([sp.diff(Ri,w) for w in (x,y,z)])
grad_Q = sp.Matrix([sp.diff(Qi,w) for w in (x,y,z)])
Rdot = sp.factor(grad_R.dot(J.cross(grad_Q)))

assert sp.factor(Rdot + 10*Si) == 0
# Therefore for H=Q_I: dt = -dR_I/(10*S_I).

# ----------------------------------------------------------------------
# D5 quotient around the fivefold axis.
#
# u=z^2, C=Re((x+iy)^5), D=Im((x+iy)^5).
# The invariant quotient can be written Y^2=u*F6(u), generically degree 7,
# hence genus 3.
# ----------------------------------------------------------------------

u, Y = sp.symbols("u Y")
Bpoly = 11*u**3 - 15*u**2 + 5*u - h
F6 = sp.factor(
    4*u*(1-u)**5 - Bpoly**2
)
D5_rhs = sp.factor(u*F6)

# Squarefree test at h=2.
D5_2 = sp.Poly(D5_rhs.subs(h,2),u)
assert sp.gcd(D5_2, sp.diff(D5_2,u)).degree() == 0
assert D5_2.degree() == 7

# ----------------------------------------------------------------------
# Local obstruction to a smooth triangle-well -> icosahedral triangle-well
# identification.
# ----------------------------------------------------------------------

alpha, q = sp.symbols("alpha q")
X_TR = sp.factor(
    -27*alpha**2*(4*alpha-1)*(9*alpha+4)**2
    /(4*(1+9*alpha**2)**3)
)
P_I = 135*q**3+115*q**2+5*q+1
X_I = sp.factor(
    27*q**2*(1-q)**5*(27*q+5)**3
    /(4*P_I**3)
)

def zero_order(expr, var, point, maximum=12):
    w = sp.symbols("w")
    series = sp.series(expr.subs(var, point+w), w, 0, maximum).removeO()
    for k in range(maximum):
        if sp.expand(series).coeff(w,k) != 0:
            return k
    raise RuntimeError("zero order not found")

assert zero_order(X_TR,alpha,0) == 2
assert zero_order(X_I,q,sp.Rational(-5,27)) == 3
assert zero_order(X_I,q,1) == 5
assert zero_order(X_I,q,0) == 2

# Equal-j relation is irreducible over Q and has bidegree (6,10).
equal_j_numerator = sp.factor(
    sp.together(X_TR-X_I).as_numer_denom()[0]
)
factors = sp.factor_list(equal_j_numerator)[1]
assert len(factors) == 1 and factors[0][1] == 1
assert sp.Poly(equal_j_numerator,alpha).degree() == 6
assert sp.Poly(equal_j_numerator,q).degree() == 10

print("PASS exact A4 frame inside the icosahedral A5")
print("PASS Q_I in tetrahedral invariants")
print("PASS R_I in tetrahedral invariants")
print("PASS genus-3 A4 quotient equation")
print("PASS explicit degree-5 map to 235II")
print("PASS icosahedral Hamiltonian time descent dR/dt=-10S")
print("PASS genus-3 D5 quotient")
print("PASS local cusp-order obstruction")
print("PASS irreducible equal-j correspondence of bidegree (6,10)")
print()
print("Icosahedral Hamiltonian in tetrahedral variables:")
print("  h = (5/2) A - (55/2) r^2 + (5*sqrt(5)/2) s")
print()
print("A4 quotient:")
print(" ", F_A4, "= 0")
print()
print("Degree-5 map to 235II:")
print("  R_I =", Rmap)
print("  S_I = (8*sqrt(5)/5)*r*C(A,r,h)")
print()
print("Time form:")
print("  dt = -dR_I/(10*S_I)")
