# Change log

- Added one complete-case manifest for models 1, 2, 3, 5, 7, and 9.
- Added `verify_complete_cases.py` as the public exact verifier.
- Kept the two older verifier commands as wrappers around the same engine.
- Added exact annihilator, recurrence, and initial-coefficient comparisons for
  all six complete cases.
- Added automatic 80-column curve-catalogue printing and exact JSON output.
- Reordered and simplified the README and release report around final status.
- Moved development history and workflow provenance under `internal/`.
- Added tests showing the old and new commands select the same exact checks.
- Moved the canonical search command to `code/search_curves.py`; retained
  `code/run_model_search.py` as a compatibility wrapper.
- Removed parenthetical details from verifier stage messages to prevent wraps.
- Printed catalogue Hamiltonians below their metadata rows with blank spacing.
- Added a deterministic listing of all 52 invariant models found by the
  default search, including presentation counts and representative parameters.
- Recorded every presentation beneath its invariant model in the search JSON.
