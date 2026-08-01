# Exact derivation

## 1. Algebraic equation

Put

```text
T(x) = A(x)-1.
```

From the OEIS equation

```text
(5-x)A = 4 + A^4
```

one obtains

```text
T = x + x*T + 6*T^2 + 4*T^3 + T^4.
```

Therefore

```text
T = x*Phi(T),
Phi(t) = (1+t)/(1-6*t-4*t^2-t^3).
```

Write

```text
Q(t) = 1-6*t-4*t^2-t^3,
R(t) = Phi(t)/t = (1+t)/(t*Q(t)).
```

## 2. Lagrange inversion and contour integral

For `n>=1`, Lagrange inversion gives

```text
a(n) = (1/n) * [t^(n-1)] Phi(t)^n.
```

Equivalently,

```text
a(n) = Res_{t=0} (1+t)^n / (n*t^n*Q(t)^n).
```

Thus define

```text
F_n(t) = R(t)^n/n.
```

Then `a(n)=Res_{t=0} F_n(t)` for `n>=1`, while `a(0)=1` separately.

## 3. Telescoper

For `j=0,...,4`, define

```text
p0(n) = 3*(n+1)*(3*n-1)*(3*n+7)
p1(n) = -15*(2*n+3)*(18*n^2+54*n+29)
p2(n) = 75*(n+2)*(54*n^2+216*n+209)
p3(n) = -6750*(n+2)*(n+3)*(2*n+5)
p4(n) = 491*(n+2)*(n+3)*(n+4)
```

The recurrence is

```text
sum_{j=0}^4 p_j(n)*a(n+j) = 0.
```

The creative-telescoping identity proves this for `n>=1`. The `n=0` instance is checked directly from the initial values, so the recurrence is valid for `n>=0`.

## 4. Rational certificate

Let

```text
C(n,t) = (1+t)*P(n,t) / (n*(n+1)*t^3*Q(t)^3),
```

where

```text
P(n,t) = c0(n) + c1(n)t + ... + c12(n)t^12
```

and

```text
c0  = -491*n*(n+1)*(n+2)
c1  = 4*n*(n+1)*(1411*n+2791)
c2  = n*(11394*n^2+34382*n+23093)
c3  = 15004*n^3+47764*n^2+31584*n-21
c4  = 16447*n^3+56569*n^2+42180*n+378
c5  = 6*(2644*n^3+9656*n^2+7971*n-336)
c6  = 7*(1812*n^3+6940*n^2+6463*n+225)
c7  = 4*(2094*n^3+8438*n^2+9116*n+1827)
c8  = 4611*n^3+19393*n^2+23539*n+7812
c9  = 15*(132*n^3+568*n^2+730*n+287)
c10 = 198*(n+1)^2*(3*n+7)
c11 = 36*(n+1)^2*(3*n+7)
c12 = 3*(n+1)^2*(3*n+7).
```

Then the exact rational-function identity is

```text
sum_{j=0}^4 p_j(n)*F_{n+j}(t)
    = d/dt ( C(n,t)*R(t)^n ).
```

After division by `R(t)^n`, the identity checked by the script is

```text
sum_{j=0}^4 p_j(n)*R(t)^j/(n+j)
    = dC/dt + n*(R'(t)/R(t))*C(n,t).
```

This avoids asking a computer algebra system to simplify symbolic integer powers.

Taking `Res_{t=0}` annihilates the derivative, because the residue of a formal Laurent-series derivative is zero. Hence the recurrence follows.

## 5. Claim level

This package supplies an explicit order-4 telescoper and certificate. It does not claim that order 4 is minimal.
