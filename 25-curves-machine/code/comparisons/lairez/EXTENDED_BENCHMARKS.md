# Extended exact comparison

Date: 2026-08-02. Research owner: Bradley Klee. Unpublished; NO POACHING.

Every completed row uses exact rational arithmetic and compares the normalized
operator coefficient-for-coefficient. Timings are single-threaded wall times
on the same Python 3.12.13 / SymPy 1.14.0 environment.

| case | degree | order | Lairez-style port | Klee exact-image | comparison |
|---|---:|---:|---:|---:|---|
| square only | 4 | 2 | 1.586 s median total (3 runs) | 2.973 s median total (3 runs) | port 1.87x faster |
| triangle--square | 4 | 2 | 2.572 s median total (3 runs) | 9.972 s median fixed-support derivation (3 runs) | port 3.88x faster |
| triangle--square bounded discovery | 4 | 2 | same run already tests derivative order 1 | 23.237 s (1 run) | port faster; Klee lower-order exclusion remains bounded |
| hexagon only | 6 | 4 | 32.013 s total (1 run) | 112.631 s total at weighted bound 35 (1 run) | port 3.52x faster |
| square--hexagon | 6 | 4 | 160.627 s total (1 run) | 61.11 s median full derivation (3 runs) | Klee 2.63x faster |
| triangle--hexagon | 6 | not reached | bounded run: derivative 2 = 49.888 s, derivative 3 = 83.847 s; stopped during derivative 4 | not run | scaling probe only |

The Klee rows return and exactly verify explicit primitives: 17 terms for
square-only, 71 for triangle--square, 120 for hexagon-only, and 514 terms for
square--hexagon. The current Lairez-style port returns identical operators and
retains quotient ledgers, but does not yet assemble them into final primitives.

Certificate-enabled quartic runs refine that last statement. Square-only and
triangle--square now return globally verified affine homotopy one-forms; the
triangle certificate costs about 2.41 seconds to assemble after reduction.
Square--hexagon retains the structured seven-step homotopy ledger, but global
one-form canonicalization exceeded the 360-second total run bound.

The separated hybrid bridge reconstructs the canonical Klee primitive from a
Lairez-derived operator. On triangle--square it returns exactly the stored
71-term numerator coefficient-for-coefficient. Initial hybrid totals are about
2.26 seconds for square-only and 10.7--11.1 seconds for triangle--square.

## Interpretation

There is a real crossover, not a universal winner. Cached projective Jacobian
profiles are excellent on the small quartics and the pure hexagon. The
support-driven method wins decisively on the mixed square--hexagon, where its
symmetry-restricted exact-image matrix is 53 by 47 while the port repeatedly
constructs and solves degree-10 Jacobian maps with a 131 by 131 profile.

The pure hexagon also falsifies the idea that polynomial degree alone predicts
the winner: it has the same degree and order as square--hexagon, but the port
wins. Relevant predictors include Jacobian-map rank defect, symmetry-sector
support size, coefficient growth, and the cost of expression canonicalization.

For triangle--square, the earlier 39.94-second number is retired as a speed
comparison: it was a verbose stored-certificate trace. The lean from-scratch
kernel supplies the valid 9.972-second median. A stricter bounded order-first
search takes 23.237 seconds.
