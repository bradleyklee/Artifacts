# Selected release evidence

This directory contains selected raw measurements retained for RC1.
Scratch runs, timed-out larger enumerations, superseded representation
benchmarks, and historical algorithm experiments are deliberately excluded.

- `external-exhaustive-suite.txt` — deterministic external suite evidence.
- `external-full-test-b1.txt` — full B1 external test run.
- `graded-graph-b1-n26.txt` — B1 graded reachable-state census through n=26.
- `benchmark-b1-arena-go1.23.2.txt` — allocation/benchmark evidence for B1.
- `workload-performance-baseline.txt` — pre-optimization ranked-memory workload.
- `workload-performance-b1-arena.txt` — optimized ranked-memory workload.
- `go-fuzz-3s.txt` — short fuzz evidence (supplementary to deterministic tests).
- `go-vet-b1.txt` — B1 vet evidence.

The current uncached RC gate output is under `release-evidence/rc1/`.
