# Quartic elliptic detector: first closed locus

## Result

For

```text
H = p^2 + q^2
  + a*p^4 + b*p^3*q + c*p^2*q^2 + d*p*q^3 + e*q^4,
```

the involution `(p,q)->(-p,-q)` preserves `dq/H_p`.  Put

```text
t = p/q,   s = q^2,
A(t) = t^2+1,
B(t) = a*t^4+b*t^3+c*t^2+d*t+e.
```

The quotient equation is

```text
B(t)*s^2 + A(t)*s - alpha = 0.
```

With `y=2*B*s+A`, this becomes

```text
y^2 = A(t)^2 + 4*alpha*B(t),
dq/H_p = -dt/(2*y).
```

Thus the relevant period is literally an elliptic binary-quartic period.  No
Weierstrass transformation is needed.

For `f=A4*t^4+B3*t^3+C2*t^2+D1*t+E0`, use

```text
I  = 12*A4*E0 - 3*B3*D1 + C2^2,
Jb = 72*A4*C2*E0 + 9*B3*C2*D1
     - 27*A4*D1^2 - 27*B3^2*E0 - 2*C2^3.
```

Then

```text
Klein_J = 4*I^3/(4*I^3-Jb^2).
```

Choosing `c4=4I`, `c6=4Jb`, the general elliptic period operator from the
cubic calculation applies unchanged.  After removing the common polynomial
factor, the generic coefficient degrees are `(5,6,7)`.

## Verification

Run

```bash
python even_quartic_klein.py --verify
```

The verifier checks:

1. the clean exact quartic operator;
2. exact agreement with the archived fully generic model A;
3. 178 zero residual equations for generic model B at each of two primes.

## Search hierarchy

The next quartic search should keep three distinct targets:

```text
A. Intrinsic genus one
   Find a canonical coordinate system in which H is quadratic in one variable.
   Write H=A(q)*p^2+B(q)*p+C(q), set y=H_p, and inspect
   y^2=B(q)^2-4*A(q)*(C(q)-alpha).
   Squarefree degree 3 or 4 gives genus one directly.

B. Elliptic quotient
   Find a finite symplectic symmetry preserving both H and the period form.
   Construct invariant coordinates and test whether the quotient has genus one.
   The general even quartic is now completely closed by this route.

C. Elliptic factor / split Prym
   When the form lies in a nontrivial symmetry sector rather than descending,
   search for an order-two factor inside a genus-two or genus-three system.
   The triangle-square example belongs here; it is more exceptional than the
   general even-quartic locus.
```

## Pseudocode

```text
for quartic H in coefficient family:
    F = homogenize(H-alpha)
    g = arithmetic_genus(F) - sum(delta_infinity(F))

    if some canonical coordinates make H quadratic in p:
        D(q,alpha) = B(q)^2 - 4*A(q)*(C(q)-alpha)
        if squarefree_degree(D) in {3,4}:
            emit intrinsic elliptic model y^2=D

    for symplectic finite-order M with H(Mx)=H(x):
        determine action of M on dq/H_p
        construct invariant quotient C/<M>
        if quotient_genus == 1 and form descends:
            compute binary-quartic invariants and Klein J
            emit order-two operator

    if modular Picard-Fuchs order == 2 but neither test fires:
        flag elliptic-factor candidate
        analyze Jacobian/Prym splitting
```
