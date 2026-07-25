#!/usr/bin/env python3
"""
Q3 Algorithm - Literal implementation of the pseudocode from
Harm.On.ica S-O-L's "Ternatree counting" derivation.

This script computes the ternary-tree sequence A120590 by:
  1. Building the reduction matrix from plum-root data
  2. Canceling columns to obtain the recurrence polynomials
  3. Iterating the dawn-loop to generate terms
  4. Verifying against the cubic and differential equations

Run: python3 q3_algorithm.py
"""

from sympy import *

x, n, A_sym, Ap_sym, App_sym = symbols('x n A Ap App')


def Lower(U, V, J, w, m):
    """
    Function Lower(U,V,J,w,m)
    1: b <- V*w;
    2: Return U*w-(J*b)/m;   (run the quotient rule backward)
    """
    b = V * w
    return U * w - (J * b) / m


def Normalize3(p0, p1, p2):
    """
    Function Normalize3(p0,p1,p2)
    1: d <- LCM(Denom(Together(p0)),Denom(Together(p1)),Denom(Together(p2)));
    2: {q0,q1,q2} <- Expand(d*{p0,p1,p2});
    3: h <- PolynomialGCD(q0,q1,q2);  {q0,q1,q2} <- {q0/h,q1/h,q2/h};
    4: c <- LCM of all coefficient denominators in q0,q1,q2;
    5: {q0,q1,q2} <- Expand(c*{q0,q1,q2});
    6: g <- GCD of all integer coefficients;  {q0,q1,q2} <- {q0/g,q1/g,q2/g};
    7: If LeadingCoefficient(q2,n)<0, negate all three;
    8: Return Factor({q0,q1,q2});
    """
    # Step 1
    d = lcm([
        together(p0).as_numer_denom()[1],
        together(p1).as_numer_denom()[1],
        together(p2).as_numer_denom()[1]
    ])
    # Step 2: use cancel() to clear denominators properly
    q0, q1, q2 = cancel(d * p0), cancel(d * p1), cancel(d * p2)
    # Step 3
    h = gcd(Poly(q0, n), gcd(Poly(q1, n), Poly(q2, n)))
    q0 = Poly(q0, n).div(h)[0].as_expr()
    q1 = Poly(q1, n).div(h)[0].as_expr()
    q2 = Poly(q2, n).div(h)[0].as_expr()
    # Step 4
    def coeff_denom(expr):
        if expr == 0:
            return 1
        coeffs = Poly(expr, n).all_coeffs()
        dens = [c.q for c in coeffs if c.is_Rational and c.q != 1]
        return lcm(dens) if dens else 1
    c = lcm([coeff_denom(q0), coeff_denom(q1), coeff_denom(q2)])
    # Step 5
    q0, q1, q2 = expand(c * q0), expand(c * q1), expand(c * q2)
    # Step 6
    def int_gcd(expr):
        if expr == 0:
            return 1
        coeffs = Poly(expr, n).all_coeffs()
        g = 0
        for c in coeffs:
            if c.is_Integer:
                g = gcd(g, abs(int(c)))
        return g if g != 0 else 1
    g = gcd(int_gcd(q0), gcd(int_gcd(q1), int_gcd(q2)))
    q0 = Poly(q0, n).div(Poly(g, n))[0].as_expr()
    q1 = Poly(q1, n).div(Poly(g, n))[0].as_expr()
    q2 = Poly(q2, n).div(Poly(g, n))[0].as_expr()
    # Step 7
    if Poly(q2, n).LC() < 0:
        q0, q1, q2 = -q0, -q1, -q2
    # Step 8
    return factor(q0), factor(q1), factor(q2)


def Cancel3(X):
    """
    Function Cancel3(X)  (X has two rows, three columns)
    1: p0 <- X[1,2]*X[2,3]-X[1,3]*X[2,2];   (cancel columns 2 and 3)
    2: p1 <- X[1,3]*X[2,1]-X[1,1]*X[2,3];   (cancel columns 1 and 3)
    3: p2 <- X[1,1]*X[2,2]-X[1,2]*X[2,1];   (cancel columns 1 and 2)
    4: Return Normalize3(p0,p1,p2);
    """
    p0 = X[0, 1] * X[1, 2] - X[0, 2] * X[1, 1]
    p1 = X[0, 2] * X[1, 0] - X[0, 0] * X[1, 2]
    p2 = X[0, 0] * X[1, 1] - X[0, 1] * X[1, 0]
    return Normalize3(p0, p1, p2)


def Apply2(P, r):
    """
    Function Apply2(P,r)
    1: Write P(n)=a*n^2+b*n+c;
    2: Return a*(x^2*A''+(1-2*r)*x*A'+r^2*A)+b*(x*A'-r*A)+c*A;
    """
    coeffs = Poly(P, n).all_coeffs()
    a, b, c = coeffs[0], coeffs[1], coeffs[2]
    return (a * (x**2 * App_sym + (1 - 2*r) * x * Ap_sym + r**2 * A_sym)
            + b * (x * Ap_sym - r * A_sym) + c * A_sym)


def MakeODE(P0, P1, P2):
    """
    Function MakeODE(P0,P1,P2)
    1: L <- x^2*Apply2(P0,0)+x*Apply2(P1,1)+Apply2(P2,2);
    2: L <- Collect(Expand(L/x^2),{A'',A',A});       (division is exact)
    3: Factor each polynomial multiplying A'', A', and A;
    4: If the coefficient of A'' leads negatively in x, set L <- -L;
    5: Return L;
    """
    L = x**2 * Apply2(P0, 0) + x * Apply2(P1, 1) + Apply2(P2, 2)
    L = collect(expand(L / x**2), [App_sym, Ap_sym, A_sym])
    coeffs_dict = L.as_coefficients_dict()
    L = sum(factor(coeffs_dict[k]) * k for k in coeffs_dict)
    app_coeff_expr = coeffs_dict.get(App_sym, 0)
    if app_coeff_expr != 0:
        lc = Poly(app_coeff_expr, x).LC()
        if lc < 0:
            L = -L
    return L


def exact_quotient(a_val, b_val):
    """Exact division with remainder check."""
    q = Rational(a_val, b_val)
    assert q.is_Integer, f"{a_val}/{b_val} is not an integer"
    return int(q)


def Q3(N):
    """
    Function Q3(N)
    1: Require N>=2;
    2: U <- (1/13)*[[153,24,3],[72,9,6],[0,0,0]];
    3: V <- (1/13)*[[-13,0,0],[75,11,3],[24,3,2]];
    4: J <- [[0,1,0],[0,0,2],[0,0,0]];  e <- [1,0,0]^T;
    5: c0 <- e;  c1 <- (n/(n+1))*Lower(U,V,J,e,n);
    6: c2 <- (n/(n+2))*Lower(U,V,J,Lower(U,V,J,e,n+1),n);
    7: X <- first two rows of MatrixFromColumns(c0,c1,c2);
    8: {P0,P1,P2} <- Cancel3(X);  Assert Simplify(X*{P0,P1,P2}^T)=0;
    9: a[0] <- 1;  a[1] <- ExactQuotient(1,4-3*a[0]^2);
    10: a[2] <- ExactQuotient(3*a[0]*a[1]^2,4-3*a[0]^2);
    11: For k <- 1 to N-2:
    12:   a[k+2] <- ExactQuotient(-P0(k)*a[k]-P1(k)*a[k+1],P2(k));
    13: S <- Sum(a[k]*x^k,k=0..N);  Assert Coeffs(4*S-3-x-S^3,0..N)=0;
    14: ODE <- MakeODE(P0,P1,P2);
    15: Assert Coeffs(Substitute(ODE,A=S,A'=S',A''=S''),0..N-2)=0;
    16: Return {a[0..N],Factor({P0,P1,P2}),ODE=0};
    """
    assert N >= 2
    U = Rational(1, 13) * Matrix([[153, 24, 3], [72, 9, 6], [0, 0, 0]])
    V = Rational(1, 13) * Matrix([[-13, 0, 0], [75, 11, 3], [24, 3, 2]])
    J = Matrix([[0, 1, 0], [0, 0, 2], [0, 0, 0]])
    e = Matrix([1, 0, 0])
    c0 = e
    c1 = (n / (n + 1)) * Lower(U, V, J, e, n)
    c2 = (n / (n + 2)) * Lower(U, V, J, Lower(U, V, J, e, n + 1), n)
    X = Matrix.hstack(c0, c1, c2)[:2, :]
    P0, P1, P2 = Cancel3(X)
    assert simplify(X * Matrix([P0, P1, P2])) == Matrix([0, 0])
    a = [0] * (N + 1)
    a[0] = 1
    a[1] = exact_quotient(1, 4 - 3 * a[0]**2)
    a[2] = exact_quotient(3 * a[0] * a[1]**2, 4 - 3 * a[0]**2)
    for k in range(1, N - 1):
        a[k + 2] = exact_quotient(
            -P0.subs(n, k) * a[k] - P1.subs(n, k) * a[k + 1],
            P2.subs(n, k)
        )
    S = sum(a[k] * x**k for k in range(N + 1))
    check = expand(4 * S - 3 - x - S**3)
    p = Poly(check, x)
    for i in range(N + 1):
        assert p.coeff_monomial(x**i) == 0
    ODE = MakeODE(P0, P1, P2)
    Sp = diff(S, x)
    Spp = diff(Sp, x)
    ode_check = ODE.subs({A_sym: S, Ap_sym: Sp, App_sym: Spp})
    p_ode = Poly(expand(ode_check), x)
    for i in range(N - 1):
        assert p_ode.coeff_monomial(x**i) == 0
    return a, [P0, P1, P2], ODE


if __name__ == "__main__":
    N = 30
    a_seq, P_polys, ODE = Q3(N)
    print("Ternatree sequence (A120590):")
    for i, v in enumerate(a_seq):
        print(f"  a[{i}] = {v}")
    print("\nRecurrence polynomials:")
    print(f"  P0(n) = {P_polys[0]}")
    print(f"  P1(n) = {P_polys[1]}")
    print(f"  P2(n) = {P_polys[2]}")
    print("\nDifferential equation:")
    print(f"  {ODE} = 0")
