from sympy import symbols, diff, simplify, factor, together, expand, Rational, Poly, fraction, powsimp, nsimplify

n, u = symbols('n u', positive=True)  # treat as positive to allow power combination rules safely for the algebraic manipulation

D = 1 - 6*u - 4*u**2 - u**3

def H(m):
    return 1/(m * u**m * D**m)

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

lhs = sum(P[r]*H(n+r) for r in range(4))
rhs = diff(R*H(n), u)

diff_expr = (lhs - rhs)
# force powsimp to combine same-base powers with symbolic exponents
diff_expr2 = powsimp(diff_expr, force=True)
diff_expr2 = together(diff_expr2)
num, den = fraction(diff_expr2)
num_expanded = expand(powsimp(num, force=True))
print("Numerator after forced power combination:")
print(num_expanded)
print()
print("Is zero?", simplify(num_expanded) == 0)
