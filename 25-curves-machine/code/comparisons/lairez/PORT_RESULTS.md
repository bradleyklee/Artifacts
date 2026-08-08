# SymPy port: first showcase results

Date: 2026-08-02  
Research owner: Bradley Klee  
Privacy: unpublished research; NO POACHING.

Algorithmic attribution: the projective Jacobian pole reduction and its place
inside the period algorithm follow Griffiths--Dwork and Pierre Lairez,
*Computing periods of rational integrals*, Math. Comp. 85 (2016), 1719--1752.

## Triangle--square: exact success

Input:

```text
2H = p^2 + q^2 + q^3 - 3p^2q
     + (p^4 - 6p^2q^2 + q^4)/4
ambient rational period = 2/(2H-alpha)
```

The independent projective reduction port found its first relation at order 2:

```text
P0 = 408 alpha^3 + 645 alpha^2 - 261 alpha + 27
P1 = 1632 alpha^4 + 5736 alpha^3 - 2827 alpha^2
     + 426 alpha - 18
P2 = alpha(alpha+6)(4alpha-1)(8alpha-1)(17alpha-3)
```

These are exactly the three coefficients in the existing triangle--square
certificate. This verifies all of the following independently:

1. the ambient Poincare-residue adapter and its factor 2;
2. homogenization of the rational integral;
3. parameter differentiation convention;
4. projective Jacobian pole reduction;
5. primitive normalization of the resulting Ore operator.

Measured baseline:

```text
curve degree:                 4
Groebner basis size:          12
reduced class rows:           2
derivatives through closure:  2
certificate-ledger steps:     3
setup:                        0.082 s
profiled fraction-free reduction: 2.503 s
```

The current ledger retains the original-gradient quotients at every reduction
step. It does not yet propagate their alpha derivatives into a single returned
primitive, so the operator comparison is closed but the primitive/gauge
comparison remains the next coding step.

## Square--hexagon: exact success

Input:

```text
2H = p^2 + q^2 - 2p^2q^2 + p^2(p^2-3q^2)^2/4
ambient rational period = 2/(2H-alpha)
```

Measured behavior:

```text
curve degree:                    6
Groebner basis size:             17
setup:                            0.131 s
exact reductions through order 4: 160.496 s
first relation found:             order 4
operator comparison:              exact coefficient-for-coefficient match
certificate-ledger steps:         7
```

The port now caches a generic rank profile (evaluated at `alpha=101`) and uses
fraction-free solves over `QQ[alpha]`, with exact full-row verification. The
large map has shape 136 by 198 and rank 131; its selected square solve is 131
by 131. This is directly inspired by Lairez's profile-reuse strategy, though
it is still not a complete transcription of his Rham--Koszul and modular
machinery.

Only about 23 seconds across the four large solves was spent in fraction-free
linear algebra. The 108.584-second fourth reduction is dominated by SymPy
expression construction and canonicalization. Thus 160.496 seconds is a real
timing of this exact port, not an estimate of Magma's original implementation.

## Certificate comparison status

```text
triangle-square operator:   exactly identical
triangle-square primitive:  ledger present, assembly pending
square-hexagon operator:    exactly identical
square-hexagon primitive:   seven-step ledger present, assembly pending
```

This is already a useful methodological comparison. The two methods see the
same minimal two-dimensional derivative-class space in the quartic example.
The Klee support-driven exact-image method currently remains faster on the
square--hexagon sextic (61.11-second median), and returns the assembled
primitive. Pierre's profiled approach has nevertheless been given a genuine
exact run and closes on the same deductive operator.
