# Quartic certificate drill: orientation and new Q2 results

Date: 2026-08-02 (America/Chicago)

## Bottom line

The transfer packet was internally coherent and reproducible.  Its largest
explicit squarefree-generic gap was the absence of a characteristic-zero
order-6 certificate for the fully asymmetric model `q2_generic_no_reflection`.
That gap is now closed for the test model.

We reconstructed the exact order-6 operator, verified it independently on the
exact rational period series, solved for a polynomial primitive by a shifted
energy recurrence, and verified the complete sparse exact-differential identity

```text
A_6(omega) = d(V / E_p^11).
```

This does **not** yet solve every quartic.  The degenerate-at-infinity fallback,
a unified portable command, and direct reductive interpolation of the operator
remain open.

## Orientation to the transferred project

The work has four logically separate layers.

1. **Finite source support.**  For a squarefree homogeneous quartic leading
   part, the exhaustive primitive support bound is `B_r = 6r - 3`.
2. **Rank/minimal-order detection.**  For Q2, orders 1 through 5 fail and order
   6 succeeds at the certified bounds, at independent modular evaluations.
3. **Characteristic-zero reconstruction.**  This was the main missing Q2 step.
4. **Exact differential verification.**  This turns an annihilating operator
   into a human- and machine-checkable certificate.

The packet had layers 1 and 2.  The present drill completes layers 3 and 4 for
Q2.

## Result 1: exact order-6 operator

Model:

```text
E = p^2 + q^2
  + (3 p^4 + 2 p^3 q - 4 p^2 q^2 + p q^3 + 5 q^4)/12
  + (p^3 - 2 p^2 q + p q^2 + 3 q^3)/15.
```

Operator format:

```text
A_6 = P_0(alpha) + P_1(alpha) D_alpha + ... + P_6(alpha) D_alpha^6.
```

Exact reconstruction data:

- order: 6;
- degree bound used: 31;
- 224 scalar coefficients;
- 71 CRT primes;
- 260 training equations per prime;
- 80 held-out equations passed at every prime;
- all primes selected the same normalization column;
- normalized rational-vector SHA-256:
  `d0298a493398e6a5fa888cc62a60322cd6574fa313bbd4382f01c3470a94de83`;
- primitive integer-vector SHA-256:
  `4eefd9937938b00cbbb23f04fdc04cd9a01c61657f98e135a28e3fbcead5dbd5`.

Independent characteristic-zero period-series verification passed all 94
available equations.  The coefficient degrees are exactly

```text
25, 26, 27, 28, 29, 30, 31
```

for `P_0,...,P_6`.  There are 202 nonzero coefficients; the largest primitive
integer coefficient has 176 digits.

## Result 2: singularity factor audit

The leading coefficient factors as

```text
P_6(alpha) = constant * alpha * Q_8(alpha) * R_22(alpha).
```

Eliminating `p,q` from

```text
E_p = 0,  E_q = 0,  E - alpha = 0
```

gives exactly `alpha * Q_8(alpha)`.  Thus:

- the degree-9 factor is the critical-value polynomial;
- the degree-22 factor is apparent for this scalar order-6 operator.

This separates geometric singular values from scalar-elimination artifacts.

## Result 3: exact primitive and full certificate

The certified squarefree support bound at order 6 is `B_6 = 33`.
The triangular primitive source has 130 columns.  One column is the known
constant-primitive kernel, leaving a gauge-fixed rank-129 system.

The successful method shifts energy to `beta = alpha - 7`.  The exact-image
matrix has degree 2 in `beta`, so one constant rational matrix is inverted and
then the primitive is recovered coefficient-by-coefficient:

```text
A_0 v_k = b_k - A_1 v_(k-1) - A_2 v_(k-2).
```

Certificate statistics:

- ambient rows: 146;
- source columns: 130;
- exact rank after gauge: 129;
- omitted gauge monomial: `q^33`;
- primitive denominator: `E_p^11`;
- primitive alpha degree: 32;
- nonzero primitive source blocks: 129;
- expanded primitive terms: 3736;
- maximum source weight: 33;
- maximum primitive numerator digits: 226;
- maximum primitive denominator digits: 47;
- full 146-row rectangular identity: pass;
- independent sparse identity verifier: pass;
- certificate JSON SHA-256:
  `3ee761be09eed4458ee41d5155cd60ab12b849bca6e8270b2510e00eafa1610e`.

The support by alpha degree collapses at the top:

```text
alpha^24: 129 blocks
alpha^25: 122
alpha^26: 106
alpha^27:  90
alpha^28:  74
alpha^29:  58
alpha^30:  42
alpha^31:  18
alpha^32:   3
alpha^33 and above: 0
```

That exact termination is the key reason the shifted recurrence is preferable
to a monolithic polynomial nullspace solve.

## Result 4: a safe alpha-degree bound

A coarse but finite alpha-degree bound can be obtained directly from the
squarefree reduction matrix.

For a quartic reduced in `p`:

- every exact-image source column has alpha degree at most 2;
- derivative column `j` at order `r` has alpha degree at most
  `floor((6r - 4j)/4) = floor(3r/2) - j`.

The first statement follows because an unreduced exact-image column has
`p`-degree at most 9, so quartic reduction introduces at most two powers of
`alpha`.  For the second, the derivative numerator has `p`-degree at most
`2j`, multiplication by `E_p^(2(r-j))` adds `6(r-j)`, and quartic reduction
converts each four powers of `p` into at most one power of `alpha`.

At the certified support `B_r=6r-3`, the source contains `24r-14` columns,
one of which is the constant-primitive kernel.  After gauging it out, signed
maximal minors of the nullity-one combined matrix give a polynomial kernel
vector.  Let

```text
h_r = floor(3r/2),
S_r = sum_(j=0)^r (h_r-j).
```

Then a safe bound is

```text
primitive coordinate degree <= 2(24r-16) + S_r,
operator coordinate j degree <= 2(24r-15) + S_r - (h_r-j).
```

For `r=6` this gives

```text
primitive coordinates <= 298,
operator coordinates <= 297,
uniform projective bound D_6 = 298.
```

Therefore 597 generic energy evaluations are sufficient for a completely
safe rational projective interpolation scheme.  This is deliberately loose;
the observed Q2 operator degree is 31 and primitive degree is 32.  Still, it
removes the logical objection that the reductive-only interpolation stage had
no finite alpha-degree cap.

Scope qualification: this bound assumes the current monic-in-`p` quartic
backend, the squarefree support theorem, the constant-kernel gauge, and a
nullity-one first relation.  It is not yet a degenerate-infinity bound.

## Revised engineering estimates

These remain implementation-maturity estimates, not theorem probabilities.
The most defensible update is:

```text
Pipeline architecture:              88%   (was 85)
Exact certificate layer:            92%   (renamed; now includes dense order 6)
Generic squarefree quartics:         90%   (was 80)
Broad benchmark/data factory:        75%   (unchanged)
Deductive-only quartic workflow:     70%   (was 55)
All quartics, degenerate included:   60%   (unchanged)
Portable polished implementation:    55%   (was 50)
Quintic extension:                   25%   (unchanged)
```

Why the squarefree line is not 100%: the exact certificate is for one dense
asymmetric model, not a symbolic family with arbitrary quartic coefficients;
the safe interpolation bound is not yet turned into a robust modular
reductive interpolator.

Why the deductive-only line is not higher: the primitive is now obtained by a
pure exact reduction recurrence, and a finite interpolation bound exists, but
the operator in this run was reconstructed from period-series data rather than
from reductive evaluations alone.

## Remaining high-value drill targets

1. **Direct reductive interpolation.**  Use the new degree bound as a hard cap,
   but stop adaptively near the observed degree.  Reconstruct the order-6
   projective relation from modular reduction at many energy values, without
   period series.
2. **Degenerate infinity.**  Stratify `Disc(F_4)=0` by successive cubic,
   quadratic, linear, and constant bands and derive a finite fallback source
   recurrence for each stratum.
3. **Portable command.**  Remove the remaining hard-coded working-directory
   assumptions and expose model -> ranks -> operator -> primitive -> verify as
   one resumable CLI.
4. **Regression corpus.**  Make this Q2 certificate the heavy exact regression
   test and retain the low-order examples as fast tests.

The first target closes the methodological gap.  The second is the only route
to honestly raising the “all quartics” percentage.
