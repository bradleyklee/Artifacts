# OEIS audit

For

```text
A(x) = (1+16x)/((1-16x)^3 sqrt(1+4x)),
```

the first coefficients are

```text
1, 62, 2182, 61292, 1519942, 34823300, 755251868,
15733489048, 317810234438, 6265083472788, ... .
```

The exact coefficient formula is

```text
a(n) = Sum_{j=0..n}
       (-1)^j binom(2j,j) (n-j+1)^2 16^(n-j).
```

The first-order differential equation gives

```text
(n+1)a(n+1)
 = (62-4n)a(n)
 + 256(n+2)a(n-1)
 + 512(2n+1)a(n-2),
```

with out-of-range terms zero and `a(0)=1`.

The full normalized sequence had no direct match in the earlier exact-prefix
audit retained for this project.  A canonical constituent is OEIS A000984,
the central binomial coefficients, because

```text
1/sqrt(1+4x) = Sum (-1)^n binom(2n,n) x^n.
```

The mathematical content of this file does not depend on a live OEIS lookup;
`src/verify_geometry.py` proves the coefficient formula and recurrence
symbolically.
