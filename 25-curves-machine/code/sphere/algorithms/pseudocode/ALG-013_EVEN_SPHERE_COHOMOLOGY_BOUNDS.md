# ALG-013 — Even-sphere cohomology bounds and exact reduction

## Degree bound

**Input:** an even Hamiltonian `H(Jx^2,Jy^2,Jz^2)` of degree `d` in the squared variables.

1. Put `X=Jx^2`, `Y=Jy^2`, `Z=Jz^2` and impose `X+Y+Z=L^2`.
2. Form the quotient curve
   `H(X,Y,Z)=alpha`, `q^2=XYZ`.
3. Under smoothness and transverse-intersection hypotheses, count `4d` branch points of the double cover of the degree-`d` plane curve.
4. Apply Riemann--Hurwitz:
   `g = 2*((d-1)*(d-2)/2)-1+2d = d^2-d+1`.
5. Allocate at most `2g=2d^2-2d+2` derivatives before declaring generic cohomological closure failure.

This bounds derivative order. It does **not** guess the coefficient degree in `alpha` or the support required by a particular polynomial primitive.

## Exact hyperelliptic reduction

When a symmetry quotient or rational parametrization gives `z^2=P(x,alpha)`:

```text
forms[0] := dx/(4z)
for k = 0,...,2g:
    differentiate forms[k] with respect to alpha
    Hermite-reduce all higher odd powers of z
    reduce the polynomial numerator modulo exact x-derivatives d(Qz)
    store the resulting vector in the basis dx/z,...,x^(deg(P)-2)dx/z
find the first exact null relation among stored vectors over Q(alpha)
reconstruct the sum of all discarded exact primitives
clear polynomial and integer content simultaneously in operator and primitive
verify sum A_k(alpha) D_alpha^k(omega) = d_x Xi exactly
```

If no relation occurs by `2g`, report a violated hypothesis, implementation defect, or an insufficient coefficient field—not “increase the primitive degree by one.”
