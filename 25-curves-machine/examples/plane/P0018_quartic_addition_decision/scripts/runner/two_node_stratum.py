#!/usr/bin/env python3
"""Symbolic generic two-node stratum inside the maximal plane quartic."""
import sympy as sp, json

t,k=sp.symbols('t k')
u,v,w,r,s,A,B,C=sp.symbols('u v w r s A B C')
Q=u+v*t+w*t**2
L=r+s*t
H2=A+B*t+C*t**2
# H4=k Q^2, H3=Q L in p=1 chart.
root=sp.symbols('root')
Qp=sp.diff(Q,t)
# At Q(root)=0, tangent cone coefficients in local coordinates xi,z.
a=sp.expand(k*Qp.subs(t,root)**2)
b=sp.expand(Qp.subs(t,root)*L.subs(t,root))
c=sp.expand(H2.subs(t,root))
disc=sp.factor(b**2-4*a*c)
out={
 'maximal_form':'H=H4+H3+H2+H1+H0 with H4=k*Q2^2 and H3=Q2*L1',
 'Q2_chart':str(Q),'L1_chart':str(L),'H2_chart':str(H2),
 'tangent_cone':f'({a})*xi^2 + ({b})*xi*z + ({c})*z^2',
 'tangent_discriminant':str(disc),
 'generic_conditions':[
   'disc(Q2) != 0 (two distinct directions at infinity)',
   'L1(root)^2 - 4*k*H2(root) != 0 at both roots (ordinary nodes)',
   'generic energy alpha avoids affine critical values'
 ],
 'conclusion':'two ordinary nodes, total delta=2, geometric genus=1',
 'rational_branch_test':'At a K-rational root of Q2, a normalization branch is K-rational when L1(root)^2-4*k*H2(root) is a square in K.'
}
print(json.dumps(out,indent=2))
