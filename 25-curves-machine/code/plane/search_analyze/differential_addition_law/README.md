# Differential reconstruction of addition laws

## Main result

For a smooth genus-one curve over a field `K`, a nonzero invariant differential
`omega` does **not** by itself choose a group law: translation preserves
`omega`.  After choosing a rational base point `O`, however, the addition map
is uniquely characterized by

```text
m(P,O)=P,   m(O,Q)=Q,
m^* omega = pr1^* omega + pr2^* omega.
```

Indeed, compare `m` with the ordinary addition map.  Their difference has zero
pullback of the nonzero differential, hence is constant; the identity condition
forces that constant to be `O`.

This gives a useful reconstruction criterion rather than merely a verifier.

## Hamiltonian PDE

On a level curve

```text
H(p,q)=alpha
```

use the time differential

```text
omega = dq/H_p.
```

For a candidate rational map

```text
M((p1,q1),(p2,q2)) = (P,Q),
```

the invariant-differential identity is equivalent to

```text
H_p(p_i,q_i) * partial_{q_i} Q
- H_q(p_i,q_i) * partial_{p_i} Q
= H_p(P,Q),                         i=1,2.
```

Together with `H(P,Q)=alpha` and the identity conditions, these are finite
algebraic equations after a rational ansatz is chosen.

## General cubic

For

```text
y^2 + a1*x*y + a3*y = x^3 + a2*x^2 + a4*x + a6,
```

write

```text
lambda = (y2-y1)/(x2-x1),
nu     = (y1*x2-y2*x1)/(x2-x1).
```

The reconstruction gives

```text
x3 = lambda^2 + a1*lambda - a2 - x1 - x2,
y3 = -(lambda+a1)*x3 - nu - a3.
```

The code verifies curve closure and

```text
dx3/(2*y3+a1*x3+a3)
 = dx1/(2*y1+a1*x1+a3) + dx2/(2*y2+a1*x2+a3).
```

The first differential residual factors exactly as

```text
[a1*(x1-x2)+2*(y1-y2)] * [F(P2)-F(P1)] / (x1-x2)^3,
```

so it vanishes identically on `C x C`.  This is a particularly clean proof that
the chord formula is the time-addition law.

## Edwards quartic

For

```text
x^2+y^2 = 1+d*x^2*y^2
```

with identity `(0,1)`, the same criterion verifies

```text
X = (x1*y2+y1*x2)/(1+d*x1*x2*y1*y2),
Y = (y1*y2-x1*x2)/(1-d*x1*x2*y1*y2),
```

and

```text
m^*[dx/(2*y*(1-d*x^2))]
 = pr1^*omega + pr2^*omega.
```

The doubling law is

```text
X(2P)=2*x*y/(1+d*x^2*y^2),
Y(2P)=(y^2-x^2)/(1-d*x^2*y^2).
```

This is exactly the algebraic statement that point addition is linear in the
time parameter.

## Consequence for quartic stratification

A genus-one quartic family can fall into two arithmetically different cases.

1. **A rational section exists.**  The curve is an elliptic curve over the
   coefficient field, and a rational binary law can be reconstructed from the
   PDE above.
2. **No rational section is visible or exists.**  The curve is a genus-one
   torsor.  Its Jacobian has a binary law, but the quartic itself need not.
   The intrinsic replacement is a rational ternary law

```text
tau(P,Q,R)=P-Q+R,
tau^*omega = omega_P - omega_Q + omega_R.
```

Once a rational point `P0` appears in a specialization, define

```text
P (+) Q = tau(P,P0,Q).
```

That immediately turns one rational point into a point-generation and
extrapolation mechanism.

## Search order

```text
order-2 period / genus-one quotient
        |
        +-- rational section O?
        |      |
        |      +-- yes: solve binary differential PDE
        |      +-- no:  solve ternary torsor PDE
        |
        +-- verify exact time-differential identity
        +-- specialize parameters and search rational points
        +-- use addition/ternary law to generate further points
```
