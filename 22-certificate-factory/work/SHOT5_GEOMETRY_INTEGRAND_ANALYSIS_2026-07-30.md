# Shot 5 report: explicit geometry and integrand reduction analysis

## Bounds

- Hard shot limit: 15 minutes.
- Per-process limit: 300 seconds and 1024 MiB.
- Active project ceiling: 10,485,760 bytes.
- No family-wide matrix computation was launched.

## 1. Explicit geometric verification

Every target was enumerated through three true leaves in a compact prefix
depth-first word language.

- `l` is a true leaf.
- `Delta_k[c](...)` is a k-child constructor with finite color `c`.
- `root[c](...)` records the shift multiplier `d`, so counts are coefficients
  of A rather than only coefficients of T.
- False leaves are suppressed in the word and recoverable as unused positions
  in the full-slot model.
- `Delta_2m[c](l,T)` is the descendant `x*T` constructor.
- Observable powers use ordered forests, with `false` as the unit component.

Results:

- Cases enumerated: 23/23.
- Published-term comparisons: 69/69 passed for n=1,2,3.
- Explicit elements serialized: 4,854.
- Largest individual set: A120605 at n=3, with 984 elements.
- n=4 was not attempted because several sets grow rapidly and n<=3 already
  supplies a family-wide explicit falsification test within the size limit.

## 2. Integrands

All 23 integrands are written explicitly in `data/integrand_analysis.json`.

- 18 primaries:
  `H_n=d/(n*rho(u)^n)`.
- 2 observable powers:
  `H_n=p*d*(1+d*u)^(p-1)/(n*rho(u)^n)`.
- 3 descendants:
  `H_n=d*h(u)^n/(n*p(u)^n)`, where `rho=p/h`.

## 3. Reduction-algorithm analysis

### Twenty core cases

The q3 term-shift algorithm applies mathematically without alteration to all
18 primaries. Each polynomial `rho` is squarefree; exact nonzero resultants
are recorded as invertibility witnesses for G.

A120589 and A120591 also use the same G/U/V lowering. The only change is that
the initial vector is the coefficient vector of the fixed numerator seed
`(1+d*u)^(p-1)` rather than the vector for 1. Its degree is below q in both
cases.

Therefore 20/20 core cases are ready for a parameterized polynomial
term-shift implementation.

### Three descendants

The term-shift ratio is

    H_(n+s)/H_n = n*h(u)^s / ((n+s)*p(u)^s).

The varying numerator `h(u)^n` means the one-factor q3 G/U/V identity cannot
be copied unchanged. It needs a two-factor Hermite reduction over p and h.

The direct-x route is substantially easier:

    Phi(x,u)=h(u)/(p(u)-x*h(u)).

The denominator `g_x=p-x*h` is polynomial in u, so the q3 direct
G_x/U_x/V_x derivative algorithm applies. Exact discriminants are recorded.
This is the recommended first route to descendant linear ODEs.

## Files changed

- Added `src/enumerate_typogeometries.py`.
- Added `src/analyze_integrand_reductions.py`.
- Added 23 `data/set_elements_n_le_3.json` files.
- Added 23 `data/integrand_analysis.json` files.
- Added `reports/explicit_set_enumeration.json`.
- Added `reports/integrand_reduction_analysis.json`.
- Added `text/GENERALIZED_REDUCTION_PSEUDOCODE.md`.
- Updated all 23 manifests.
- Added this report.

## Checks

- Explicit enumeration versus published terms: 69/69.
- No duplicate words within any recursively generated tree set.
- Polynomial-kernel squarefreeness witnesses: 20/20 relevant core/parent
  kernels nonzero.
- Integrand classification: 23/23.
- Python compilation: pass.
- JSON parsing: pass for the complete project.
- Active project size before final packaging: below 5.5 MiB.

## Blockers and questions

1. The core implementation is engineering-blocked only: parameterize rho and
   the seed vector in the existing term-shift factory.
2. Descendant term-shift certificates need a derived two-factor lowering
   identity; direct-x ODE reduction is not blocked.
3. Should the next shot prioritize:
   - A120592 as the first generalized polynomial term-shift certificate, or
   - A244594 as the first descendant direct-x ODE?

## Proposed next shot

Default: parameterize the current q3 term-shift factory and run A120592 only.
Verify G inverse, every lowering step, nullity one, recurrence residuals, and
the cleared rational certificate. Stop before the rest of the family.
