# P^4 consistent extraction

This extraction regenerates the exact reports for levels 1–4 and preserves a
restartable, staged exact search at level 5. Human-facing objects use labeled
quadtree braces: `0` is empty, an integer is an occupied labeled leaf, and
`{a,b,c,d}` has children in `NW, SW, SE, NE` order.

## Install and verify

Install Python 3, NumPy, and SciPy, then run:

```bash
make verify
```

Reports can be regenerated with:

```bash
make reports
```

## Carry results from the previous extraction

Do not rerun the completed 30-second pass. Import its checkpoint directory:

```bash
make import-search FROM=/full/path/to/23-problem-statement/search
make status
```

The importer copies JSONL checkpoints without overwriting local files. If a
filename collision contains different data, it keeps both files under a stable
imported name. `make status` deduplicates overlapping two-worker and ten-worker
layouts by class ID; an `optimal` or `infeasible` result always supersedes an
earlier `timeout`.

## Push only the current timeouts

After importing the earlier run, the normal next command is:

```bash
make push WORKERS=10 TIME_LIMIT=120 HEARTBEAT=10
```

This automatically:

1. reads every checkpoint in `search/`;
2. combines duplicate class records from old shard layouts;
3. selects only classes whose best current status is `timeout`;
4. divides that remainder over the requested workers;
5. streams serialized progress in the main terminal;
6. writes a separate restart-safe retry stage.

When the 120-second pass finishes, inspect the remainder:

```bash
make status
```

Then push only the timeouts that still remain:

```bash
make push WORKERS=10 TIME_LIMIT=600 HEARTBEAT=30
```

The default stage name comes from `TIME_LIMIT`, so these runs write separate
files such as:

```text
search/retry_t120s_shard_00_of_10.jsonl
search/retry_t600s_shard_00_of_10.jsonl
```

Repeating exactly the same `make push` command resumes that stage and skips all
cases already attempted there. A different worker count is also safe: the
runner checks every file belonging to that stage before assigning work.

For two distinct passes with the same time limit, name the stages explicitly:

```bash
make push WORKERS=10 TIME_LIMIT=600 STAGE=second_600s
```

## Initial level-5 run

A clean search can still start from the frozen unresolved queue:

```bash
make level5 WORKERS=10 TIME_LIMIT=30 HEARTBEAT=10
```

For an existing search, use `make push`; do not repeat the initial pass.

## Progress and status

All terminal and saved progress lines are limited to 80 columns. Parallel
worker output is serialized and prefixed in the main terminal:

```text
[W03] [18/56] id=1484 tag=314a2cf9ac running elapsed=20s limit=120s
```

Per-worker logs remain under `logs/`. Follow them separately with:

```bash
make logs
```

The status report distinguishes raw records from the deduplicated current
state:

```text
[raw] files=22 records=3502
[current] unique=2811
[current] optimal=...
[current] infeasible=...
[current] timeout=...
```

Only the `[current] timeout` count is queued by the next `make push` command.

## Useful commands

```bash
make help
make verify
make reports
make status
make level5-smoke WORKERS=2
make push-smoke WORKERS=2
```

## Important files

- `src/p4_solver.py`: exact MILP solver.
- `src/resume_level5.py`: initial and staged timeout runner.
- `src/search_status.py`: deduplicated search summary.
- `src/import_search.py`: safe checkpoint importer.
- `src/generate_reports.py`: brace-coded report generator.
- `src/verify_extraction.py`: extraction consistency checks.
- `results/n5_manifest.tsv`: frozen level-5 class manifest.

## Status boundary

Levels 2–4 are exact under the implemented first-resolution model. Level 5 is
not complete. This package records an exact lower bound and a reproducible
checkpoint; it does not claim that 6 is the finished fifth term.
