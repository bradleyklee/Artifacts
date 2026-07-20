from sympy import symbols, diff, simplify, together, expand, fraction, Rational, factor, cancel

n, u = symbols('n u')

D = 1 - 6*u - 4*u**2 - u**3
Dp = diff(D, u)

P0 = -8*(4*n+5)*(2*n+1)*(4*n-1)
P1 = -64*(n+1)*(48*n**2+96*n+43)
P2 = -6144*(2*n+3)*(n+2)*(n+1)
P3 = 491*(n+3)*(n+2)*(n+1)
P = [P0,P1,P2,P3]

N_by_n_degree = {
  2: [-491, 6396, 204, -8524, -5136, 2784, 4496, 2304, 576, 64],
  1: [-491, 6648, -948, -11872, -6228, 5784, 7988, 4032, 1008, 112],
  0: [0, 0, 40, -440, 640, 2960, 2960, 1440, 360, 40],
}
N_nu = 0
for d, coeffs in N_by_n_degree.items():
    for e, c in enumerate(coeffs):
        N_nu += c * n**d * u**e
R = N_nu / (u**2 * (u**3+4*u**2+6*u-1)**2)

# H_{n+r}/H_n = [n/(n+r)] * u^(-r) * D^(-r)   -- r is a CONCRETE small integer (0,1,2,3),
# so no symbolic exponent combination is ever needed here.
def ratio(r):
    if r == 0:
        return 1
    return Rational(1) * (n) / (n + r) * u**(-r) * D**(-r)

# H_n'/H_n = d/du log H_n = -n*(1/u + D'/D)
Hn_logderiv = -n*(1/u + Dp/D)

lhs = sum(P[r]*ratio(r) for r in range(4))
rhs = diff(R, u) + R*Hn_logderiv

expr = together(lhs - rhs)
num, den = fraction(expr)
num_expanded = expand(num)
print("Numerator is identically zero (fully symbolic in n AND u)?", num_expanded == 0)
if num_expanded != 0:
    print("Residual (first 500 chars):", str(num_expanded)[:500])

# Sanity: confirm lhs and rhs are each nontrivial (not accidentally 0=0),
# and cross-check by substituting several concrete n values into this
# symbolic derivation and comparing against the earlier fixed-n cross-multiplication check.
from sympy import Rational as Rat
print()
print("Sanity check: lhs, rhs nonzero individually at n=5:")
print(" lhs(n=5) simplifies to:", simplify(lhs.subs(n,5)) != 0)
print(" rhs(n=5) simplifies to:", simplify(rhs.subs(n,5)) != 0)

print()
print("Cross-check against earlier fixed-n numerator-zero test, n=1..10:")
for nn in range(1, 11):
    val = together(lhs - rhs).subs(n, nn)
    val = simplify(val)
    print(f"  n={nn}: identity residual = {val}  (zero = {val == 0})")
