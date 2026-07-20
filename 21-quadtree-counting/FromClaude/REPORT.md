# Independent verification report — Artifact 21 (A120593 certificate)

**Scope:** cross-layer transcription (surface ink vs. hidden payload) and
independent mathematical re-derivation. Code was written from scratch, not
adapted from `verification/verify_layered_pdf.py` — I read that script only
after finishing mine, to keep the two checks genuinely independent.

## 1. Container / integrity

- `Artifact21_Certificate.pdf`, `payload/certificate.json`,
  `verification/verify_layered_pdf.py`, `verification/report.json` all match
  `SHA256SUMS` exactly.
- The PDF's embedded attachment `a120593_certificate.json` is **byte-identical**
  (same SHA-256) to `payload/certificate.json`. No silent payload substitution.

## 2. Cross-layer transcription (surface vs. payload)

`payload/certificate.json` now carries a `surface_math` block: canonical LaTeX
for every equation the builder emits via `math_svg(...)`. I extracted all 31
`math_svg(r'...')` call strings straight from `source/build_certificate_spread.py`
by regex, in document order, and diffed them one-for-one against
`surface_math.page_1` + `surface_math.page_2`.

**Result: 31/31 exact string matches, zero mismatches.** This is the strongest
version of this check available without OCR/vision: it compares the actual
source that generates the ink, not a re-reading of the ink.

(Note: I couldn't get the image-viewing tool to render pages for me this turn,
so I did not additionally eyeball the rasterized PDF pages against this text —
worth doing as a belt-and-suspenders pass if that tool comes back online,
per the artifact's own README, which correctly flags this as the one
remaining "ordinary presentation assumption.")

## 3. Independent mathematical re-derivation

Five checks, each recomputing a consequence from nothing but the certificate's
stated formulas — no numbers borrowed from `report.json` or the source's own
`audit_payload_matches_print()` asserts:

1. **Multinomial closed form → initial values.** Brute-force summed
   `a(n) = Σ (n+i+j+k-1)!·6^i·4^j / (n!i!j!k!)` over `i+2j+3k=n-1` for
   `n=0..5`. Matches `1,1,6,76,1201,21252` exactly (exact integer arithmetic).
2. **P-recurrence.** Extended the multinomial sequence to `n=0..14` and checked
   `Σ_r P_r(n)·q_{n+r} = 0` holds exactly (integers, not floats) for every `n`
   in that range.
3. **Algebraic equation.** Solved `Q = x+6Q²+4Q³+Q⁴` by fixed-point iteration
   as an exact-rational power series, set `A=1+Q`, and confirmed
   `5A = 4+x+A⁴` holds identically as a truncated power series, and that `Q`'s
   coefficients agree with the multinomial values.
4. **Differential operator.** Differentiated that same independently-derived
   `A(x)` series three times and confirmed the claimed ODE
   `(256x³+3072x²+12288x−491)A''' + (1152x²+9216x+18432)A'' + (688x+2752)A' − 40A = 0`
   holds to the computed order. This ties the ODE to the *same* series used
   for check 3, rather than trusting the two are consistent by construction.
5. **Creative-telescoping identity — now proved for symbolic n.** Dividing
   the identity through by `H_n(u)` before simplifying avoids the earlier
   `powsimp` limitation entirely: `H_{n+r}/H_n` collapses to the closed form
   `[n/(n+r)]·u^(-r)·D(u)^(-r)` (r is a concrete small integer, so no symbolic
   exponent combination is ever needed), and `H_n'/H_n = -n(1/u + D'/D)`.
   Substituting both into the identity and clearing denominators gives a
   **fully symbolic-in-(n,u) polynomial identity whose numerator sympy reduces
   to exactly zero** — not a finite check, an actual proof for all n. Verified
   this directly (see `check7_symbolic_n_proof.py`) and cross-checked it
   against 10 concrete integer substitutions, all zero, consistent with the
   earlier n=1..8 cross-multiplication check. This closes the one gap flagged
   in the first pass of this review.

**All five checks pass.**

## 4. Julia code

`verify_A120593.jl` in this folder is a from-scratch Julia port of exactly the
above five checks, using only `Base` (`Rational{BigInt}`, hand-rolled dense
polynomial arithmetic) — nothing to `Pkg.add`.

**Honesty note:** this sandbox has no Julia runtime and no route to install one
(the network allowlist here covers pypi/npm/crates/apt security updates, not
julialang.org), so I could not execute `verify_A120593.jl` myself. To de-risk
that, I first hand-translated the same algorithm into plain Python using only
`fractions.Fraction` (no SymPy) — `mirror_full_check_python_reference.py` — ran
it, and got all five checks passing with results identical to the sympy-based
checks above. I then transcribed that validated logic into Julia, keeping the
same variable-by-variable structure (padd/pmul/pderiv/etc.) so the translation
risk is just syntax, not algorithm. If you or Hadrien run `verify_A120593.jl`
directly, that gives a genuine independent-implementation execution, which
I'd treat as a stronger check than my say-so.

```sh
julia verify_A120593.jl
```

should print all five checks and `ALL CHECKS PASS: true`.

## Bottom line

Surface ink and hidden payload agree exactly everywhere checked; the
combinatorics, the algebraic/functional equation, the P-recurrence, the
differential equation, and the rational telescoping certificate are all
mutually consistent under independent recomputation, and check #5 is now a
fully symbolic proof rather than a finite check. The remaining qualification
is presentation-layer only (matplotlib-rendered vector paths vs. the LaTeX
that generated them), matching the artifact's own README.
