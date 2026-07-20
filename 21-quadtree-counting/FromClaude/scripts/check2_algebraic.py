from sympy import symbols, series, solve, Poly, O, sqrt, simplify, Rational

x = symbols('x')
# Q = x + 6Q^2 + 4Q^3 + Q^4, solve for Q as power series in x via iteration
N = 8
Q = 0
for _ in range(N+3):
    Q = (x + 6*Q**2 + 4*Q**3 + Q**4)
    Q = Q.series(x, 0, N+2).removeO()

Qs = Q.series(x,0,N+2)
print("Q series:", Qs)

A = 1 + Q
A = A.series(x,0,N+2)
print("A series:", A)

# check algebraic equation A^4 - 5A + 4 + x = 0 (as formal power series, order-by-order)
Afull = (1+Q)
eq = Afull**4 - 5*Afull + 4 + x
eq_series = eq.series(x,0,N).removeO()
print("A^4-5A+4+x series (should be 0 up to computed order):", simplify(eq_series))
