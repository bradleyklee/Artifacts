# Project charter

## Mission

Build a general, auditable computational instrument for period equations and
exact differential certificates attached to plane and sphere geometries. The
instrument should cover every declared geometry until the only remaining
failures are genuine computational limits: memory overflow or timeout.

Once that coverage threshold is reached, the machinery can be exported into
chemistry and physics applications.

## First-class entities

### 1. Geometries and data

Every example has a stable `case_id`, exact model, conventions, parameter
normalization, generated series, modular data, ranks, timings, failures, and
links to certificates. Raw run data is immutable. Derived summaries may be
regenerated.

### 2. Algorithms and pseudocode

Implementations and language-neutral pseudocode are maintained together.
Whenever an algorithm succeeds on a new class of examples, its registry and
pseudocode success notes are updated. When no registered algorithm solves a
case, that gap triggers a new implementation and a new pseudocode candidate.

### 3. Certificates

A raw machine certificate is required whenever deductive work is performed.
Raw certificates also record bounded failures and computational blockers. A
crystalline success is promoted to a pretty-print certificate for human review.

### 4. Coverage

Coverage is measured across explicitly declared geometry domains, not by a
handful of favorite examples. Reports separate exact success, inductive
pattern, partial reduction, computational limit, method gap, and not-applicable
states.

### 5. Comparison backends

Independent tools, including Pierre Lairez's approach, remain independently
callable. Comparison uses common inputs, canonical output normalization,
mathematical verification, stage-level timing, and explicit workload labels.
No backend is silently substituted for another.

### 6. Principal-investigator metadata

Procedures, decisions, failed approaches, successful heuristics, and lessons
learned are recorded to prevent drift. The metadata must keep future work
locked onto the coverage-to-computational-limit goal.

## Non-negotiable rules

- Preserve original research ownership and privacy; NO POACHING.
- Use `H_p` for the Hamiltonian derivative/function; do not repurpose `E_p`.
- Never discard raw data, partial certificates, failed bounds, timeout state,
  or the last verified object.
- Never call a pattern a theorem without an exact deductive verification.
- Never call a timing comparison fair unless workloads and environments match.
- Completion precedes global optimization and final refactoring.
- Refactoring must preserve branch provenance and regression behavior.
