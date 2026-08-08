# ALG-008: general even sphere curves and the quartic factory

## Input class

```text
H = H(X,Y,Z),
X=Jx^2, Y=Jy^2, Z=Jz^2,
X+Y+Z=1.
```

`H` is even in each angular-momentum coordinate.  "Quartic" means that `H`
has total degree at most two in `(X,Y,Z)`, equivalently degree at most four in
`(Jx,Jy,Jz)`.

## Algebraic chart

Choose the `Jz` axis and put

```text
u = Jz^2,
v = cos(phi)^2,
X = (1-u)*v,
Y = (1-u)*(1-v),
Z = u,
F(u,v,alpha) = H(X,Y,Z)-alpha,
y^2 = u*v*(1-v).
```

The oriented period differential is

```text
tau = -dv/(4*y*F_u).
```

This follows from `lambda=Jz`, `dphi=-dv/(2*sqrt(v(1-v)))`, and
`H_lambda=2*lambda*F_u`.

## Exact derivations on the complete intersection

At fixed `v`, energy differentiation is

```text
u_alpha = 1/F_u,
y_alpha = v*(1-v)/(2*y*F_u),
D_alpha = partial_alpha + u_alpha*partial_u + y_alpha*partial_y.
```

Along the energy curve,

```text
u_v = -F_v/F_u,
y_v = (u_v*v*(1-v)+u*(1-2*v))/(2*y),
D_v = partial_v + u_v*partial_u + y_v*partial_y.
```

Both derivations preserve the ideal

```text
I = <F, y^2-u*v*(1-v)>.
```

## Parallel inductive/reductive program

```text
FOR each critical point and regular incident cycle:
  1. choose the axis/chart fixed by the critical-point and symmetry data
  2. generate period values or a local action series
  3. guess the smallest operator A=sum a_k(alpha) D_alpha^k
  4. construct tau, D_alpha(tau), ..., D_alpha^r(tau)
  5. choose Xi=P/[y^(2r-1)*F_u^(2r-1)] with a growing finite P support
  6. reduce A(tau)-D_v(Xi) modulo I
  7. solve the exact coefficient nullspace
  8. reconstruct and verify the unreduced rational identity modulo I
  9. compare all critical-point series under the same operator
```

## Showcase order

1. symmetric top (degenerate elementary control);
2. asymmetric top (Chapter 4 order-two operator);
3. octahedral quartic `2*(X^2+Y^2+Z^2)`;
4. rotated/scaled versions of 1--3;
5. every quartic coefficient-support stratum;
6. dense general quartics.

The tetrahedral showcase is cubic in `J` and is not even in each `J_i`.  The
icosahedral showcase contains sign-sensitive degree-six terms.  They remain
important sphere-curve tests, but are outside this first even-quartic factory.

## Exhaustive quartic parameterization

Before restriction to `X+Y+Z=1`, use

```text
c0 + cx*X + cy*Y + cz*Z
   + cxx*X^2 + cyy*Y^2 + czz*Z^2
   + cxy*X*Y + cyz*Y*Z + czx*Z*X.
```

Because adding a multiple of `X+Y+Z-1` changes no sphere curve, catalog both
the raw ten coefficients and a gauge-fixed six-coefficient representative after
setting `Z=1-X-Y`.  Tests must sample strata, not merely random dense points:
linear, diagonal quadratic, reflection-enhanced, factored/degenerate, and fully
asymmetric dense representatives.

