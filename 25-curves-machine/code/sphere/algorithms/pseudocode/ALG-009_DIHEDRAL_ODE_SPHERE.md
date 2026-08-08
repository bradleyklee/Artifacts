# ALG-009: dissertation DihedralToODE adapted to sphere curves

## Source discipline

This reconstruction uses Chapter 3 prose and Algorithm 1 only.  The original
Mathematica notebook is not inspected.  Chapter 4 operators are comparison
targets after derivation, not inputs to the reducer.

## Input and normalization

```text
alpha = H(lambda,phi)
      = h1(lambda)+h2(lambda)*cos(m*phi),
lambda = J_axis.
```

Chapter 3 writes `alpha=2H`, introducing factors `1/2` in Hamilton's equations.
For the Chapter 4 sphere convention `alpha=H`, use

```text
rho = h2*h1_lambda + (alpha-h1)*h2_lambda = h2*dot(phi),
dot(lambda)^2 = -m^2*(alpha-h1-h2)*(alpha-h1+h2),
ddot(lambda) = (1/2)*partial_lambda(dot(lambda)^2),
dot(phi)=rho/h2.
```

## Period derivative tower

At fixed `phi`, implicit differentiation of `H=lambda` gives

```text
partial_alpha(lambda)=1/dot(phi)=h2/rho,
D_alpha = partial_alpha + (h2/rho)*partial_lambda.
```

If `f=1/dot(phi)=h2/rho`, the period is `T=integral f dphi`.  Relative to
`dt`, define the dissertation-style reduced densities

```text
x_n = dot(phi)*D_alpha^n(f),
x_0 = 1.
```

Then a telescoper satisfies

```text
sum_n a_n(alpha)*x_n = d_t Xi.
```

## Dissertation Hermite kernel

Put

```text
s = dot(lambda)^2,
d = degree_lambda(rho),
Delta = degree_lambda(s)-1,
deg(u) <= d+Delta-1,
deg(v) <= d-1.
```

Construct the square coefficient matrix of

```text
w = rho*u - s*(partial_lambda rho)*v.
```

If its determinant vanishes, report an ineffective extraction for this chart.
Otherwise invert and split into `U,V`.  Pole descent uses

```text
w/rho^(k+1)
 = [u-(ddot(lambda)*v+s*partial_lambda(v))/k]/rho^k
   + d_t[dot(lambda)*v/(k*rho^k)].
```

The implementation also permits direct construction of the same finite linear
system with

```text
Xi = dot(lambda)*P(lambda,alpha)/rho^(2r-1),
```

which is convenient for exact comparison with the complete-intersection route.

## Required comparisons

For every closed model:

1. derive the operator without supplying the Chapter 4 target;
2. verify the exact `t`-derivative identity;
3. normalize and compare operators;
4. transform the Dihedral primitive into the `(u,v,y)` field;
5. subtract the general-reducer primitive and test whether the difference has
   zero total derivative.

