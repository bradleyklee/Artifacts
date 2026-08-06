# Changelog v3 — classification-first repair

- Restored the missing Miranda/Persson configuration generator at
  `code/classification/generate_configurations.py`.
- Restored the full 379-case audit and the 279 allowable-configuration ledger.
- Made the generated 59-case four-fibre slice, rather than an unexplained JSON
  table, the explicit input to the 56-target Herfurtner scan.
- Added exact regression checks for the counts
  `379 -> 293 -> 279` and `85 -> 69 -> 59 = 56 + 3`.
- Replaced the mandatory pytest invocation with standard-library `unittest`, so
  `python3 code/run_release_checks.py` no longer fails when pytest is absent.
- Moved the tacnode calculation out of the default release-check pipeline; it is
  retained only as an auxiliary experiment.
- No new plane model or Laurent polynomial is claimed in this repair.

- Promoted the eleven retained exact models into a printable canonical catalog.
- Added `code/run_model_search.py` with default progress reporting, an exact
  bounded cubic search, rechecking of the eight structured-quartic witnesses,
  JSON recording, and a final table headed by Kodaira fiber codes.
- The first cubic box `[-3,3]^4 \ {0}` found 236 exact presentations and 44
  invariant triples in the three already known cubic fiber codes.  It found no
  twelfth fiber configuration.  Equivalence among the invariant triples remains
  a separate check.
