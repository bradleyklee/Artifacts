# General two-node genus-one quartic and its order-2 annihilator

## 1. Family in unrestricted expansion coefficients

Let

```text
Q2(p,q) = A p^2 + B p q + C q^2,
L1(p,q) = D p + E q,
H2(p,q) = F p^2 + G p q + K q^2,
H1(p,q) = M p + N q.
```

The genus-one stratum discussed in the calculation is

```text
H = kappa Q2^2 + Q2 L1 + H2 + H1 + R.
```

Written out:

```text
H(p,q) =
    kappa A^2 p^4
  + 2 kappa A B p^3 q
  + kappa (B^2 + 2 A C) p^2 q^2
  + 2 kappa B C p q^3
  + kappa C^2 q^4

  + A D p^3
  + (A E + B D) p^2 q
  + (B E + C D) p q^2
  + C E q^3

  + F p^2 + G p q + K q^2
  + M p + N q + R.
```

Assume `Q2` is squarefree and the two tangent-cone discriminants at its roots
are nonzero.  The projective curve `H=alpha` then has two ordinary nodes at
infinity, total delta invariant two, and normalization genus

```text
g = 3 - 2 = 1.
```

## 2. Split-node coordinates

After a linear coordinate change sending the two factors of `Q2` to `p` and
`q`, the same family has the particularly readable form

```text
H(p,q) =
    k p^2 q^2
  + beta p^2 q + gamma p q^2
  + a p^2 + b p q + c q^2
  + d p + e q + h.
```

This is not a Weierstrass conversion.  It only places the two nodes at the
coordinate points at infinity.

For a nonsplit `Q2`, perform this step over its quadratic splitting field.  The
resulting Picard--Fuchs operator is invariant under conjugation and descends to
the original coefficient field.  The supplied implementation presently works
in the split-node chart.

## 3. Direct reduction to a binary quartic

On the level `H=alpha`, regard the equation as quadratic in `q`:

```text
A(p) q^2 + B(p) q + C(p) = 0,

A(p) = k p^2 + gamma p + c,
B(p) = beta p^2 + b p + e,
C(p) = a p^2 + d p + h - alpha.
```

Set

```text
y = H_q = 2 A(p) q + B(p).
```

Then, identically on the level curve,

```text
y^2 = D_alpha(p) = B(p)^2 - 4 A(p) C(p),
```

and Hamilton's relation gives

```text
dq/H_p = -dp/H_q = -dp/y.
```

Thus the time differential itself becomes the invariant differential of a
binary quartic.  No guessed addition formula or Weierstrass equation is used.

Write

```text
D_alpha(p) = u4 p^4 + u3 p^3 + u2 p^2 + u1 p + u0,
```

where

```text
u4 = beta^2 - 4 k a,
u3 = 2 beta b - 4(k d + gamma a),
u2 = b^2 + 2 beta e - 4 a c - 4 gamma d - 4 k(h-alpha),
u1 = 2 b e - 4 c d - 4 gamma(h-alpha),
u0 = e^2 - 4 c(h-alpha).
```

## 4. Universal order-2 annihilator

Define the binary-quartic invariants

```text
I  = 12 u4 u0 - 3 u3 u1 + u2^2,
Jb = 72 u4 u2 u0 + 9 u3 u2 u1
     - 27 u4 u1^2 - 27 u3^2 u0 - 2 u2^3.
```

Then put

```text
c4 = 4 I,
c6 = 4 Jb,
Delta = c4^3 - c6^2,
G = 2 c4 c6' - 3 c6 c4',
```

where primes denote `d/dalpha`.  For

```text
T(alpha) = integral dq/H_p
```

the following compact universal equation holds:

```text
P2 T'' + P1 T' + P0 T = 0,

P2 = 144 Delta G,
P1 = 144(Delta' G - Delta G'),
P0 = 12(Delta'' G - Delta' G')
     - 9 G c4 (c4')^2 + 4 G (c6')^2.
```

Common factors should be divided out after specialization.  Generically,

```text
deg_alpha(I,Jb,Delta,G) = (2,3,5,3),
deg_alpha(P0,P1,P2)     = (6,7,8).
```

Special strata can collapse drastically.  For example,

```text
H = p^2 + q^2 - d p^2 q^2
```

gives the reduced equation

```text
d T + 4(2 alpha d - 1) T'
    + 4 alpha(alpha d - 1) T'' = 0.
```

## 5. Exact-differential verification

Let `D=D_alpha(p)` and `D_alpha_derivative=dD/dalpha`.  The code verifies that
for each generic exact specialization there is a polynomial `R(p,alpha)` with

```text
P0 dp/sqrt(D) + P1 d/dalpha(dp/sqrt(D))
 + P2 d^2/dalpha^2(dp/sqrt(D))
 = d( R / D^(3/2) ).
```

Equivalently,

```text
R_p D - (3/2) R D_p
 = P0 D^2 - (1/2)P1 D_alpha_derivative D
   + (3/4)P2 D_alpha_derivative^2.
```

Three fully generic integer specializations pass exactly.  In all three, the
reduced operator degrees are `(6,7,8)` and a primitive of degree six in `p`
and six in `alpha` closes the identity.  The symbolic Edwards specialization
also matches exactly.

Run:

```bash
python two_node_annihilator.py --verify
```
