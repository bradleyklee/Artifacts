# Cyclic R3 trefoil geometry

Standalone first-principles reconstruction of a real-space trefoil family,
implemented entirely in Python/SymPy.

The starting parametrization is

```text
x(phi) = k sin(phi) + sin(2 phi)
y(phi) = k cos(phi) - cos(2 phi)
z(phi) = sin(3 phi)
```

with shape parameter `k`.  Everything else in this folder is derived or
verified from that parametrization.

## Implicit geometry

`src/derive_implicit_surfaces.py` uses the Laurent substitution
`q=exp(i phi)`, sparse polynomial ansatzes, coefficient matching, and linear
algebra.  It does **not** use a Groebner basis.  The resulting surfaces are

```text
H1 = -k*x^3 + 3*k*x*y^2
     + (x^2+y^2-(1-k^2)^2) z

H2 = (x^2+y^2)^2 + (1-k^2)(x^2+y^2)
     - 6*x^2*y + 2*y^3 - 4(1-k^2)z^2.
```

Direct substitution proves `H1=H2=0` on the complete parametrized curve.

## Tangent field and period

Let

```text
V = grad(H1) x grad(H2).
```

The exact verifier proves that on the curve

```text
V = Lambda(phi,k) * d r/dphi,
```

so `dt/dphi=1/Lambda` for the cross-product time.  A residue calculation then
gives, on `0<k<1`,

```text
T(k)/pi = (1+k^2)/(k(1-k^2)^3 sqrt(k^2+4)).
```

This is checked against direct 80-digit quadrature of the original
trigonometric integral.

## Final algebraic form

Writing `Y=T/pi`, the period is exactly the positive branch of

```text
k^2 (1-k^2)^6 (k^2+4) Y^2 - (1+k^2)^2 = 0.
```

Thus the period is algebraic over `Q(k)`.  Its minimal linear annihilator on
the oriented branch is already first order:

```text
Q1 Y' + Q0 Y = 0,
Q1 = k(k^2-1)(k^2+1)(k^2+4),
Q0 = 2(k^2+2)(3k^4+8k^2-1).
```

The verifier also checks a valid order-2 operator, its first-order
factorization, and a rational differential certificate for the order-2
integrand identity.  The order-2 equation is therefore correct but nonminimal
for this particular period.

## Integral normalization

The period has a simple pole at `k=0`.  Put

```text
x = k^2/16,
A(x) = 2 k T(k)/pi
     = (1+16x)/((1-16x)^3 sqrt(1+4x)).
```

Then

```text
(1+4x)(1-16x)^6 A(x)^2 - (1+16x)^2 = 0,
```

and

```text
A(x) = 1 + 62x + 2182x^2 + 61292x^3
       + 1519942x^4 + 34823300x^5 + ... .
```

The exact recurrence and convolution formula are in `OEIS_AUDIT.md` and are
checked term by term in `src/verify_geometry.py`.

## Reproduce

```bash
./verify.sh
./build.sh
```

The build generates the exact family drawings and period plot from the
parametrization.  A full-form certificate can be added later without changing
the mathematical core of this extraction.
