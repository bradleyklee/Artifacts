---
title: "OEIS Field Deltas for 23 Calculus Certificates"
generated_date: "2026-07-30"
case_count: 23
comparison_basis: "current OEIS records checked 2026-07-30"
format: "per-item comparison plus paste-ready OEIS internal fields"
---

# OEIS field deltas: what exists and what should be added

The status tables distinguish genuinely new identities from formulas already
present on OEIS in the same or an equivalent normalization. Full reduction
matrices are not pasted into Formula fields; a concise dimensional identity
belongs in Comments and the exact payload belongs in a linked certificate.

The `%F`, `%C`, and `%H` lines below use OEIS internal-field notation.
Remove the leading field code and A-number when pasting into the corresponding
web form field.

## A120588

Current record: https://oeis.org/A120588

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / Lagrange formula | already present |
| Polynomial recurrence | already present or equivalent normalization |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: 3*A(x)=2+1*x+A(x)^2.
- Lagrange/reversion coefficient content equivalent to: a(n)=d/n * [u^(n-1)] D(u)^(-n), n>=1.
- A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.

### Recommended additions

```text
%F A120588 Contour form: Put rho(u)=u*(1-1*u^1). a(n)=(1)/(2*Pi*i*n) * Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A120588 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (2*x)*A(x) + (-4*x^2 + x)*A'(x) = 3*x.
%C A120588 Typogeometric interpretation: with A(x)=1+(1)*T(x), T=x+1*T^2. The colored plane constructors have multiplicities {Delta_2: 1}; coefficients count the resulting words by number of true leaves.
%e A120588 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1; 2 true leaves: {1,1}; 3 true leaves: {1,{1,1}}, {{1,1},1}.
%C A120588 Exact Hermite/direct-x reduction uses a 4 X 4 reduction matrix and a 1 X 2 remainder matrix of rank 1 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120588 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation, reversion/Lagrange formula, and polynomial recurrence are already represented on the current record.

## A120589

Current record: https://oeis.org/A120589

| Candidate identity | Status against current OEIS record |
|---|---|
| Power/convolution definition | already present |
| Coefficient formula | already present or immediate equivalent |
| Polynomial recurrence | new |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Definition: A_parent(x)^2 from A120588.
- Coefficient identity: a(n)=[x^n]A_A120588(x)^2.

### Recommended additions

```text
%F A120589 Recurrence: (0)*a(n) + (-4*n - 2)*a(n+1) + (n + 2)*a(n+2) = 0, for n>=1.
%F A120589 Contour form: Put D(u)=1-1*u^1. a(n)=(2*1)/(2*Pi*i*n)*Integral_gamma (1+(1)*u)^1 du/(u^n*D(u)^n) Here gamma is a small positively oriented loop around u=0.
%F A120589 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (2*x)*A(x) + (-4*x^2 + x)*A'(x) = 2*x^2 + 4*x.
%C A120589 Typogeometric interpretation: ordered forest of 2 parent A120588 typogeometries; Delta_2 with all 2 positions occupied.
%e A120589 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: {0,1}, {1,0}; 2 true leaves: {0,{1,1}}, {1,1}, {{1,1},0}; 3 true leaves: {0,{1,{1,1}}}, {0,{{1,1},1}}, {1,{1,1}}, {{1,1},1}, {{1,{1,1}},0}, {{{1,1},1},0}.
%C A120589 Exact Hermite/direct-x reduction uses a 4 X 4 reduction matrix and a 2 X 3 remainder matrix of rank 2 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120589 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The defining convolution/power relation and its immediate coefficient identity are already represented on the current record.

## A120590

Current record: https://oeis.org/A120590

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / Lagrange formula | already present |
| Polynomial recurrence | already present or equivalent normalization |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: 4*A(x)=3+1*x+A(x)^3.
- Lagrange/reversion coefficient content equivalent to: a(n)=d/n * [u^(n-1)] D(u)^(-n), n>=1.
- A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.

### Recommended additions

```text
%F A120590 Contour form: Put rho(u)=u*(1-3*u^1-1*u^2). a(n)=(1)/(2*Pi*i*n) * Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A120590 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (3*x^2)*A(x) + (-27*x^3 - 81*x^2)*A'(x) + (-27*x^4 - 162*x^3 + 13*x^2)*A^(2)(x) = 0.
%C A120590 Typogeometric interpretation: with A(x)=1+(1)*T(x), T=x+3*T^2+1*T^3. The colored plane constructors have multiplicities {Delta_2: 3, Delta_3: 1}; coefficients count the resulting words by number of true leaves.
%e A120590 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1; 2 true leaves: {1,1} (multiplicity 3); 3 true leaves: {1,{1,1}} (multiplicity 9), {{1,1},1} (multiplicity 9), {1,1,1}.
%C A120590 Exact Hermite/direct-x reduction uses a 6 X 6 reduction matrix and a 2 X 3 remainder matrix of rank 2 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120590 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation, reversion/Lagrange formula, and polynomial recurrence are already represented on the current record.

## A120591

Current record: https://oeis.org/A120591

| Candidate identity | Status against current OEIS record |
|---|---|
| Power/convolution definition | already present |
| Coefficient formula | already present or immediate equivalent |
| Polynomial recurrence | new |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Definition: A_parent(x)^3 from A120590.
- Coefficient identity: a(n)=[x^n]A_A120590(x)^3.

### Recommended additions

```text
%F A120591 Recurrence: (0)*a(n) + (-27*n^2 - 54*n - 24)*a(n+1) + (-162*n^2 - 567*n - 486)*a(n+2) + (13*n^2 + 65*n + 78)*a(n+3) = 0, for n>=1.
%F A120591 Contour form: Put D(u)=1-3*u^1-1*u^2. a(n)=(3*1)/(2*Pi*i*n)*Integral_gamma (1+(1)*u)^2 du/(u^n*D(u)^n) Here gamma is a small positively oriented loop around u=0.
%F A120591 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (3*x^2)*A(x) + (-27*x^3 - 81*x^2)*A'(x) + (-27*x^4 - 162*x^3 + 13*x^2)*A^(2)(x) = 24*x^3 + 72*x^2.
%C A120591 Typogeometric interpretation: ordered forest of 3 parent A120590 typogeometries; Delta_3 with all 3 positions occupied.
%e A120591 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: {0,0,1}, {0,1,0}, {1,0,0}; 2 true leaves: {0,0,{1,1}} (multiplicity 3), {0,1,1}, {0,{1,1},0} (multiplicity 3), {1,0,1}, {1,1,0}, {{1,1},0,0} (multiplicity 3); 3 true leaves: {0,0,{1,{1,1}}} (multiplicity 9), {0,0,{{1,1},1}} (multiplicity 9), {0,0,{1,1,1}}, {0,1,{1,1}} (multiplicity 3), {0,{1,1},1} (multiplicity 3), {0,{1,{1,1}},0} (multiplicity 9), {0,{{1,1},1},0} (multiplicity 9), {0,{1,1,1},0}, {1,0,{1,1}} (multiplicity 3), {1,1,1}, {1,{1,1},0} (multiplicity 3), {{1,1},0,1} (multiplicity 3), {{1,1},1,0} (multiplicity 3), {{1,{1,1}},0,0} (multiplicity 9), {{{1,1},1},0,0} (multiplicity 9), {{1,1,1},0,0}.
%C A120591 Exact Hermite/direct-x reduction uses a 6 X 6 reduction matrix and a 3 X 4 remainder matrix of rank 3 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120591 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The defining convolution/power relation and its immediate coefficient identity are already represented on the current record.

## A120592

Current record: https://oeis.org/A120592

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / Lagrange formula | already present |
| Polynomial recurrence | already present or equivalent normalization |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: 5*A(x)=4+4*x+A(x)^3.
- Lagrange/reversion coefficient content equivalent to: a(n)=d/n * [u^(n-1)] D(u)^(-n), n>=1.
- A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.

### Recommended additions

```text
%F A120592 Contour form: Put rho(u)=u*(1-3*u^1-2*u^2). a(n)=(2)/(2*Pi*i*n) * Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A120592 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (12*x^2)*A(x) + (-108*x^3 - 108*x^2)*A'(x) + (-108*x^4 - 216*x^3 + 17*x^2)*A^(2)(x) = 0.
%C A120592 Typogeometric interpretation: with A(x)=1+(2)*T(x), T=x+3*T^2+2*T^3. The colored plane constructors have multiplicities {Delta_2: 3, Delta_3: 2}; coefficients count the resulting words by number of true leaves.
%e A120592 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1 (multiplicity 2); 2 true leaves: {1,1} (multiplicity 6); 3 true leaves: {1,{1,1}} (multiplicity 18), {{1,1},1} (multiplicity 18), {1,1,1} (multiplicity 4).
%C A120592 Exact Hermite/direct-x reduction uses a 6 X 6 reduction matrix and a 2 X 3 remainder matrix of rank 2 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120592 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation, reversion/Lagrange formula, and polynomial recurrence are already represented on the current record.

## A120593

Current record: https://oeis.org/A120593

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / Lagrange formula | already present |
| Polynomial recurrence | already present or equivalent normalization |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: 5*A(x)=4+1*x+A(x)^4.
- Lagrange/reversion coefficient content equivalent to: a(n)=d/n * [u^(n-1)] D(u)^(-n), n>=1.
- A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.

### Recommended additions

```text
%F A120593 Contour form: Put rho(u)=u*(1-6*u^1-4*u^2-1*u^3). a(n)=(1)/(2*Pi*i*n) * Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A120593 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (40*x^3)*A(x) + (-688*x^4 - 2752*x^3)*A'(x) + (-1152*x^5 - 9216*x^4 - 18432*x^3)*A^(2)(x) + (-256*x^6 - 3072*x^5 - 12288*x^4 + 491*x^3)*A^(3)(x) = 0.
%C A120593 Typogeometric interpretation: with A(x)=1+(1)*T(x), T=x+6*T^2+4*T^3+1*T^4. The colored plane constructors have multiplicities {Delta_2: 6, Delta_3: 4, Delta_4: 1}; coefficients count the resulting words by number of true leaves.
%e A120593 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1; 2 true leaves: {1,1} (multiplicity 6); 3 true leaves: {1,{1,1}} (multiplicity 36), {{1,1},1} (multiplicity 36), {1,1,1} (multiplicity 4).
%C A120593 Exact Hermite/direct-x reduction uses a 8 X 8 reduction matrix and a 3 X 4 remainder matrix of rank 3 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120593 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation, reversion/Lagrange formula, and polynomial recurrence are already represented on the current record.

## A120594

Current record: https://oeis.org/A120594

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / Lagrange formula | already present |
| Polynomial recurrence | already present or equivalent normalization |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: 8*A(x)=7+8*x+A(x)^4.
- Lagrange/reversion coefficient content equivalent to: a(n)=d/n * [u^(n-1)] D(u)^(-n), n>=1.
- A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.

### Recommended additions

```text
%F A120594 Contour form: Put rho(u)=u*(1-3*u^1-4*u^2-2*u^3). a(n)=(2)/(2*Pi*i*n) * Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A120594 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (80*x^3)*A(x) + (-1376*x^4 - 1204*x^3)*A'(x) + (-2304*x^5 - 4032*x^4 - 1764*x^3)*A^(2)(x) + (-512*x^6 - 1344*x^5 - 1176*x^4 + 89*x^3)*A^(3)(x) = 0.
%C A120594 Typogeometric interpretation: with A(x)=1+(2)*T(x), T=x+3*T^2+4*T^3+2*T^4. The colored plane constructors have multiplicities {Delta_2: 3, Delta_3: 4, Delta_4: 2}; coefficients count the resulting words by number of true leaves.
%e A120594 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1 (multiplicity 2); 2 true leaves: {1,1} (multiplicity 6); 3 true leaves: {1,{1,1}} (multiplicity 18), {{1,1},1} (multiplicity 18), {1,1,1} (multiplicity 8).
%C A120594 Exact Hermite/direct-x reduction uses a 8 X 8 reduction matrix and a 3 X 4 remainder matrix of rank 3 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120594 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation, reversion/Lagrange formula, and polynomial recurrence are already represented on the current record.

## A120595

Current record: https://oeis.org/A120595

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / Lagrange formula | already present |
| Polynomial recurrence | already present or equivalent normalization |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: 13*A(x)=12+27*x+A(x)^4.
- Lagrange/reversion coefficient content equivalent to: a(n)=d/n * [u^(n-1)] D(u)^(-n), n>=1.
- A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.

### Recommended additions

```text
%F A120595 Contour form: Put rho(u)=u*(1-2*u^1-4*u^2-3*u^3). a(n)=(3)/(2*Pi*i*n) * Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A120595 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (1080*x^3)*A(x) + (-18576*x^4 - 8256*x^3)*A'(x) + (-31104*x^5 - 27648*x^4 - 6144*x^3)*A^(2)(x) + (-6912*x^6 - 9216*x^5 - 4096*x^4 + 451*x^3)*A^(3)(x) = 0.
%C A120595 Typogeometric interpretation: with A(x)=1+(3)*T(x), T=x+2*T^2+4*T^3+3*T^4. The colored plane constructors have multiplicities {Delta_2: 2, Delta_3: 4, Delta_4: 3}; coefficients count the resulting words by number of true leaves.
%e A120595 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1 (multiplicity 3); 2 true leaves: {1,1} (multiplicity 6); 3 true leaves: {1,{1,1}} (multiplicity 12), {{1,1},1} (multiplicity 12), {1,1,1} (multiplicity 12).
%C A120595 Exact Hermite/direct-x reduction uses a 8 X 8 reduction matrix and a 3 X 4 remainder matrix of rank 3 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120595 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation, reversion/Lagrange formula, and polynomial recurrence are already represented on the current record.

## A120596

Current record: https://oeis.org/A120596

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / Lagrange formula | already present |
| Polynomial recurrence | already present or equivalent normalization |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: 6*A(x)=5+1*x+A(x)^5.
- Lagrange/reversion coefficient content equivalent to: a(n)=d/n * [u^(n-1)] D(u)^(-n), n>=1.
- A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.

### Recommended additions

```text
%F A120596 Contour form: Put rho(u)=u*(1-10*u^1-10*u^2-5*u^3-1*u^4). a(n)=(1)/(2*Pi*i*n) * Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A120596 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (1155*x^4)*A(x) + (-31875*x^5 - 159375*x^4)*A'(x) + (-73125*x^6 - 731250*x^5 - 1828125*x^4)*A^(2)(x) + (-31250*x^7 - 468750*x^6 - 2343750*x^5 - 3906250*x^4)*A^(3)(x) + (-3125*x^8 - 62500*x^7 - 468750*x^6 - 1562500*x^5 + 37531*x^4)*A^(4)(x) = 0.
%C A120596 Typogeometric interpretation: with A(x)=1+(1)*T(x), T=x+10*T^2+10*T^3+5*T^4+1*T^5. The colored plane constructors have multiplicities {Delta_2: 10, Delta_3: 10, Delta_4: 5, Delta_5: 1}; coefficients count the resulting words by number of true leaves.
%e A120596 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1; 2 true leaves: {1,1} (multiplicity 10); 3 true leaves: {1,{1,1}} (multiplicity 100), {{1,1},1} (multiplicity 100), {1,1,1} (multiplicity 10).
%C A120596 Exact Hermite/direct-x reduction uses a 10 X 10 reduction matrix and a 4 X 5 remainder matrix of rank 4 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120596 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation, reversion/Lagrange formula, and polynomial recurrence are already represented on the current record.

## A120597

Current record: https://oeis.org/A120597

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / Lagrange formula | already present |
| Polynomial recurrence | already present or equivalent normalization |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: 9*A(x)=8+8*x+A(x)^5.
- Lagrange/reversion coefficient content equivalent to: a(n)=d/n * [u^(n-1)] D(u)^(-n), n>=1.
- A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.

### Recommended additions

```text
%F A120597 Contour form: Put rho(u)=u*(1-5*u^1-10*u^2-10*u^3-4*u^4). a(n)=(2)/(2*Pi*i*n) * Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A120597 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (18480*x^4)*A(x) + (-510000*x^5 - 510000*x^4)*A'(x) + (-1170000*x^6 - 2340000*x^5 - 1170000*x^4)*A^(2)(x) + (-500000*x^7 - 1500000*x^6 - 1500000*x^5 - 500000*x^4)*A^(3)(x) + (-50000*x^8 - 200000*x^7 - 300000*x^6 - 200000*x^5 + 9049*x^4)*A^(4)(x) = 0.
%C A120597 Typogeometric interpretation: with A(x)=1+(2)*T(x), T=x+5*T^2+10*T^3+10*T^4+4*T^5. The colored plane constructors have multiplicities {Delta_2: 5, Delta_3: 10, Delta_4: 10, Delta_5: 4}; coefficients count the resulting words by number of true leaves.
%e A120597 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1 (multiplicity 2); 2 true leaves: {1,1} (multiplicity 10); 3 true leaves: {1,{1,1}} (multiplicity 50), {{1,1},1} (multiplicity 50), {1,1,1} (multiplicity 20).
%C A120597 Exact Hermite/direct-x reduction uses a 10 X 10 reduction matrix and a 4 X 5 remainder matrix of rank 4 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120597 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation, reversion/Lagrange formula, and polynomial recurrence are already represented on the current record.

## A120598

Current record: https://oeis.org/A120598

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / Lagrange formula | already present |
| Polynomial recurrence | already present or equivalent normalization |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: 30*A(x)=29+125*x+A(x)^5.
- Lagrange/reversion coefficient content equivalent to: a(n)=d/n * [u^(n-1)] D(u)^(-n), n>=1.
- A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.

### Recommended additions

```text
%F A120598 Contour form: Put rho(u)=u*(1-2*u^1-10*u^2-25*u^3-25*u^4). a(n)=(5)/(2*Pi*i*n) * Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A120598 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (721875*x^4)*A(x) + (-19921875*x^5 - 4621875*x^4)*A'(x) + (-45703125*x^6 - 21206250*x^5 - 2459925*x^4)*A^(2)(x) + (-19531250*x^7 - 13593750*x^6 - 3153750*x^5 - 243890*x^4)*A^(3)(x) + (-1953125*x^8 - 1812500*x^7 - 630750*x^6 - 97556*x^5 + 10267*x^4)*A^(4)(x) = 0.
%C A120598 Typogeometric interpretation: with A(x)=1+(5)*T(x), T=x+2*T^2+10*T^3+25*T^4+25*T^5. The colored plane constructors have multiplicities {Delta_2: 2, Delta_3: 10, Delta_4: 25, Delta_5: 25}; coefficients count the resulting words by number of true leaves.
%e A120598 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1 (multiplicity 5); 2 true leaves: {1,1} (multiplicity 10); 3 true leaves: {1,{1,1}} (multiplicity 20), {{1,1},1} (multiplicity 20), {1,1,1} (multiplicity 50).
%C A120598 Exact Hermite/direct-x reduction uses a 10 X 10 reduction matrix and a 4 X 5 remainder matrix of rank 4 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120598 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation, reversion/Lagrange formula, and polynomial recurrence are already represented on the current record.

## A120599

Current record: https://oeis.org/A120599

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / Lagrange formula | already present |
| Polynomial recurrence | already present or equivalent normalization |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: 13*A(x)=12+32*x+A(x)^5.
- Lagrange/reversion coefficient content equivalent to: a(n)=d/n * [u^(n-1)] D(u)^(-n), n>=1.
- A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.

### Recommended additions

```text
%F A120599 Contour form: Put rho(u)=u*(1-5*u^1-20*u^2-40*u^3-32*u^4). a(n)=(4)/(2*Pi*i*n) * Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A120599 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (591360*x^4)*A(x) + (-16320000*x^5 - 6120000*x^4)*A'(x) + (-37440000*x^6 - 28080000*x^5 - 5265000*x^4)*A^(2)(x) + (-16000000*x^7 - 18000000*x^6 - 6750000*x^5 - 843750*x^4)*A^(3)(x) + (-1600000*x^8 - 2400000*x^7 - 1350000*x^6 - 337500*x^5 + 14771*x^4)*A^(4)(x) = 0.
%C A120599 Typogeometric interpretation: with A(x)=1+(4)*T(x), T=x+5*T^2+20*T^3+40*T^4+32*T^5. The colored plane constructors have multiplicities {Delta_2: 5, Delta_3: 20, Delta_4: 40, Delta_5: 32}; coefficients count the resulting words by number of true leaves.
%e A120599 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1 (multiplicity 4); 2 true leaves: {1,1} (multiplicity 20); 3 true leaves: {1,{1,1}} (multiplicity 100), {{1,1},1} (multiplicity 100), {1,1,1} (multiplicity 80).
%C A120599 Exact Hermite/direct-x reduction uses a 10 X 10 reduction matrix and a 4 X 5 remainder matrix of rank 4 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120599 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation, reversion/Lagrange formula, and polynomial recurrence are already represented on the current record.

## A120600

Current record: https://oeis.org/A120600

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / Lagrange formula | already present |
| Polynomial recurrence | already present or equivalent normalization |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: 7*A(x)=6+1*x+A(x)^6.
- Lagrange/reversion coefficient content equivalent to: a(n)=d/n * [u^(n-1)] D(u)^(-n), n>=1.
- A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.

### Recommended additions

```text
%F A120600 Contour form: Put rho(u)=u*(1-15*u^1-20*u^2-15*u^3-6*u^4-1*u^5). a(n)=(1)/(2*Pi*i*n) * Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A120600 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (57456*x^5)*A(x) + (-2307456*x^6 - 13844736*x^5)*A'(x) + (-6658200*x^7 - 79898400*x^6 - 239695200*x^5)*A^(2)(x) + (-4153680*x^8 - 74766240*x^7 - 448597440*x^6 - 897194880*x^5)*A^(3)(x) + (-816480*x^9 - 19595520*x^8 - 176359680*x^7 - 705438720*x^6 - 1058158080*x^5)*A^(4)(x) + (-46656*x^10 - 1399680*x^9 - 16796160*x^8 - 100776960*x^7 - 302330880*x^6 + 4856069*x^5)*A^(5)(x) = 0.
%C A120600 Typogeometric interpretation: with A(x)=1+(1)*T(x), T=x+15*T^2+20*T^3+15*T^4+6*T^5+1*T^6. The colored plane constructors have multiplicities {Delta_2: 15, Delta_3: 20, Delta_4: 15, Delta_5: 6, Delta_6: 1}; coefficients count the resulting words by number of true leaves.
%e A120600 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1; 2 true leaves: {1,1} (multiplicity 15); 3 true leaves: {1,{1,1}} (multiplicity 225), {{1,1},1} (multiplicity 225), {1,1,1} (multiplicity 20).
%C A120600 Exact Hermite/direct-x reduction uses a 12 X 12 reduction matrix and a 5 X 6 remainder matrix of rank 5 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120600 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation, reversion/Lagrange formula, and polynomial recurrence are already represented on the current record.

## A120601

Current record: https://oeis.org/A120601

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / Lagrange formula | already present |
| Polynomial recurrence | already present or equivalent normalization |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: 15*A(x)=14+27*x+A(x)^6.
- Lagrange/reversion coefficient content equivalent to: a(n)=d/n * [u^(n-1)] D(u)^(-n), n>=1.
- A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.

### Recommended additions

```text
%F A120601 Contour form: Put rho(u)=u*(1-5*u^1-20*u^2-45*u^3-54*u^4-27*u^5). a(n)=(3)/(2*Pi*i*n) * Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A120601 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (41885424*x^5)*A(x) + (-1682135424*x^6 - 872218368*x^5)*A'(x) + (-4853827800*x^7 - 5033599200*x^6 - 1305007200*x^5)*A^(2)(x) + (-3028032720*x^8 - 4710273120*x^7 - 2442363840*x^6 - 422136960*x^5)*A^(3)(x) + (-595213920*x^9 - 1234517760*x^8 - 960180480*x^7 - 331914240*x^6 - 43025920*x^5)*A^(4)(x) + (-34012224*x^10 - 88179840*x^9 - 91445760*x^8 - 47416320*x^7 - 12293120*x^6 + 533607*x^5)*A^(5)(x) = 0.
%C A120601 Typogeometric interpretation: with A(x)=1+(3)*T(x), T=x+5*T^2+20*T^3+45*T^4+54*T^5+27*T^6. The colored plane constructors have multiplicities {Delta_2: 5, Delta_3: 20, Delta_4: 45, Delta_5: 54, Delta_6: 27}; coefficients count the resulting words by number of true leaves.
%e A120601 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1 (multiplicity 3); 2 true leaves: {1,1} (multiplicity 15); 3 true leaves: {1,{1,1}} (multiplicity 75), {{1,1},1} (multiplicity 75), {1,1,1} (multiplicity 60).
%C A120601 Exact Hermite/direct-x reduction uses a 12 X 12 reduction matrix and a 5 X 6 remainder matrix of rank 5 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120601 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation, reversion/Lagrange formula, and polynomial recurrence are already represented on the current record.

## A120602

Current record: https://oeis.org/A120602

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / Lagrange formula | already present |
| Polynomial recurrence | already present or equivalent normalization |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: 31*A(x)=30+125*x+A(x)^6.
- Lagrange/reversion coefficient content equivalent to: a(n)=d/n * [u^(n-1)] D(u)^(-n), n>=1.
- A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.

### Recommended additions

```text
%F A120602 Contour form: Put rho(u)=u*(1-3*u^1-20*u^2-75*u^3-150*u^4-125*u^5). a(n)=(5)/(2*Pi*i*n) * Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A120602 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (4488750000*x^5)*A(x) + (-180270000000*x^6 - 43264800000*x^5)*A'(x) + (-520171875000*x^7 - 249682500000*x^6 - 29961900000*x^5)*A^(2)(x) + (-324506250000*x^8 - 233644500000*x^7 - 56074680000*x^6 - 4485974400*x^5)*A^(3)(x) + (-63787500000*x^9 - 61236000000*x^8 - 22044960000*x^7 - 3527193600*x^6 - 211631616*x^5)*A^(4)(x) + (-3645000000*x^10 - 4374000000*x^9 - 2099520000*x^8 - 503884800*x^7 - 60466176*x^6 + 4197653*x^5)*A^(5)(x) = 0.
%C A120602 Typogeometric interpretation: with A(x)=1+(5)*T(x), T=x+3*T^2+20*T^3+75*T^4+150*T^5+125*T^6. The colored plane constructors have multiplicities {Delta_2: 3, Delta_3: 20, Delta_4: 75, Delta_5: 150, Delta_6: 125}; coefficients count the resulting words by number of true leaves.
%e A120602 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1 (multiplicity 5); 2 true leaves: {1,1} (multiplicity 15); 3 true leaves: {1,{1,1}} (multiplicity 45), {{1,1},1} (multiplicity 45), {1,1,1} (multiplicity 100).
%C A120602 Exact Hermite/direct-x reduction uses a 12 X 12 reduction matrix and a 5 X 6 remainder matrix of rank 5 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120602 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation, reversion/Lagrange formula, and polynomial recurrence are already represented on the current record.

## A120603

Current record: https://oeis.org/A120603

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / Lagrange formula | already present |
| Polynomial recurrence | already present or equivalent normalization |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: 16*A(x)=15+27*x+A(x)^7.
- Lagrange/reversion coefficient content equivalent to: a(n)=d/n * [u^(n-1)] D(u)^(-n), n>=1.
- A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.

### Recommended additions

```text
%F A120603 Contour form: Put rho(u)=u*(1-7*u^1-35*u^2-105*u^3-189*u^4-189*u^5-81*u^6). a(n)=(3)/(2*Pi*i*n) * Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A120603 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (85926431745*x^6)*A(x) + (-4714309873665*x^7 - 2619061040925*x^6)*A'(x) + (-16309749406545*x^8 - 18121943785050*x^7 - 5033873273625*x^6)*A^(2)(x) + (-13292033432580*x^9 - 22153389054300*x^8 - 12307438363500*x^7 - 2279155252500*x^6)*A^(3)(x) + (-3867194395890*x^10 - 8593765324200*x^9 - 7161471103500*x^8 - 2652396705000*x^7 - 368388431250*x^6)*A^(4)(x) + (-437664515463*x^11 - 1215734765175*x^10 - 1350816405750*x^9 - 750453558750*x^8 - 208459321875*x^7 - 23162146875*x^6)*A^(5)(x) + (-16209796869*x^12 - 54032656230*x^11 - 75045355875*x^10 - 55589152500*x^9 - 23162146875*x^8 - 5147143750*x^7 + 159704067*x^6)*A^(6)(x) = 0.
%C A120603 Typogeometric interpretation: with A(x)=1+(3)*T(x), T=x+7*T^2+35*T^3+105*T^4+189*T^5+189*T^6+81*T^7. The colored plane constructors have multiplicities {Delta_2: 7, Delta_3: 35, Delta_4: 105, Delta_5: 189, Delta_6: 189, Delta_7: 81}; coefficients count the resulting words by number of true leaves.
%e A120603 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1 (multiplicity 3); 2 true leaves: {1,1} (multiplicity 21); 3 true leaves: {1,{1,1}} (multiplicity 147), {{1,1},1} (multiplicity 147), {1,1,1} (multiplicity 105).
%C A120603 Exact Hermite/direct-x reduction uses a 14 X 14 reduction matrix and a 6 X 7 remainder matrix of rank 6 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120603 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation, reversion/Lagrange formula, and polynomial recurrence are already represented on the current record.

## A120604

Current record: https://oeis.org/A120604

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / Lagrange formula | already present |
| Polynomial recurrence | already present or equivalent normalization |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: 24*A(x)=23+64*x+A(x)^8.
- Lagrange/reversion coefficient content equivalent to: a(n)=d/n * [u^(n-1)] D(u)^(-n), n>=1.
- A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.

### Recommended additions

```text
%F A120604 Contour form: Put rho(u)=u*(1-7*u^1-56*u^2-280*u^3-896*u^4-1792*u^5-2048*u^6-1024*u^7). a(n)=(4)/(2*Pi*i*n) * Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A120604 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (7695929180160*x^7)*A(x) + (-551730806784000*x^8 - 198278258688000*x^7)*A'(x) + (-2219107764142080*x^9 - 1594983705477120*x^8 - 286598634577920*x^7)*A^(2)(x) + (-2224480667566080*x^10 - 2398268219719680*x^9 - 861877641461760*x^8 - 103245759133440*x^7)*A^(3)(x) + (-853689174589440*x^11 - 1227178188472320*x^10 - 661525742223360*x^9 - 158490542407680*x^8 - 14239384669440*x^7)*A^(4)(x) + (-143769735266304*x^12 - 258336243056640*x^11 - 185679174696960*x^10 - 66728453406720*x^9 - 11990268971520*x^8 - 861800582328*x^7)*A^(5)(x) + (-10582799417344*x^13 - 22819161243648*x^12 - 20501590179840*x^11 - 9823678627840*x^10 - 2647788380160*x^9 - 380619579648*x^8 - 22797526906*x^7)*A^(6)(x) + (-274877906944*x^14 - 691489734656*x^13 - 745512370176*x^12 - 446530846720*x^11 - 160472023040*x^10 - 34601779968*x^9 - 4145004892*x^8 + 124902511*x^7)*A^(7)(x) = 0.
%C A120604 Typogeometric interpretation: with A(x)=1+(4)*T(x), T=x+7*T^2+56*T^3+280*T^4+896*T^5+1792*T^6+2048*T^7+1024*T^8. The colored plane constructors have multiplicities {Delta_2: 7, Delta_3: 56, Delta_4: 280, Delta_5: 896, Delta_6: 1792, Delta_7: 2048, Delta_8: 1024}; coefficients count the resulting words by number of true leaves.
%e A120604 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1 (multiplicity 4); 2 true leaves: {1,1} (multiplicity 28); 3 true leaves: {1,{1,1}} (multiplicity 196), {{1,1},1} (multiplicity 196), {1,1,1} (multiplicity 224).
%C A120604 Exact Hermite/direct-x reduction uses a 16 X 16 reduction matrix and a 7 X 8 remainder matrix of rank 7 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120604 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation, reversion/Lagrange formula, and polynomial recurrence are already represented on the current record.

## A120605

Current record: https://oeis.org/A120605

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / Lagrange formula | already present |
| Polynomial recurrence | already present or equivalent normalization |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: 25*A(x)=24+64*x+A(x)^9.
- Lagrange/reversion coefficient content equivalent to: a(n)=d/n * [u^(n-1)] D(u)^(-n), n>=1.
- A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.

### Recommended additions

```text
%F A120605 Contour form: Put rho(u)=u*(1-9*u^1-84*u^2-504*u^3-2016*u^4-5376*u^5-9216*u^6-9216*u^7-4096*u^8). a(n)=(4)/(2*Pi*i*n) * Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A120605 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (71227287561830400*x^8)*A(x) + (-6455079759359508480*x^9 - 2420654909759815680*x^8)*A'(x) + (-29539426281817374720*x^10 - 22154569711363031040*x^9 - 4153981820880568320*x^8)*A^(2)(x) + (-35068410631123107840*x^11 - 39451961960013496320*x^10 - 14794485735005061120*x^9 - 1849310716875632640*x^8)*A^(3)(x) + (-16673235078422200320*x^12 - 25009852617633300480*x^11 - 14068042097418731520*x^10 - 3517010524354682880*x^9 - 329719736658251520*x^8)*A^(4)(x) + (-3718899924404797440*x^13 - 6972937358258995200*x^12 - 5229703018694246400*x^11 - 1961138632010342400*x^10 - 367713493501939200*x^9 - 27578512012645440*x^8)*A^(5)(x) + (-408436530921603072*x^14 - 918982194573606912*x^13 - 861545807412756480*x^12 - 430772903706378240*x^11 - 121154879167418880*x^10 - 18173231875112832*x^9 - 1135826992194552*x^8)*A^(6)(x) + (-21124470987030528*x^15 - 55451736340955136*x^14 - 62383203383574528*x^13 - 38989502114734080*x^12 - 14621063293025280*x^11 - 3289739240930688*x^10 - 411217405116336*x^9 - 22029503845518*x^8)*A^(7)(x) + (-406239826673664*x^16 - 1218719480020992*x^15 - 1599569317527552*x^14 - 1199676988145664*x^13 - 562348588193280*x^12 - 168704576457984*x^11 - 31632108085872*x^10 - 3389154437772*x^9 + 79551964831*x^8)*A^(8)(x) = 0.
%C A120605 Typogeometric interpretation: with A(x)=1+(4)*T(x), T=x+9*T^2+84*T^3+504*T^4+2016*T^5+5376*T^6+9216*T^7+9216*T^8+4096*T^9. The colored plane constructors have multiplicities {Delta_2: 9, Delta_3: 84, Delta_4: 504, Delta_5: 2016, Delta_6: 5376, Delta_7: 9216, Delta_8: 9216, Delta_9: 4096}; coefficients count the resulting words by number of true leaves.
%e A120605 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1 (multiplicity 4); 2 true leaves: {1,1} (multiplicity 36); 3 true leaves: {1,{1,1}} (multiplicity 324), {{1,1},1} (multiplicity 324), {1,1,1} (multiplicity 336).
%C A120605 Exact Hermite/direct-x reduction uses a 18 X 18 reduction matrix and a 8 X 9 remainder matrix of rank 8 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120605 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation, reversion/Lagrange formula, and polynomial recurrence are already represented on the current record.

## A120606

Current record: https://oeis.org/A120606

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / Lagrange formula | already present |
| Polynomial recurrence | already present or equivalent normalization |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: 36*A(x)=35+81*x+A(x)^9.
- Lagrange/reversion coefficient content equivalent to: a(n)=d/n * [u^(n-1)] D(u)^(-n), n>=1.
- A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.

### Recommended additions

```text
%F A120606 Contour form: Put rho(u)=u*(1-4*u^1-28*u^2-126*u^3-378*u^4-756*u^5-972*u^6-729*u^7-243*u^8). a(n)=(3)/(2*Pi*i*n) * Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A120606 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (4011058905828975*x^8)*A(x) + (-363508228979510895*x^9 - 157071456966455325*x^8)*A'(x) + (-1663468916430505905*x^10 - 1437565730248585350*x^9 - 310585188633953625*x^8)*A^(2)(x) + (-1974825457913578410*x^11 - 2559958926925009050*x^10 - 1106155091881176750*x^9 - 159322749859428750*x^8)*A^(3)(x) + (-938928468843224055*x^12 - 1622839328864831700*x^11 - 1051840305745724250*x^10 - 302999265029632500*x^9 - 32731402086534375*x^8)*A^(4)(x) + (-209424325596026310*x^13 - 452459962707464250*x^12 - 391014782586697500*x^11 - 168957004821412500*x^10 - 36503056597218750*x^9 - 3154585138031250*x^8)*A^(5)(x) + (-23000496591939678*x^14 - 59630917090213980*x^13 - 64416114140663250*x^12 - 37112164525485000*x^11 - 12027090355481250*x^10 - 2078756357737500*x^9 - 149704675968750*x^8)*A^(6)(x) + (-1189593207657972*x^15 - 3598152294767940*x^14 - 4664271493217700*x^13 - 3359043256432500*x^12 - 1451438444137500*x^11 - 376298855887500*x^10 - 54199423687500*x^9 - 3345643437500*x^8)*A^(7)(x) + (-22876792454961*x^16 - 79080270214680*x^15 - 119596704954300*x^14 - 103355177121000*x^13 - 55824555543750*x^12 - 19297377225000*x^11 - 4169186437500*x^10 - 514714375000*x^9 + 26495939759*x^8)*A^(8)(x) = 0.
%C A120606 Typogeometric interpretation: with A(x)=1+(3)*T(x), T=x+4*T^2+28*T^3+126*T^4+378*T^5+756*T^6+972*T^7+729*T^8+243*T^9. The colored plane constructors have multiplicities {Delta_2: 4, Delta_3: 28, Delta_4: 126, Delta_5: 378, Delta_6: 756, Delta_7: 972, Delta_8: 729, Delta_9: 243}; coefficients count the resulting words by number of true leaves.
%e A120606 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1 (multiplicity 3); 2 true leaves: {1,1} (multiplicity 12); 3 true leaves: {1,{1,1}} (multiplicity 48), {{1,1},1} (multiplicity 48), {1,1,1} (multiplicity 84).
%C A120606 Exact Hermite/direct-x reduction uses a 18 X 18 reduction matrix and a 8 X 9 remainder matrix of rank 8 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120606 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation, reversion/Lagrange formula, and polynomial recurrence are already represented on the current record.

## A120607

Current record: https://oeis.org/A120607

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / Lagrange formula | already present |
| Polynomial recurrence | already present or equivalent normalization |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: 37*A(x)=36+81*x+A(x)^10.
- Lagrange/reversion coefficient content equivalent to: a(n)=d/n * [u^(n-1)] D(u)^(-n), n>=1.
- A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.

### Recommended additions

```text
%F A120607 Contour form: Put rho(u)=u*(1-5*u^1-40*u^2-210*u^3-756*u^4-1890*u^5-3240*u^6-3645*u^7-2430*u^8-729*u^9). a(n)=(3)/(2*Pi*i*n) * Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A120607 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (60765412591845561600*x^9)*A(x) + (-6785005073897406182400*x^10 - 3015557810621069414400*x^9)*A'(x) + (-34765586231546797200000*x^11 - 30902743316930486400000*x^10 - 6867276292651219200000*x^9)*A^(2)(x) + (-47624162850889657200000*x^12 - 63498883801186209600000*x^11 - 28221726133860537600000*x^10 - 4180996464275635200000*x^9)*A^(3)(x) + (-26966441197320817500000*x^13 - 47940339906348120000000*x^12 - 31960226604232080000000*x^11 - 9469696771624320000000*x^10 - 1052188530180480000000*x^9)*A^(4)(x) + (-7475401032758757000000*x^14 - 16612002295019460000000*x^13 - 14766224262239520000000*x^12 - 6562766338773120000000*x^11 - 1458392519727360000000*x^10 - 129634890642432000000*x^9)*A^(5)(x) + (-1089648823126500000000*x^15 - 2905730195004000000000*x^14 - 3228589105560000000000*x^13 - 1913237988480000000000*x^12 - 637745996160000000000*x^11 - 113377065984000000000*x^10 - 8398301184000000000*x^9)*A^(6)(x) + (-84213735183000000000*x^16 - 261998287236000000000*x^15 - 349331049648000000000*x^14 - 258763740480000000000*x^13 - 115006106880000000000*x^12 - 30668295168000000000*x^11 - 4543451136000000000*x^10 - 288473088000000000*x^9)*A^(7)(x) + (-3228504075000000000*x^17 - 11479125600000000000*x^16 - 17856417600000000000*x^15 - 15872371200000000000*x^14 - 8817984000000000000*x^13 - 3135283200000000000*x^12 - 696729600000000000*x^11 - 88473600000000000*x^10 - 4915200000000000*x^9)*A^(8)(x) + (-47829690000000000*x^18 - 191318760000000000*x^17 - 340122240000000000*x^16 - 352719360000000000*x^15 - 235146240000000000*x^14 - 104509440000000000*x^13 - 30965760000000000*x^12 - 5898240000000000*x^11 - 655360000000000*x^10 + 27001782375529*x^9)*A^(9)(x) = 0.
%C A120607 Typogeometric interpretation: with A(x)=1+(3)*T(x), T=x+5*T^2+40*T^3+210*T^4+756*T^5+1890*T^6+3240*T^7+3645*T^8+2430*T^9+729*T^10. The colored plane constructors have multiplicities {Delta_10: 729, Delta_2: 5, Delta_3: 40, Delta_4: 210, Delta_5: 756, Delta_6: 1890, Delta_7: 3240, Delta_8: 3645, Delta_9: 2430}; coefficients count the resulting words by number of true leaves.
%e A120607 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1 (multiplicity 3); 2 true leaves: {1,1} (multiplicity 15); 3 true leaves: {1,{1,1}} (multiplicity 75), {{1,1},1} (multiplicity 75), {1,1,1} (multiplicity 120).
%C A120607 Exact Hermite/direct-x reduction uses a 20 X 20 reduction matrix and a 9 X 10 remainder matrix of rank 9 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A120607 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation, reversion/Lagrange formula, and polynomial recurrence are already represented on the current record.

## A244594

Current record: https://oeis.org/A244594

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / composition identity | already present |
| Coefficient-extraction formula | new |
| Polynomial recurrence | new |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: (4-1*x)*A(x)=3+A(x)^3.
- Series-reversion and composition identities are already present.

### Recommended additions

```text
%F A244594 a(n)=d/n * [u^(n-1)] E(u)^(-n), where x=u*E(u)
%F A244594 Recurrence: (4*n^3 + 2*n^2 - 2*n)*a(n) + (-64*n^3 - 168*n^2 - 136*n - 32)*a(n+1) + (384*n^3 + 1824*n^2 + 2848*n + 1472)*a(n+2) + (-781*n^3 - 5825*n^2 - 14286*n - 11520)*a(n+3) + (52*n^3 + 468*n^2 + 1352*n + 1248)*a(n+4) = 0, for n>=1.
%F A244594 Contour form: Put rho(u)=u*(1-3*u^1-1*u^2)/(1+1*u). a(n)=(1)/(2*Pi*i*n)*Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A244594 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (0)*A(x) + (4*x^5 - 32*x^4 + 64*x^3)*A'(x) + (14*x^6 - 168*x^5 + 672*x^4 - 1139*x^3)*A^(2)(x) + (4*x^7 - 64*x^6 + 384*x^5 - 781*x^4 + 52*x^3)*A^(3)(x) = 0.
%C A244594 Typogeometric interpretation: with A(x)=1+(1)*T(x), T=x+1*x*T+3*T^2+1*T^3. The colored plane constructors have multiplicities {Delta_2: 3, Delta_2_with_one_true_leaf_and_one_subtree: 1, Delta_3: 1}; coefficients count the resulting words by number of true leaves.
%e A244594 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1; 2 true leaves: {1,1} (multiplicity 4); 3 true leaves: {1,{1,1}} (multiplicity 16), {{1,1},1} (multiplicity 12), {1,1,1}.
%C A244594 Exact Hermite/direct-x reduction uses a 6 X 6 reduction matrix and a 2 X 3 remainder matrix of rank 2 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A244594 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation and reversion/composition identities are already represented on the current record.

## A244627

Current record: https://oeis.org/A244627

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / composition identity | already present |
| Coefficient-extraction formula | new |
| Polynomial recurrence | new |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: (5-4*x)*A(x)=4+A(x)^3.
- Series-reversion and composition identities are already present.

### Recommended additions

```text
%F A244627 a(n)=d/n * [u^(n-1)] E(u)^(-n), where x=u*E(u)
%F A244627 Recurrence: (256*n^3 + 128*n^2 - 128*n)*a(n) + (-1280*n^3 - 3360*n^2 - 2720*n - 640)*a(n+1) + (2400*n^3 + 11400*n^2 + 17800*n + 9200)*a(n+2) + (-1568*n^3 - 11590*n^2 - 28158*n - 22500)*a(n+3) + (85*n^3 + 765*n^2 + 2210*n + 2040)*a(n+4) = 0, for n>=1.
%F A244627 Contour form: Put rho(u)=u*(1-3*u^1-2*u^2)/(1+2*u). a(n)=(2)/(2*Pi*i*n)*Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A244627 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (0)*A(x) + (256*x^5 - 640*x^4 + 400*x^3)*A'(x) + (896*x^6 - 3360*x^5 + 4200*x^4 - 2182*x^3)*A^(2)(x) + (256*x^7 - 1280*x^6 + 2400*x^5 - 1568*x^4 + 85*x^3)*A^(3)(x) = 0.
%C A244627 Typogeometric interpretation: with A(x)=1+(2)*T(x), T=x+2*x*T+3*T^2+2*T^3. The colored plane constructors have multiplicities {Delta_2: 3, Delta_2_with_one_true_leaf_and_one_subtree: 2, Delta_3: 2}; coefficients count the resulting words by number of true leaves.
%e A244627 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1 (multiplicity 2); 2 true leaves: {1,1} (multiplicity 10); 3 true leaves: {1,{1,1}} (multiplicity 50), {{1,1},1} (multiplicity 30), {1,1,1} (multiplicity 4).
%C A244627 Exact Hermite/direct-x reduction uses a 6 X 6 reduction matrix and a 2 X 3 remainder matrix of rank 2 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A244627 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation and reversion/composition identities are already represented on the current record.

## A244856

Current record: https://oeis.org/A244856

| Candidate identity | Status against current OEIS record |
|---|---|
| Defining algebraic equation | already present |
| Series reversion / composition identity | already present |
| Coefficient-extraction formula | new |
| Polynomial recurrence | new |
| Contour integral | new |
| Scalar linear ODE | new |
| Typogeometric interpretation | new |
| Brace-word examples | new |
| Reduction matrices / certificate | new; concise comment plus certificate link |

### Already on OEIS in equivalent form

- Defining equation: (5-1*x)*A(x)=4+A(x)^4.
- Series-reversion and composition identities are already present.

### Recommended additions

```text
%F A244856 a(n)=d/n * [u^(n-1)] E(u)^(-n), where x=u*E(u)
%F A244856 Recurrence: (3*(n+1)*(3*n-1)*(3*n+7))*a(n) + (-15*(2*n+3)*(18*n^2+54*n+29))*a(n+1) + (75*(n+2)*(54*n^2+216*n+209))*a(n+2) + (-6750*(n+2)*(n+3)*(2*n+5))*a(n+3) + (491*(n+2)*(n+3)*(n+4))*a(n+4) = 0, for n>=0.
%F A244856 Contour form: Put rho(u)=u*(1-6*u^1-4*u^2-1*u^3)/(1+1*u). a(n)=(1)/(2*Pi*i*n)*Integral_gamma du/rho(u)^n, n>=1 Here gamma is a small positively oriented loop around u=0.
%F A244856 Differential equation: Let A(x)=Sum_{n>=0} a(n)*x^n. Then (-21*x^4 + 105*x^3)*A(x) + (141*x^5 - 1410*x^4 + 3525*x^3)*A'(x) + (162*x^6 - 2430*x^5 + 12150*x^4 - 20250*x^3)*A^(2)(x) + (27*x^7 - 540*x^6 + 4050*x^5 - 13500*x^4 + 491*x^3)*A^(3)(x) = 0.
%C A244856 Typogeometric interpretation: with A(x)=1+(1)*T(x), T=x+1*x*T+6*T^2+4*T^3+1*T^4. The colored plane constructors have multiplicities {Delta_2: 6, Delta_2_with_one_true_leaf_and_one_subtree: 1, Delta_3: 4, Delta_4: 1}; coefficients count the resulting words by number of true leaves.
%e A244856 In the brace-word encoding (1 = true leaf, 0 = false leaf, braces preserve the ordered child slots): 1 true leaves: 1; 2 true leaves: {1,1} (multiplicity 7); 3 true leaves: {1,{1,1}} (multiplicity 49), {{1,1},1} (multiplicity 42), {1,1,1} (multiplicity 4).
%C A244856 Exact Hermite/direct-x reduction uses a 8 X 8 reduction matrix and a 3 X 4 remainder matrix of rank 3 and nullity 1; a kernel vector gives the stated recurrence. The full matrices and rational telescoping certificate are supplied in the linked certificate.
%H A244856 Bradley Klee and Harm.On.ica S-O-L 5.6, <a href="https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory">Exact typogeometric, contour, matrix-reduction, recurrence, and ODE certificate</a>.
```

### Do not resubmit

The algebraic equation and reversion/composition identities are already represented on the current record.
