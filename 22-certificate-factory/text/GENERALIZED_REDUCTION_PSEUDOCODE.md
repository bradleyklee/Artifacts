# Generalized contour-reduction plan

This is the q3 paper algorithm with its actual invariants exposed. It is an
analysis specification, not yet a family-wide computation.

## Polynomial term-shift kernel

Input:

- a squarefree polynomial `rho(u)` of degree `q`, with a simple zero at zero;
- a fixed numerator seed `s(u)` of degree below `q`;
- `H_n(u)=s(u)/(n*rho(u)^n)`.

```text
Function BuildUV(rho)
1: Build G for (a,b) -> rho*a-rho'*b,
   using deg(a),deg(b)<q and output degrees 0..2q-1.
2: Invert G exactly.
3: Let E embed degrees 0..q-1 into degrees 0..2q-1.
4: Split G^(-1)*E vertically as U,V.
5: Return U,V,J, where J differentiates coefficient vectors.

Function Lower(w,m)
1: Return U*w-(1/m)*J*V*w;
2: Record (V*w)/(m*rho^m) as the exact-differential contribution.

Function ShiftColumn(seed,r)
1: w <- coefficient vector of seed;
2: For j from r down to 1:
3:     w <- Lower(w,n+j-1);
4: Return (n/(n+r))*w.

Function TermShiftRelation(rho,seed)
1: {U,V,J} <- BuildUV(rho);
2: Build q columns ShiftColumn(seed,r), r=0..q-1.
3: Delete the exact-differential row and find the primitive exact nullvector.
4: Accumulate every recorded V-contribution with the nullvector weights.
5: Verify the cleared telescoping identity exactly.
```

For the 18 primary core cases, `seed=1`. For A120589 and A120591,
`seed=(1+d*u)^(p-1)`. Thus all 20 core cases use the same mathematics as q3;
the implementation only needs `rho` and `seed` as data instead of deriving
them from a normalized q.

## Rational descendants

Write

```text
H_n(u)=h(u)^n/(n*p(u)^n),  rho(u)=p(u)/h(u).
```

The shift ratio contains `h(u)^r/p(u)^r`, and

```text
d_u log H_n = n*(h'/h-p'/p).
```

Therefore the one-factor term-shift `G` is not valid unchanged. A future
term-shift implementation needs a two-factor Hermite lowering identity.

The direct generating-function kernel is simpler:

```text
Phi(x,u)=h(u)/(p(u)-x*h(u)).
```

Its denominator `g_x(u)=p(u)-x*h(u)` is polynomial in `u`. Apply the q3
`G_x/U_x/V_x` derivative-reduction algorithm to `g_x` first, retaining the
fixed numerator `h`. This should produce a linear ODE before attempting the
harder term-shift certificate.
