# Rewrite / adversarial-check brief

This is a deliberately small exact-dynamics artifact. A fresh implementation
should be able to reproduce each public statement without relying on any prior
messages or hidden state.

## What to rebuild first

1. Implement fixed-orientation regular polygons with edge `1/2` and support
   normals documented in every JSON `model.face_normals` array.
2. Work exactly in `Q(sqrt(2),sqrt(3))` or in an equivalent exact subfield.
   It is acceptable to use specialised `Q`, `Q(sqrt(2))`, and `Q(sqrt(3))`
   implementations, but all results must serialize in the common four-slot
   coefficient basis `(1,sqrt(2),sqrt(3),sqrt(6))`.
3. Reproduce the event rule from `docs/EXPERIMENT_CONTRACT.md`: enumerate all
   body--wall and body--body candidates, select the globally earliest positive
   time, classify all same-time contacts as one batch, and never serialize a
   shared-body batch.
4. Read one v2 full certificate in isolation and replay it from its embedded
   model/container/instance. Check every exact time, contact, and post-state.
5. Only after certificate parity, rebuild an atlas in its recorded raw order and
   compare its complete status counts and earliest-case fields.

## Minimum adversarial checks

* Test normal directions and cardinal support widths independently.
* Confirm the central dodecagon time-zero collision is closing before applying
  the collision map.
* Test a valid disjoint same-time batch and a shared-body same-time batch;
  they must receive different classifications.
* Confirm that all negative statements are statements about named, exhaustive,
  finite families, not claims about every possible initial condition.
* Confirm 24-gon classes `(E,S)` and `(W,N)` at sites `[0,1]` swap under direct
  velocity negation.
* Confirm dodecagon face labels are reduced mod 3 only after pair contacts are
  selected; wall contacts do not emit ternary symbols.

## Success criterion

A rewrite is credible when it independently regenerates the committed atlas
counts, replays all highlighted full certificates, regenerates the ternary CSV,
and renders the same event-indexed visual inputs from the checked JSON.
