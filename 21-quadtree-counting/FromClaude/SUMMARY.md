# Executive summary — A120593 quadtree certificate (v10 → v28 → Artifact 21)

## Bottom line

**Yes — I believe the certificate proves what it claims**, for the scope it
actually claims (see "gaps" below). Every mathematically substantive
statement in it was independently recomputed from nothing but the raw
definitions, using at least two different methods per claim, and all of them
agree with each other and with the printed/embedded numbers.

## What was checked, and how

| Claim | Method 1 | Method 2 | Result |
|---|---|---|---|
| a(1..5) = 1,1,6,76,1201,21252 | Direct multinomial-sum brute force | Fixed-point power-series solve of `Q=x+6Q²+4Q³+Q⁴` | Agree exactly |
| `Q=x/D(Q)` ⇒ Lagrange contour form `H_n(u)` | Residue/coefficient-extraction computation | (same numbers as above) | Agrees exactly, n=1..5 |
| P-recurrence `ΣP_r(n)q_{n+r}=0` | Exact integer arithmetic, n=0..11 | — | Holds exactly, no floats |
| Algebraic equation `5A=4+x+A⁴` | Power-series substitution | — | Holds to computed order |
| Differential operator (3rd order, in A(x)) | Differentiated the *same* independently-derived series | — | Holds to computed order |
| Telescoping identity `ΣP_rH_{n+r}=d/du(RH_n)` | Symbolic-in-u, cross-multiplied, cleared denominators (sympy) | Re-verified in exact-rational Python, then ported to Julia | Holds exactly for n=1..8 (see caveat) |
| Printed ink vs. hidden JSON payload | Regex-extracted all 31 `math_svg()` LaTeX calls from the actual build source, diffed against payload's `surface_math` block | SHA-256 of PDF attachment vs. sidecar JSON | 31/31 match; hashes identical |

Everything above was written from scratch — I did not reuse or trust the
artifact's own bundled `verify_layered_pdf.py`/`report.json`; I only read
those afterward, and they reached the same conclusions independently.

## Gaps / things I want to be honest about

1. ~~The telescoping identity was only checked at 8 concrete n.~~ **Closed.**
   Dividing the identity through by `H_n(u)` first avoids the symbolic-power
   issue entirely — `H_{n+r}/H_n` and `H_n'/H_n` both reduce to genuine
   rational functions with no leftover symbolic exponent — and the resulting
   identity is symbolically zero for all `n`, not just the 8 tested points
   (see `check7_symbolic_n_proof.py`). This was the one open item in the
   first pass and it's now a proof rather than a finite check.
2. **I could not visually inspect the rendered PDF pages this session** — the
   image-viewing tool stopped returning content partway through. I compensated
   by diffing the *source that generates the ink* (the LaTeX strings passed to
   `math_svg()`) against the payload, which is arguably a stronger check than
   eyeballing rasterized glyphs, but it doesn't rule out a rendering-layer bug
   between matplotlib mathtext and the final vector paths. Worth a human or a
   working vision pass as final belt-and-suspenders, per the artifact's own
   stated "primary relay boundary" concern.
3. **No Julia runtime exists in this sandbox**, so `verify_A120593.jl` was
   never actually executed by me. I de-risked this by first validating the
   identical algorithm in pure Python (`fractions.Fraction`, no SymPy), then
   transcribing it to Julia line-by-line. Running the `.jl` file yourself
   gives a real independent-implementation execution I don't currently have.
4. **Provenance, not re-derived by me:** the certificate's `provenance` field
   claims independent derivation with no Maple/Mathematica, and cites a
   specific inspected commit of `HBrochet/CreativeTelescoping`. I did not
   audit that repository or verify the provenance claim itself — only that
   the mathematics stands on its own regardless of how it was produced.
5. **Scope boundary, stated by the certificate itself:** it proves the
   generating-function/recurrence/telescoping package for `n≥1` (with `n=0`
   "checked directly," per its own text) — I didn't find any silent
   overreach beyond that stated range.

## What's in this zip

- `SUMMARY.md` — this file.
- `REPORT.md` — the fuller verification report (also dropped in the
  artifact's own `FromClaude/` folder).
- `verify_A120593.jl` — from-scratch Julia port of all five math checks,
  Base-only (`Rational{BigInt}`, hand-rolled polynomials), not yet executed
  by me (see gap #3).
- `mirror_full_check_python_reference.py` — the exact-rational Python
  translation I *did* run, used to validate the Julia logic before writing it.
- `scripts/` — the earlier sympy-based exploratory checks (multinomial,
  Lagrange/residue form, recurrence, differential equation, and three
  iterations of the telescoping-identity check, including the numeric-n
  version that actually worked) — kept for a full audit trail of how I got
  to the final checks.
