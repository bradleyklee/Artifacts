from sympy import symbols, series, diff, simplify, Rational, O

x = symbols('x')
N = 16
Q = 0
for _ in range(N+3):
    Q = (x + 6*Q**2 + 4*Q**3 + Q**4)
    Q = Q.series(x, 0, N+2).removeO()

A = (1+Q).series(x,0,N+2).removeO()

dA = diff(A, x, 1)
d2A = diff(A, x, 2)
d3A = diff(A, x, 3)

lhs = (256*x**3+3072*x**2+12288*x-491)*d3A + (1152*x**2+9216*x+18432)*d2A + (688*x+2752)*dA - 40*A

lhs_series = lhs.series(x, 0, N-4).removeO()
print("Differential equation residual series (should be 0):")
print(simplify(lhs_series))
