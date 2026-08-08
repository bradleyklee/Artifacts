#!/usr/bin/env python3
import sympy as sp

R,e1,e2,e3,k,b,S=sp.symbols("R e1 e2 e3 k b S")
a=b*(1+k)/(1-k)

D=(1-k)*R-(e1-k*e2)
x=b*((1+k)*R-(e1+k*e2))/D
y=b*(a-b)*(e2-e1)/(sp.sqrt(3)*sp.sqrt(e3-e2))*S/D**2

res=sp.together(
    12*y**2+x**4-(a**2+b**2)*x**2+a**2*b**2
)

e3_sub=(k**2*e2-e1)/(k**2-1)

res=res.subs(S**2,-(R-e1)*(R-e2)*(R-e3))
res=res.subs(e3,e3_sub)
res=sp.factor(sp.together(res))

assert res==0
print("PASS exact generic cubic-to-even-quartic identity")
