# Work Manifest: Certificate Factory Expansion

## Read this first

This repository is the current certificate-factory artifact. Work in bounded
shots of at most 15 minutes. At the end of every shot, stop, summarize what
changed, list generated files and checks, and state the next mathematical or
engineering question. Do not continue grinding through a blocker without
reformulating.

## Immediate objective

Refactor the factory into a manifest-driven multi-case system whose first data
target is the complete machine-readable certificate payload. Preserve the
existing q3/A120590 release candidate and its mathematics.

The renderer is downstream. It must transcribe verified data; it must not infer
or repair missing mathematics.

## Verified target scope

### Closed original block: 20 targets

A120588 through A120607, inclusive.

This contains 18 primary algebraic series and two observable-power companions:

- A120589 is the power companion of A120588.
- A120591 is the power companion of A120590.

### Verified direct composition descendants: 3 targets

- A244594, descended from A120590.
- A244627, descended from A120592.
- A244856, descended from A120593.

Total strict queue: 23 targets.

Do not include A245009 or A245043. Earlier inclusion was caused by search-result
context contamination; no explicit family relationship was verified.

Broader Hanna series-reversion and composition sequences belong in a separate
future discovery queue, not this certification run.

Canonical target data are also stored in `work/targets.json`.

## Required repository migration

Rename verified example directories by OEIS A-number rather than q-label when
the mapping is certain. Preserve the old q-label as an alias in metadata.
Never guess a mapping: report uncertainty and stop that migration item.

Each case should converge on this standard structure:

    examples/Axxxxxx/
      manifest.json
      CHECKLIST.md
      input/case_spec.json
      data/terms.json
      data/inverse_map.json
      data/coefficient_formula.json
      data/matrices.json
      data/recurrence.json
      data/certificate.json
      data/ode.json
      data/tree_model.json
      checks/expectations.json
      checks/results.json
      checks/validation.log
      text/certificate.md
      text/pseudocode.md
      text/notes.md
      release/payload.json
      release/certificate.pdf
      provenance/generation.json
      provenance/SHA256SUMS.txt

Missing or blocked data must be represented by a file with an explicit status,
not by an absent path.

## Component states

Use only:

- not_attempted
- running
- produced
- verified
- blocked
- not_applicable
- rejected

Top-level case states:

- NEW
- GENERATING
- PARTIAL
- BLOCKED
- ANALYTIC_COMPLETE
- CERTIFICATE_READY
- RELEASED
- INVALID

## Tree-model policy

Tree models are expected to be the difficult part. Analytic completion must not
be blocked by tree-model failure.

Attempt at most three automatic tree approaches in one work shot:

1. Expand the defining equation in Y=A-1 and inspect multinomial coefficients.
2. Seek a literal or finitely colored plane-tree grammar from node arities and
   multiplicities.
3. Compare the resulting profile formula with Lagrange/multinomial coefficients.

Then classify the result as one of:

- literal_unweighted
- colored_unweighted
- weighted_positive
- signed_or_rational
- candidate_unverified
- not_found
- structurally_impossible_under_current_grammar

Every attempt must record the proposed grammar, derived functional equation,
first coefficients tested, and first mismatch or unresolved integrality issue.
Do not spend a second shot on the same failed grammar without a new idea.

## Fixed data expectations

Canonical locations:

- parameters: `input/case_spec.json`
- terms: `data/terms.json`
- inverse map: `data/inverse_map.json`
- coefficient formula: `data/coefficient_formula.json`
- exact matrices and bases: `data/matrices.json`
- recurrence: `data/recurrence.json`
- telescoping certificate: `data/certificate.json`
- differential equation: `data/ode.json`
- tree interpretation: `data/tree_model.json`
- expected checks: `checks/expectations.json`
- results: `checks/results.json`
- human transcription: `text/certificate.md`
- compact machine payload: `release/payload.json`

Generate `CHECKLIST.md` from manifests and check results. Do not maintain it by
hand.

## Stop conditions

Stop the current case or shot and report a blocker when any of these occurs:

- identity_unverified
- normalization_ambiguous
- coefficient_formula_failed
- inverse_map_not_regular_at_origin
- matrix_construction_failed
- kernel_not_found_within_bounds
- kernel_nonunique
- recurrence_failed_term_check
- certificate_residual_nonzero
- ode_translation_failed
- minimality_unresolved
- tree_model_weighted_only
- tree_model_not_found
- rational_kernel_unsupported
- resource_limit
- internal_inconsistency

A blocker report must include attempts, exact bounds, the smallest failing input,
observed residual or rank, and the decision or new theorem required.

## Work-shot cadence

No uninterrupted work shot may exceed 15 minutes. Each shot must return with:

1. files changed or generated;
2. checks run and exact outcomes;
3. cases advanced and their new states;
4. blockers or ambiguities;
5. the proposed next shot.

Do not launch a long family-wide computation until the current shot's migration
or pilot checks have been reviewed.

## Resource policy

- Default case wall-time limit: 5 minutes.
- Default per-process address-space limit: 1024 MiB.
- Hard work-shot limit: 15 minutes.
- Active project ceiling: 10 MiB (10,485,760 bytes), checked before generation.
- Generate one case per process. Do not retain duplicate run directories in the
  active project after their verified knowledge is canonicalized.
- On timeout, memory failure, signal, or size refusal, write a compact forensic
  JSON record under `reports/forensics/`. It must include the limits, elapsed
  time, last observed stage, output tail, peak child RSS when available, and
  project sizes before and after the attempt.
- A resource failure advances no mathematical status. Preserve the forensic
  record and return with the smallest unresolved case and a proposed bound or
  algorithm change.

Use `src/bounded_case_runner.py` for new case computation. Reformat or archive
only when it reduces ambiguity or active size; do not reorganize for appearance.

## Ordered plan

### Shot 1: infrastructure migration only

- Create schemas/manifests and canonical case paths.
- Verify q-to-A mappings for existing q2-q5 examples.
- Rename only verified mappings.
- Generate empty standard files and CHECKLIST.md from status data.
- Preserve all existing mathematics and validate migrated q3 content.
- Stop at the first mapping ambiguity or after 15 minutes.

### Shot 2: four-case analytic pilot

Use A120588, A120590, A120593, and A120596. Generate standard analytic data and
payloads. Do not fabricate tree models. Report dimension changes, failed
assumptions, and any nonminimal recurrence/ODE issues.

### Shot 3: tree-model pilot

Attempt the bounded tree policy on the same four cases. Stop and reformulate
when the three allowed approaches are exhausted.

### Later shots

Only after review of the pilots, parallelize the remaining core targets. Handle
A244594, A244627, and A244856 in a separate queue requiring rational or
cleared-denominator inverse-map support.

## First action in a new Work window

Inspect this manifest, `work/targets.json`, and the repository tree. Then perform
Shot 1 only. Do not begin bulk certificate generation in the first shot.
