# A181785 — dual BFS enumerator

Counts free lattice-convex polyominoes:

\[
\operatorname{conv}(P)\cap\mathbb Z^2=P,
\]

with translation, rotation, and reflection identified.

`--mode both` runs two independent breadth-first generators against the same
integer-only hull/closure utility:

1. **Fast recurrence.** Expand only accepted order-\(n\) shapes by one edge
   square; retain a child only if it is already lattice-convex.
2. **Forward-completion BFS.** Expand completed shapes by one edge square.
   When the child is non-convex, replace it by its exact lattice closure
   \(\operatorname{conv}(P)\cap\mathbb Z^2\), schedule that completed shape
   into its later-size bucket, and expand it normally when that bucket is
   reached.

The buckets are consumed in increasing size, but future buckets can be filled
raggedly from earlier levels. Workers only parallelize *inside* one frozen source
level; their local maps merge before the next level begins.

## Run from Go source

You are already in the project root when `ls` shows `go.mod`, `cmd`, and
`internal`. The source entry point is **not** `.`:

```bash
go run ./cmd/a181785 --mode both --max-n 24 --workers 10 \
  | tee output/both_n24_w10.txt
```

For all fourteen logical CPUs reported by the machine:

```bash
go run ./cmd/a181785 --mode both --max-n 24 --workers 14 \
  | tee output/both_n24_w14.txt
```

Build once for repeated runs:

```bash
go build -o bin/a181785-linux-amd64 ./cmd/a181785
./bin/a181785-linux-amd64 --mode both --max-n 24 --workers 10
```

The source has no third-party dependencies. Check Go first with:

```bash
go version
```

## Normal `both` output

The normal report is a fixed 80-column terminal table. The last output line is
an unlabelled comma-separated sequence suitable for pasting directly into the
OEIS search box.

```text
A181785 dual BFS | horizon=12 | workers=1 of 14 logical CPUs
--------------------------------------------------------------------------------
 n |       a(n) | check |   promoted | jump |   >horizon |   fast(s) |   full(s)
--------------------------------------------------------------------------------
 ...
--------------------------------------------------------------------------------
all checks OK | fast=... | full=... | total=...
OEIS copy/paste (n=1..12):
1,1,2,5,10,25,48,107,193,365,621,1082
```

Column meanings:

- `a(n)`: one authoritative count; it is printed only after the two methods
  have agreed for that order.
- `promoted`: in-horizon extension events whose closure gained at least one
  additional square. It is an event count, not an additional-shape count.
- `jump`: maximum forced completion size beyond the ordinary one-square child,
  including candidates dropped beyond the horizon.
- `>horizon`: closures deliberately dropped because their completed size
  exceeds `--max-n`.
- `fast(s)` and `full(s)`: time spent expanding that source level in the fast
  and completion engines. The final row is `--` because the horizon bucket is
  reported but not expanded.

A mismatch exits nonzero at the first disagreement, for example:

```text
CHECK FAIL at n=18: fast=14210 complete=14213
```

## Other modes

```bash
# Shared integer hull utility checks
go run ./cmd/a181785 --mode test

# Fast recurrence only (CSV output)
go run ./cmd/a181785 --mode fast --max-n 28 --workers 10

# Completion BFS only (detailed CSV audit)
go run ./cmd/a181785 --mode complete --max-n 24 --workers 10
```

## Exact shared core

`internal/poly/poly.go` contains the proof-critical common utility:

- monotone-chain convex hull,
- exact lattice totals using Pick's theorem, including segment cases,
- explicit lattice closure rasterization checked against its Pick count,
- edge-connectivity verification after closure,
- D4 + translation canonicalization.
