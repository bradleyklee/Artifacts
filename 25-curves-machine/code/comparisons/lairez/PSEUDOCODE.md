# Parallel pseudocode: Klee certificates versus Lairez reduction

Research owner: Bradley Klee. Unpublished research; NO POACHING.

Attribution: `LAIREZ_*` steps abstract Pierre Lairez's extended
Griffiths--Dwork / Rham--Koszul reduction and Picard--Fuchs implementation.
They are not claimed as new algorithms here.

## Adapter

```text
KLEE_TO_LAIREZ(case):
    INPUT E(p,q) = 2H(p,q), parameter alpha
    SET rho = (2H)_p = 2H_p
    ASSERT omega = dq/H_p = 2 dq/rho
    SET ambient_form = 2 dp wedge dq / (E-alpha)
    VERIFY PoincareResidue(ambient_form, E=alpha) = omega
    RETURN rational_function f(alpha,p,q) = 2/(E-alpha)
```

The factor `2` is essential. Omitting it gives `dq/rho`, only half of the
period form used in the showcase certificates, where `rho=(2H)_p=2H_p`.

## Our current exact-image route

```text
KLEE_CERTIFICATE(E, guessed_operator A, support_filtration P_b):
    rho <- derivative(E,p)
    W <- common-pole numerators of omega, d_alpha omega, ...
    FOR support bound b:
        C_b <- columns for d(V/rho^(2r-1)), V in P_b
        IF rank(C_b) != rank([C_b | A(W)]):
            record exact bounded failure
            CONTINUE
        solve C_b x = A(W)
        reconstruct Xi_K = V/rho^(2r-1)
        VERIFY ReduceModulo(E-alpha, A(omega)-d Xi_K) = 0
        RETURN A, Xi_K, support/rank witness
```

## Lairez route, including the currently hidden certificate

```text
LAIREZ_CERTIFICATE(f, initial_reduction_depth r):
    (F,N) <- homogenize square-free denominator and numerator
    LOOP:
        U <- initialize Rham-Koszul reducer at depth r
        classes <- []
        witnesses <- []
        current <- input class
        REPEAT:
            (remainder, cofactor) <- HomReduceWithCertificate(U,current,r)
            append remainder to classes
            append cofactor to witnesses
            current <- parameter_derivative(remainder)
        UNTIL classes are linearly dependent
        IF closure degree test fails:
            r <- r+1
            CONTINUE
        a <- primitive null vector of classes
        Xi_L <- same linear combination of witnesses
        VERIFY sum_j a_j partial_alpha^j(f) = total_derivative(Xi_L)
        RETURN A_L=sum_j a_j D^j, Xi_L, r, basis, closure witness
```

### Minimal instrumentation needed in Pierre's code

```text
1. Keep representation mode R:c when variant contains "cert".
2. Change EDecode so it returns both reduced polynomial and accumulated
   cofactor instead of discarding the second module component.
3. Propagate those cofactors through HomReduce -> ComputeGM -> GaussManin.
4. In CyclicEquation, apply the cyclic null vector to the stored cofactors.
5. Return <operator, primitive, replay_data> from a new intrinsic
   PeriodsCertificate; leave Periods unchanged.
```

## Certificate comparison

Literal equality of primitive numerators is not the right test: the two
algorithms use different ambient coordinates, homogenizations, bases, and
primitive gauges.

```text
COMPARE_CERTIFICATES(E, (A_K,Xi_K), (A_L,Xi_L)):
    normalize A_K and A_L to primitive Ore operators
    IF A_K != A_L:
        test left/right Ore divisibility and common minimal right factor
        IF their minimal period operator differs:
            RETURN genuinely different annihilators

    pull Xi_L back through Lairez homogenization/dehomogenization
    Delta <- Xi_L - Xi_K
    VERIFY ReduceModulo(E-alpha, d(Delta)) = 0

    IF Delta = 0 in the curve function field:
        RETURN same certificate in different presentation
    IF d(Delta) = 0 but Delta != 0:
        RETURN same certificate up to locally constant gauge
    IF both certificate identities verify but d(Delta) != 0:
        RETURN operators are Ore-equivalent but primitives correspond to
               different operator representatives; transport operators first
    ELSE:
        RETURN mismatch or extraction bug
```

## Showcase matrix

```text
case             Klee order  Klee pole       Lairez input
triangle-square       2       rho^3           2/(2H-alpha)
square-hexagon        4       rho^7           2/(2H-alpha)
```

The minimal operators agree after primitive normalization. For
triangle--square, feeding the Lairez-derived operator into the Klee canonical
curve reconstruction returns exactly the stored 71-term primitive. Direct
conversion of the higher-pole ambient one-form to that curve gauge remains a
separate normalization problem.

## Affine certificate transport added by the comparison port

```text
REDUCE_WITH_CERTIFICATE(P/f^k, beta):
    R, (Gp,Gq,Gz) <- JACOBIAN_DECOMPOSE(P)
    A <- substitute_z_1(Gp-p*Gz)
    B <- substitute_z_1(Gq-q*Gz)
    beta <- beta + (B dp-A dq)/((k-1)f^(k-1))
    low <- div(G)/(k-1)
    RETURN R/f^k + low/f^(k-1), beta

PARAMETER_DERIVATIVE(class, beta):
    differentiated_class <- d_alpha(class)
    differentiated_beta <- d_alpha(beta)
    RETURN REDUCE_WITH_CERTIFICATE(differentiated_class, differentiated_beta)

ASSEMBLE(operator P, derivative_classes):
    beta <- sum_j P_j * beta_j
    VERIFY d(beta) = sum_j P_j*d_alpha^j(2 dp dq/(2H-alpha))
    RETURN beta
```

## Separated hybrid bridge

```text
operator <- LAIREZ_OPERATOR(2H)
C, W <- KLEE_EXACT_IMAGE_AND_DERIVATIVE_MAPS(2H, configured_support)
solve C*x + W*operator = 0
Xi <- (-x as polynomial)/rho^(2*order-1)
VERIFY operator(omega) = d(Xi)
COMPARE Xi with the independently stored/derived Klee primitive
```
