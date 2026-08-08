# Algorithms directory

- `pseudocode/` contains language-neutral descriptions of the inductive,
  reductive, deductive, quotient-audit, primitive-verification, and reusable
  reduction stages.
- `src/core/` contains the smallest set of reusable Python modules selected
  from the working packets.
- `src/benchmark/` contains the frozen mixed-quartic benchmark generator and
  summarizer.  `run_benchmark.py` is preserved from the original environment
  and contains path assumptions; use it as an execution record until the
  portable runner is completed.
- `scripts/verify_transfer.py` validates this curated transfer packet.

The authoritative frozen execution environments are retained under
`../source_archives/`.
