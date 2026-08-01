# Verification pseudocode

```text
Q(t) <- 1 - 6*t - 4*t^2 - t^3
R(t) <- (1+t)/(t*Q(t))

Define p[0..4](n) from certificate.json
Define P(n,t) from its 13 t-coefficients
C(n,t) <- (1+t)*P(n,t)/(n*(n+1)*t^3*Q(t)^3)

lhs <- Sum_{j=0..4} p[j](n)*R(t)^j/(n+j)
rhs <- dC/dt + n*(R'(t)/R(t))*C(n,t)
Assert Cancel(lhs-rhs) = 0

For n=1..N:
    contour_term[n] <- (1/n)*Coeff_t(Phi(t)^n, n-1)
Assert contour_term agrees with stored OEIS terms

Enumerate grammar members through size 4
Assert counts = [1,1,7,95,1614]

For each available n:
    Assert Sum_{j=0..4} p[j](n)*a[n+j] = 0
```
