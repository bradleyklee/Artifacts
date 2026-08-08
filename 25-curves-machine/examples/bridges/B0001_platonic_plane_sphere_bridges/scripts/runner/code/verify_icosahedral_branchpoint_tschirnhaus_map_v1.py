#!/usr/bin/env python3
import sympy as sp

beta,z,R = sp.symbols("beta z R")

P = 135*beta**3 + 115*beta**2 + 5*beta + 1
N = beta**2*(1-beta)**5*(27*beta+5)**3
Q = 729*beta**5 + 5130*beta**4 + 1870*beta**3 + 480*beta**2 - 15*beta - 2
U = 531441*beta**9 - 2086398*beta**8 + 5089149*beta**7 - 2554767*beta**6 + 891211*beta**5 + 347561*beta**4 - 97793*beta**3 - 23261*beta**2 + 8*beta + 1
V = 2834352*beta**9 - 17025795*beta**8 + 20685375*beta**7 - 11753325*beta**6 + 1314795*beta**5 + 2556001*beta**4 - 477155*beta**3 - 211455*beta**2 - 19895*beta - 50

A = -sp.Rational(9,4)*Q/P
B = (7*beta+1)*U/(P*Q)
C = -beta*V/(P*Q)

fR = (
    -R**3 +(4-65*beta)*R**2
    +beta*(720*beta**2+200-795*beta)*R
    +500*beta**2-2275*beta**3+3440*beta**4-1728*beta**5
)

Fz = sp.Poly(
    sp.expand(N*(4-3*z)**3-4*P**3*z**2*(1-z)),
    z,
    domain=sp.QQ.frac_field(beta),
)

image = A*z**2+B*z+C
num = sp.together(fR.subs(R,image)).as_numer_denom()[0]
rem = sp.Poly(num,z,domain=sp.QQ.frac_field(beta)).rem(Fz)

assert rem.is_zero
print("PASS exact quadratic Tschirnhaus map")
print("R =", sp.factor(image))
