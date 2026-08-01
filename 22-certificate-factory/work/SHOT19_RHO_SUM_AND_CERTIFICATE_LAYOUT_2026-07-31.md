---
shot: 19
date: 2026-07-31
scope: 23 concise calculus certificates
status: complete
time_limit: 15 minutes
---

# Rho, sum notation, and certificate-layout quality pass

## Changes

- Defined the contour kernel near the top of every certificate as
  `rho(u)=...`, followed by `x=rho(T(x))`. Companion cases use the stored
  polynomial `D` through the explicit convention `rho(u)=u D(u)`.
- Recast binomial/multinomial closed forms using the named finite index sets
  `K_n` or `K_{n,h}`. All tuple domains, weighted-degree constraints, and the
  abbreviation `K=sum k_j` are now explicit before the summand.
- Recast companion convolutions with `p(n)=[x^n]A_parent(x)` and explicit
  nonnegative summation indices.
- Started the telescoper certificate on a new line after the matrices, with a
  visible `Certificate.` label. The certificate's denominator now refers to
  the already-defined `rho`.
- Preserved the accepted enlarged matrix type, fraction display style, row
  spacing, inline typogeometric multiplicities, and all canonical mathematics.

## Statistical coverage and checks

- Case states: 23/23 rebuilt and verified; 0 blocked; 0 incomplete.
- Individual layout: 23/23 are one-page PDFs; 0 overfull-box warnings.
- Aggregate layout: 24 pages (cover plus 23 certificates).
- Arithmetic audit: 552 stored terms, 138 published terms, and 430 recurrence
  instances checked; all pass.
- Visual spot checks: A120590 (standard polynomial kernel) and A244856
  (rational kernel and descendant sum) pass for rho placement, sum legibility,
  matrix spacing, certificate separation, and inline tree multiplicities.

## Blockers

None.

## Proposed next shot

Freeze certificate typography and perform only a publication-facing copy edit
of labels and explanatory prose. Do not change formulas, matrices, recurrence
data, ODE data, or typogeometric multiplicities unless a new mathematical
discrepancy is identified.
