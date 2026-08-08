# Merged status and continuation plan

Date: 2026-08-02  
Research owner: Bradley Klee  
Privacy: unpublished research; NO POACHING.

## 1. The active computations are the same new square–hexagon example

The earlier triangle–square certificate is complete.  It appears in the
certificate-transfer packet only as a regression test and should not be
confused with the present target.

The active square–hexagon computations in both packets use

\[
2H(p,q)=p^2+q^2-2p^2q^2+
\frac14(p^3-3pq^2)^2,
\qquad \alpha=2H,
\]

or, in canonical polar variables,

\[
\alpha=2\lambda+
\lambda^2(-1+\cos4\phi)+
\lambda^3(1+\cos6\phi).
\]

Their first 60 coefficients of \(T(\alpha)/(2\pi)\) agree exactly.  The
integer b-file in the square–hexagon packet uses

\[
T(\alpha)/(2\pi)=\sum_{n\ge0}b(n)(\alpha/8)^n.
\]

## 2. Why the preliminary guesser appeared negative

The preliminary packet had 60 coefficients and held 8 out, leaving 52 fitting
equations.  Its feasible order-four search therefore stopped at coefficient
degree 8.  The operator later found by the other thread has order 4 and degree
14, hence 75 nominal coefficient unknowns before normalization.  It was never
inside the identifiable search box.  There is no contradiction.

## 3. Contributions retained from each thread

### Series/geometry thread

- exact period generator;
- exact order-four, degree-fourteen annihilator \(A_4\);
- exact order-six, degree-eight annihilator \(A_6\);
- verification through more than 210 coefficient equations;
- critical cubic and separatrix geometry;
- bounded order-three exclusion through degree 68.

### Deductive/certificate thread

- Cartesian reduction over \(\mathbb Q(\alpha)\);
- common-pole derivative numerators;
- exact-image map for \(\Xi=V/\rho^{2r-1}\), with \(\rho=(2H)_p\);
- support-driven rectangular matrices;
- symmetry sector \(p\) even, \(q\) odd for the primitive;
- rank, failure, and replay conventions.

## 4. New merged result: the missing exact certificate closes

Let

\[
\rho=(2H)_p=2H_p,
\qquad
\omega=\frac{dq}{H_p}=\frac{2\,dq}{\rho},
\qquad
A_4=\sum_{j=0}^{4}P_j(\alpha)\partial_\alpha^j.
\]

Use

\[
\Xi=\frac{V(\alpha,p,q)}{\rho^7},
\]

with primitive source slots

\[
p\in\{0,2,4\},\qquad q\in\{1,3,\ldots,27\}.
\]

A candidate-guided exact backsolve gives:

```text
ambient rows:                 55
primitive columns:            42
rank of exact-image matrix:   42
nonzero primitive slots:      40
expanded (alpha,p,q) terms:   514
maximum alpha degree in V:    15
coefficient denominators:     at most 2
exact reduced residual:       zero
```

The two zero source slots are

```text
p^0 q^27
p^4 q^27
```

The exact support boundary within this pole/parity ansatz is:

```text
odd q-bound 25: rank(C)=39, rank([C|target])=40, no solution
odd q-bound 27: rank(C)=42, rank([C|target])=42, solution
```

Thus the packet now contains an exact, replayable identity

\[
\boxed{A_4\circ\omega=d\Xi}
\]

on the energy curve.  The replay verifies the cleared numerator after reduction
modulo \(E-\alpha\), exactly as required for the ambient polynomial check.

The primitive coefficients are polynomial in \(\alpha\), not rational
functions with an extra parameter denominator.  Multiplying both \(A_4\) and
\(V\) by 2 makes every stored primitive coefficient integral.

## 5. What work should be stopped

Do not spend more time on these tasks for this fixed model:

1. generating more coefficients merely to rediscover \(A_4\);
2. unrestricted order/degree guessing before using the known operator;
3. direct combined-nullspace searches at orders 1 and 2 as a route to this
   certificate;
4. treating the 60-term preliminary negative as evidence against order 4;
5. starting a second certificate backend before the present certificate is
   archived and made readable.

These branches have either completed their job or have been superseded by the
candidate-guided backsolve.

## 6. Immediate continuation plan

### Stage A — finish the certificate artifact

1. Treat `exact/order4_operator.json` and `exact/order4_xi.json` as the canonical
   machine payload.
2. Generate a human certificate that states \(H\), \(H_p\),
   \(\rho=(2H)_p\), \(\omega=dq/H_p=2dq/\rho\), the five \(P_j\),
   and \(\Xi=V/\rho^7\).
3. Present \(V\) as a 40-row table of coefficient polynomials
   \(v_{p,q}(\alpha)\), not as a 514-term wall of text.
4. Embed the JSON and replay script as the hidden payload.
5. Include the two rank witnesses at q-bounds 25 and 27.

This is now packaging work, not an open existence search.

### Stage B — seek a smaller equivalent certificate

The present solution is unique inside the 42-column source space because the
exact-image matrix has full column rank.  Merely changing pivot rows will not
make it sparser.  Genuine compression must change one of:

- the operator within its Ore-equivalence class;
- the pole divisor or primitive gauge;
- the coordinate backend, especially the compressed \((\lambda,c,y)\) action
  fiber;
- a common scaling/presentation convention.

Use the current certificate as the regression oracle: every proposed
compression must reproduce the same exact identity.

### Stage C — explain the order-six operator

Perform exact left Ore division of \(A_6\) by \(A_4\).  The concrete target is
an order-two multiplier \(B\) satisfying

\[
A_6=B A_4.
\]

If exact division succeeds, factor the leading singular polynomials and identify
which roots are apparent.  This will explain the degree-eight/order-six tradeoff
without further series guessing.

### Stage D — prove the support filtration

For this sextic-in-\(p\) model, record the growth of

\[
\mathcal P_b=\operatorname{span}
\{p^i q^j:i=0,2,4;\ j\le b\text{ odd}\}
\]

and the actual reduced image space.  Use the leading q-bands of the three image
families to prove eventual full column rank and stable quotient dimension.  The
q=25/27 transition is the first exact datum for that theorem.

### Stage E — resume parameter-stratum search only afterward

Once the certificate and regression are stable, return to

\[
\alpha=2\lambda+
\lambda^2(a_0+\cos4\phi)+
\lambda^3(b_0+b_6\cos6\phi)
\]

and classify whether \((-1,1,1)\) is isolated or lies on an exceptional
algebraic locus.  The reusable pipeline should be:

```text
geometry screen
-> exact period series
-> candidate operator
-> candidate-guided exact-image backsolve
-> certificate replay
-> Ore relation signature
```

## 7. Algorithm-library update

Add a new entry, `ALG-007 Candidate-Guided Certificate Backsolve`:

```text
INPUT:
    energy E, known exact operator A, parity/pole ansatz

BUILD:
    common derivative target T = numerator(A o omega)
    exact-image columns C(mu) for source monomials mu

FOR support bounds b:
    form the actual union of supports
    compute rank(C_b) and rank([C_b | T])
    if ranks differ: record exact bounded failure
    if ranks agree:
        solve C_b x = T
        reconstruct V and Xi
        verify the exact reduced residual is zero
        return A, Xi, ranks, support trace
```

This is the correct bridge between inductive discovery and deductive proof.  It
is much cheaper than asking the deductive branch to rediscover an operator that
is already known.

## 8. Present status

The square-plus-hexagon example is no longer missing its differential
certificate.  The main remaining mathematical jobs are compression,
Ore-factor explanation, and a filtration theorem.  The parameter-family search
is valuable but should not interrupt completion of those three items.
