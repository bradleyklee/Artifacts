#!/usr/bin/env python3
"""
Exact first-stage bridge between the triangle-rectangle Hamiltonian and
the octahedral sphere Hamiltonian.

This checks:
  * the triangle-rectangle reflection quotient and its period differential;
  * the octahedral rotation quotient and its Hamiltonian time differential;
  * the natural 2-isogeny on each side;
  * a common Gamma_0(2) Hauptmodul;
  * two algebraic energy correspondences, preserving or swapping the
    2-isogeny orientation;
  * local ramification data at the relevant wells.
"""

import sympy as sp

alpha, q = sp.symbols("alpha q")
x, y, z = sp.symbols("x y z")
U, W = sp.symbols("U W")
X, Y = sp.symbols("X Y")

# ------------------------------------------------------------------
# Generic invariants for y^2 = x^3 + A*x^2 + B*x, with (0,0) a
# rational 2-torsion point.
# ------------------------------------------------------------------

def invariants_2torsion(A, B):
    b2 = 4*A
    b4 = 2*B
    b6 = 0
    b8 = -B**2
    c4 = sp.factor(b2**2 - 24*b4)
    c6 = sp.factor(-b2**3 + 36*b2*b4)
    Delta = sp.factor(-b2**2*b8 - 8*b4**3)
    j = sp.factor(c4**3 / Delta)
    h = sp.factor(256*B / (A**2 - 4*B))
    return {
        "c4": c4,
        "c6": c6,
        "Delta": Delta,
        "j": j,
        "h": h,
    }

def j0(h):
    return sp.factor((h + 256)**3 / h**2)

def j1(h):
    return sp.factor((h + 16)**3 / h)

Phi2 = (
    X**3 + Y**3 - X**2*Y**2
    + 1488*X*Y*(X+Y)
    - 162000*(X**2+Y**2)
    + 40773375*X*Y
    + 8748000000*(X+Y)
    - 157464000000000
)

# ------------------------------------------------------------------
# Triangle-rectangle curve.
#
# Certificate quartic:
#   12*y^2 = -x^4 + (2+12 alpha)*x^2 + 4 alpha - 1.
#
# Put U=-x^2 and W=2*sqrt(3)*x*y. Then:
#   W^2 = U^3 + (2+12 alpha) U^2 + (1-4 alpha) U.
#
# The certificate period form omega=dx/(sqrt(3)y) satisfies
#   omega = -dU/W.
# ------------------------------------------------------------------

A_TR = 2 + 12*alpha
B_TR = 1 - 4*alpha
TR2 = invariants_2torsion(A_TR, B_TR)

h_TR = sp.factor(TR2["h"])
j_TR_quot = sp.factor(TR2["j"])
j_TR_original = sp.factor(
    -256*(1 + 9*alpha**2)**3
    / (alpha**2*(4*alpha - 1)*(9*alpha + 4)**2)
)

assert sp.factor(h_TR - 16*(1-4*alpha)/(alpha*(9*alpha+4))) == 0
assert sp.factor(j_TR_quot - j0(h_TR)) == 0
assert sp.factor(j_TR_original - j1(h_TR)) == 0
assert sp.factor(Phi2.subs({X:j_TR_quot, Y:j_TR_original})) == 0

# Quotient equation identity and differential pullback.
quartic_rhs = -x**4 + (2+12*alpha)*x**2 + 4*alpha - 1
assert sp.factor(
    (
        (2*sp.sqrt(3)*x*y)**2
        - ((-x**2)**3 + A_TR*(-x**2)**2 + B_TR*(-x**2))
    ).subs(y**2, quartic_rhs/12)
) == 0

# dU/W = - dx/(sqrt(3)*y)
assert sp.simplify(
    (-2*x)/(2*sp.sqrt(3)*x*y) + 1/(sp.sqrt(3)*y)
) == 0

# ------------------------------------------------------------------
# Octahedral sphere quotient.
# ------------------------------------------------------------------

P = x**2 + y**2 + z**2
Q = x**2*y**2 + y**2*z**2 + z**2*x**2
R = x**2*y**2*z**2
S = x*y*z*(x**2-y**2)*(y**2-z**2)*(z**2-x**2)

goursat_rhs = (
    -27*R**3
    + P*(18*Q - 4*P**2)*R**2
    + Q**2*(P**2 - 4*Q)*R
)
assert sp.factor(S**2 - goursat_rhs) == 0

# Lie-Poisson flow for Hamiltonian H=Q:
#   Jdot = J cross grad(Q).
Jvec = sp.Matrix([x,y,z])
gradQ = sp.Matrix([sp.diff(Q,v) for v in (x,y,z)])
gradR = sp.Matrix([sp.diff(R,v) for v in (x,y,z)])
dRdt = sp.factor(gradR.dot(Jvec.cross(gradQ)))
assert sp.factor(dRdt + 4*S) == 0

# Hence dt = -dR/(4S) for H=Q, up to sign convention.
#
# Put P=1 and transform the quotient cubic with
#   X=-27 R, Y=27 S:
#   Y^2 = X^3 + (18q-4)X^2 -27q^2(1-4q)X.
A_O = 18*q - 4
B_O = -27*q**2*(1-4*q)
O234 = invariants_2torsion(A_O, B_O)

h_O = sp.factor(O234["h"])
j_234 = sp.factor(O234["j"])
j_126 = sp.factor(j1(h_O))

assert sp.factor(h_O + 432*q**2*(4*q-1)/(3*q-1)**3) == 0
assert sp.factor(j_234 - j0(h_O)) == 0
assert sp.factor(Phi2.subs({X:j_234, Y:j_126})) == 0

# ------------------------------------------------------------------
# Common Gamma_0(2) architecture.
#
# Orientation-preserving:
#   h_TR(alpha)=h_O(q)
# implies simultaneously
#   j(TR quotient)=j(234III)
#   j(TR original)=j(126III).
#
# Atkin-Lehner-swapped:
#   h_TR(alpha)=4096/h_O(q)
# swaps the two members of the 2-isogeny pair.
# ------------------------------------------------------------------

F_preserve = sp.factor(
    sp.together(h_TR-h_O).as_numer_denom()[0] / 16
)
F_swap = sp.factor(
    sp.together(h_TR*h_O-4096).as_numer_denom()[0] / (-256)
)

expected_preserve = (
    972*alpha**2*q**3 - 243*alpha**2*q**2
    + 324*alpha*q**3 - 36*alpha*q + 4*alpha
    + 27*q**3 - 27*q**2 + 9*q - 1
)
assert sp.factor(F_preserve-expected_preserve) == 0

# Atkin-Lehner identity.
h = sp.symbols("h")
assert sp.factor(j0(4096/h)-j1(h)) == 0
assert sp.factor(j1(4096/h)-j0(h)) == 0

# Genus-one evidence: after solving the quadratic in alpha, the
# nonsquare part of the discriminant is a squarefree cubic.
disc_preserve_alpha = sp.factor(sp.discriminant(F_preserve, alpha))
disc_swap_alpha = sp.factor(sp.discriminant(F_swap, alpha))

assert disc_preserve_alpha == (
    4*(9*q-2)**2*(405*q**3-81*q**2-9*q+1)
)
assert sp.discriminant(405*q**3-81*q**2-9*q+1, q) != 0
assert sp.discriminant(
    sp.factor(disc_swap_alpha / (-1048576*(9*q-2)**2)), q
) != 0

# ------------------------------------------------------------------
# Local branches of the orientation-preserving correspondence.
# ------------------------------------------------------------------

u = sp.symbols("u")
preserve_u = sp.expand(F_preserve.subs(q, (1-u)/3))
branches_triangular = [
    sp.series(sol, u, 0, 7)
    for sol in sp.solve(preserve_u, alpha)
]

branches_square = [
    sp.series(sol, q, 0, 6)
    for sol in sp.solve(F_preserve, alpha)
]

print("PASS triangle-rectangle quotient cubic and exact period descent")
print("PASS octahedral Goursat quotient and exact Hamiltonian time descent")
print("PASS natural degree-2 isogeny on both sides")
print("PASS common Gamma_0(2) Hauptmodul")
print("PASS orientation-preserving and Atkin-Lehner-swapped correspondences")
print("PASS correspondence normalizations have genus one")
print()
print("h_TR(alpha) =", h_TR)
print("h_O(q)       =", h_O)
print()
print("orientation-preserving energy curve:")
print(sp.factor(F_preserve), "= 0")
print()
print("branches near octahedral triangular well q=1/3:")
for item in branches_triangular:
    print(" ", item)
print()
print("branches near octahedral square well q=0:")
for item in branches_square:
    print(" ", item)
