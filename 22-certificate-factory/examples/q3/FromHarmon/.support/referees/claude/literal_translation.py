"""
Direct SymPy transcription of the Q3(N) pseudocode.
Every function name below corresponds 1:1 to a function in the pseudocode.
No shortcut/closed-form equation is used anywhere -- P0,P1,P2, the a[k],
and the ODE are all produced purely by running this machinery on U,V,J,e.
"""

from sympy import (symbols, Matrix, Rational, Integer, simplify, expand,
                    cancel, together, fraction, gcd, lcm, factor, Poly, diff)

n, x = symbols('n x')


# ---------------------------------------------------------------------
# Function Lower(U,V,J,w,m)
#   1: b <- V*w
#   2: Return U*w - (J*b)/m
# ---------------------------------------------------------------------
def Lower(U, V, J, w, m):
    b = V * w
    return U * w - (J * b) / m


# ---------------------------------------------------------------------
# Function Normalize3(p0,p1,p2)
#   clears denominators, divides by poly GCD, clears coefficient
#   denominators, divides by integer coefficient GCD, fixes sign,
#   and factors.
# ---------------------------------------------------------------------
def Normalize3(p0, p1, p2):
    exprs = [p0, p1, p2]

    # 1: d <- LCM(Denom(Together(p0)), Denom(Together(p1)), Denom(Together(p2)))
    denoms = [fraction(together(e))[1] for e in exprs]
    d = denoms[0] * denoms[1] * denoms[2]          # (product suffices as a common denominator)

    # 2: {q0,q1,q2} <- Expand(d*{p0,p1,p2})
    q = [expand(cancel(d * e)) for e in exprs]

    # 3: h <- PolynomialGCD(q0,q1,q2); {q0,q1,q2} <- {q0/h,q1/h,q2/h}
    h = gcd(gcd(q[0], q[1]), q[2])
    if h == 0:
        h = 1
    q = [expand(cancel(qq / h)) for qq in q]

    # 4: c <- LCM of all coefficient denominators in q0,q1,q2
    c = 1
    for qq in q:
        poly = Poly(qq, n)
        for coeff in poly.all_coeffs():
            if coeff != 0:
                c = lcm(c, fraction(coeff)[1])
    # {q0,q1,q2} <- Expand(c*{q0,q1,q2})
    q = [expand(c * qq) for qq in q]

    # 6: g <- GCD of all integer coefficients; {q0,q1,q2} <- {q0/g,q1/g,q2/g}
    allcoeffs = []
    for qq in q:
        poly = Poly(qq, n)
        allcoeffs += [cf for cf in poly.all_coeffs() if cf != 0]
    g = allcoeffs[0]
    for cf in allcoeffs[1:]:
        g = gcd(g, cf)
    if g == 0:
        g = 1
    q = [expand(qq / g) for qq in q]

    # 7: If LeadingCoefficient(q2,n) < 0, negate all three
    lead = Poly(q[2], n).LC()
    if lead < 0:
        q = [-qq for qq in q]

    # 8: Return Factor({q0,q1,q2})
    return [factor(qq) for qq in q]


# ---------------------------------------------------------------------
# Function Cancel3(X)     (X has two rows, three columns)
# ---------------------------------------------------------------------
def Cancel3(X):
    p0 = X[0, 1] * X[1, 2] - X[0, 2] * X[1, 1]     # cancel columns 2,3
    p1 = X[0, 2] * X[1, 0] - X[0, 0] * X[1, 2]     # cancel columns 1,3
    p2 = X[0, 0] * X[1, 1] - X[0, 1] * X[1, 0]     # cancel columns 1,2
    return Normalize3(p0, p1, p2)


# ---------------------------------------------------------------------
# Function Apply2(P,r)
#   Write P(n) = a*n^2 + b*n + c
#   Return a*(x^2*A'' + (1-2r)*x*A' + r^2*A) + b*(x*A' - r*A) + c*A
# ---------------------------------------------------------------------
App, Ap, A = symbols("App Ap A")   # stand-ins for A'', A', A

def Apply2(P, r):
    coeffs = Poly(P, n).all_coeffs()
    while len(coeffs) < 3:                          # pad up to quadratic
        coeffs = [0] + coeffs
    a_, b_, c_ = coeffs[-3], coeffs[-2], coeffs[-1]
    return (a_ * (x**2 * App + (1 - 2*r) * x * Ap + r**2 * A)
            + b_ * (x * Ap - r * A)
            + c_ * A)


# ---------------------------------------------------------------------
# Function MakeODE(P0,P1,P2)
# ---------------------------------------------------------------------
def MakeODE(P0, P1, P2):
    # 1: L <- x^2*Apply2(P0,0) + x*Apply2(P1,1) + Apply2(P2,2)
    L = x**2 * Apply2(P0, 0) + x * Apply2(P1, 1) + Apply2(P2, 2)

    # 2: L <- Collect(Expand(L/x^2), {A'',A',A})     (division is exact)
    L = expand(L / x**2)

    # 3: Factor each polynomial multiplying A'', A', and A
    cApp = factor(L.coeff(App, 1))
    cAp = factor(L.coeff(Ap, 1))
    cA = factor(L.coeff(A, 1))

    # 4: If the coefficient of A'' leads negatively in x, set L <- -L
    if Poly(cApp, x).LC() < 0:
        cApp, cAp, cA = -cApp, -cAp, -cA

    # 5: Return L
    return cApp, cAp, cA


# ---------------------------------------------------------------------
# Function Q3(N)
# ---------------------------------------------------------------------
def Q3(N):
    assert N >= 2

    # 2-4: given data
    U = Rational(1, 13) * Matrix([[153, 24, 3], [72, 9, 6], [0, 0, 0]])
    V = Rational(1, 13) * Matrix([[-13, 0, 0], [75, 11, 3], [24, 3, 2]])
    J = Matrix([[0, 1, 0], [0, 0, 2], [0, 0, 0]])
    e = Matrix([1, 0, 0])

    # 5-6: c0, c1, c2
    c0 = e
    c1 = simplify((n / (n + 1)) * Lower(U, V, J, e, n))
    c2 = simplify((n / (n + 2)) * Lower(U, V, J, simplify(Lower(U, V, J, e, n + 1)), n))

    # 7: X <- first two rows of MatrixFromColumns(c0,c1,c2)
    X = simplify(Matrix.hstack(c0, c1, c2)[0:2, :])

    # 8: {P0,P1,P2} <- Cancel3(X); Assert Simplify(X*{P0,P1,P2}^T)=0
    P0, P1, P2 = Cancel3(X)
    assert simplify(X * Matrix([P0, P1, P2])) == Matrix([0, 0])

    # 9-10: bootstrap
    a = {0: Integer(1)}
    a[1] = Rational(1, 4 - 3 * a[0]**2)
    a[2] = Rational(3 * a[0] * a[1]**2, 4 - 3 * a[0]**2)

    # 11-12: recurrence
    for k in range(1, N - 1):
        P0k, P1k, P2k = P0.subs(n, k), P1.subs(n, k), P2.subs(n, k)
        a[k + 2] = simplify((-P0k * a[k] - P1k * a[k + 1]) / P2k)

    # 13: S <- Sum(a[k]*x^k); Assert Coeffs(4*S-3-x-S^3, 0..N)=0
    S = sum(a[k] * x**k for k in sorted(a))
    check_cubic = Poly(expand(4 * S - 3 - x - S**3), x)
    for k in range(0, N + 1):
        assert simplify(check_cubic.nth(k)) == 0

    # 14: ODE <- MakeODE(P0,P1,P2)
    cApp, cAp, cA = MakeODE(P0, P1, P2)

    # 15: Assert Coeffs(Substitute(ODE,...), 0..N-2)=0
    Sp, Spp = diff(S, x), diff(S, x, 2)
    ode_check = Poly(expand(cApp * Spp + cAp * Sp + cA * S), x)
    for k in range(0, N - 1):
        assert simplify(ode_check.nth(k)) == 0

    # 16: Return {a[0..N], Factor({P0,P1,P2}), ODE=0}
    return {
        "a": a,
        "P0": P0, "P1": P1, "P2": P2,
        "ODE": (cApp, cAp, cA),
    }


if __name__ == "__main__":
    result = Q3(15)
    print("P0 =", result["P0"])
    print("P1 =", result["P1"])
    print("P2 =", result["P2"])
    print()
    for k in sorted(result["a"]):
        print(f"a[{k}] =", result["a"][k])
    print()
    cApp, cAp, cA = result["ODE"]
    print("ODE: (%s) A'' + (%s) A' + (%s) A = 0" % (cApp, cAp, cA))
