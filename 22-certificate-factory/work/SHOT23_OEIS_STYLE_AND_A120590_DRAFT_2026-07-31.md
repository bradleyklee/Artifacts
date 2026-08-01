---
shot: 23
date: 2026-07-31
scope: OEIS Style Sheet and live A120590 draft revision 31
status: complete
time_limit: 15 minutes
---

# OEIS style and A120590 live-draft pass

## Sources checked

- OEIS Style Sheet: https://oeis.org/wiki/Style_Sheet
- OEIS AI policy: https://oeis.org/wiki/Use_of_AI_for_OEIS_Submissions
- Live work-in-progress draft: https://oeis.org/draft/A120590, revision 31,
  Bradley Klee, Jul 31 2026.

## Violations found in the previous local deltas

- Formula, Comment, and Example contributions lacked the required signature
  and date placeholder. They now end with `. - ~~~~`.
- Several contour formulas used ambiguous slash placement such as
  `du/rho(u)^n`. They now use `Integral_gamma 1/(rho(u)^n) du` and fully
  parenthesized prefactors.
- The three descendant coefficient formulas contained undefined `d` and
  `E(u)`. They now state `rho(u)` explicitly and use
  `[u^(n-1)](u/rho(u))^n` with the numerical prefactor substituted.
- Companion recurrences and descendant ODEs displayed redundant zero terms.
  Those terms are now omitted.
- The Links lines named an AI system as a co-author. OEIS explicitly prohibits
  claiming an AI tool as author or co-author. The links now name Bradley Klee
  as the human author. The separate PDF certificates retain the requested
  `Mech.An.ika Sol (Open AI)` affiliation line.
- Typogeometric examples were too long and did not use the compact
  multiplicity convention from the live draft. They now use the human-readable
  `{,},0,1` alphabet with adjacent `(*m)` multiplicities.

## Tightening adopted from the live A120590 draft

- Short `Hermite reduction` comments followed by the proof-certificate link.
- Direct `Typogeometry: From A(x)=... write T=...` language.
- `Integral:` and `ODE:` labels.
- Compact typogeometric examples such as `{1,1} (*3)`.
- One human-authored certificate link per A-number.

## Live-draft issues not propagated

1. The draft currently says `a(1)=3` for `{1,1}` and `a(2)=19` for the
   three-leaf objects. With offset 0 and published terms
   `1,1,3,19,...`, these should be `a(2)=3` and `a(3)=19`.
2. The draft contour text uses `du/rho(u)^n`, which is ambiguous under the
   Style Sheet's slash rule. Prefer `1/(rho(u)^n) du`.
3. The draft contribution signatures render immediately after the terminal
   period in parentheses. The canonical local deltas use the documented
   `. - ~~~~` contribution form.

## Final local audit

- Cases: 23/23.
- Field lines: 146.
- Signed Formula/Comment/Example lines: 123/123.
- Human-authored Links lines: 23/23.
- Non-ASCII mathematical text: 0.
- Undefined `d` or `E(u)`: 0.
- Lowercase matrix-dimension `x`: 0.
- AI systems named as OEIS authors: 0.
- Mechanical style findings remaining: 0.

The audit is recorded in `reports/oeis_style_audit.json` and can be repeated
with `python3 src/check_oeis_style.py`.

## Case states, blockers, and next shot

- Mathematical case states: unchanged; 23/23 certificate-ready.
- Blockers: none in the local package. The three live-draft points above
  require manual correction in OEIS before submission for review.
- Proposed next shot: after the A120590 draft is edited, compare its next
  revision against this canonical text before generalizing further edits.
