# Ranked-memory workload performance baseline

Environment: local container, Go 1.23.2, AMD EPYC 9V74, 5 logical CPUs available to process.

The authoritative raw output is in `verification/workload-performance-baseline.txt`.

Interpretation:
- Insert/update: skip-list includes maintenance of the ordered secondary index; map baseline updates only the primary unordered map.
- Single page: skip-list pops K already-ranked entries; map baseline collects and sorts all current entries before returning K.
- Full drain map_snapshot sorts once and walks a stable snapshot; map_resort recomputes order on every page.
- Absolute timings are machine-specific; ratios and scaling shape are the intended evidence.
