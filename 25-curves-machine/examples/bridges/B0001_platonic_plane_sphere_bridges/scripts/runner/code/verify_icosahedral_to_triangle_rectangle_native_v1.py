#!/usr/bin/env python3
import sympy as sp
beta,z,alpha,x,y,p,q=sp.symbols("beta z alpha x y p q")
P=135*beta**3+115*beta**2+5*beta+1
N=beta**2*(1-beta)**5*(27*beta+5)**3
F=N*(4-3*z)**3-4*P**3*z**2*(1-z)
G=z*(1+6*alpha)**2-4*alpha*(4+9*alpha)
H=p**2+q**2+q**3-3*p**2*q+sp.Rational(1,4)*(q**2-3*p**2)**2
A=lambda U:(3*U**2+6*U+4)/12
B=lambda U:U*(3*U+2)/6
u=x-1
v=(y-B(u))/(2*A(u))
qq=(u+v)/2
pp=(v-u)/(2*sp.sqrt(3))
Q=12*y**2+x**4-(2+12*alpha)*x**2-4*alpha+1
num,den=sp.together(H.subs({p:pp,q:qq})-alpha).as_numer_denom()
quo,rem=sp.div(sp.Poly(num,y),sp.Poly(Q,y))
assert sp.factor(rem.as_expr())==0
print("PASS direct native tower")
print("F_icosahedral =",sp.factor(F))
print("G_triangle_rectangle =",sp.factor(G))
print("(2H-alpha)/quartic =",sp.factor(quo.as_expr()/den))
