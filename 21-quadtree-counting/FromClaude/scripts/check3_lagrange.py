from sympy import symbols, series, Rational, O, Poly, factorial

u = symbols('u')
D = 1 - 6*u - 4*u**2 - u**3

# q[n] = (1/n) * [u^(n-1)] D(u)^(-n)   (Lagrange inversion / residue form)
def q_lagrange(n, order=25):
    Dinv_n = (D**(-n)).series(u, 0, order).removeO()
    coeff = Dinv_n.coeff(u, n-1)
    return Rational(coeff, n)

vals = [q_lagrange(n) for n in range(1,6)]
print("Lagrange/coefficient-form q[1..5]:", vals)
print("Claimed:                          ", [1,6,76,1201,21252])
