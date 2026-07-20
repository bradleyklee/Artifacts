from sympy import symbols, diff, together, expand, fraction, Rational, nsimplify

u = symbols('u')

D = 1 - 6*u - 4*u**2 - u**3

def Hn(m):
    return 1/(m * u**m * D**m)

def Pvals(n):
    P0 = -8*(4*n+5)*(2*n+1)*(4*n-1)
    P1 = -64*(n+1)*(48*n**2+96*n+43)
    P2 = -6144*(2*n+3)*(n+2)*(n+1)
    P3 = 491*(n+3)*(n+2)*(n+1)
    return [P0,P1,P2,P3]

N_by_n_degree = {
  2: [-491, 6396, 204, -8524, -5136, 2784, 4496, 2304, 576, 64],
  1: [-491, 6648, -948, -11872, -6228, 5784, 7988, 4032, 1008, 112],
  0: [0, 0, 40, -440, 640, 2960, 2960, 1440, 360, 40],
}
def R_of_n(n):
    N_nu = 0
    for d, coeffs in N_by_n_degree.items():
        for e, c in enumerate(coeffs):
            N_nu += c * (n**d) * u**e
    return N_nu / (u**2 * (u**3+4*u**2+6*u-1)**2)

all_ok = True
for n in range(1, 9):
    P = Pvals(n)
    lhs = sum(P[r]*Hn(n+r) for r in range(4))
    rhs = diff(R_of_n(n)*Hn(n), u)
    diff_expr = together(lhs - rhs)
    num, den = fraction(diff_expr)
    num_e = expand(num)
    ok = (num_e == 0)
    all_ok = all_ok and ok
    print(f"n={n}: identity holds exactly = {ok}")

print()
print("ALL n tested hold:", all_ok)
