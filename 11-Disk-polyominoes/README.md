# Exact disk-polyomino enumerator (C++)

This is a self-contained compiled implementation of the current experimental
enumerator for OEIS A147680.

It keeps a shape only when a circle can contain exactly its lattice sites:
all selected points are inside or on the circle, and every immediate exterior
lattice neighbor is strictly outside.  The circle test tries **every pair** of
selected points as a chord.  For each chord, all circles through that pair form
a pencil whose centers lie on the perpendicular bisector.  The implementation
uses exact integer/rational comparisons to test the permitted intervals of that
pencil.  It does not use floating-point geometry.

## Build

```sh
make
```

Requires a C++20 compiler.  Recent GCC and Clang work; no third-party library
is required.

## Run

Ordinary hereditary growth: each level is one-square extensions of successful
shapes from the preceding level.

```sh
./disk_polyomino --max-n 50 --depth 1 --csv depth1_n50.csv
```

Depth-two growth: at target order `n`, use the union of

1. one-square extensions of accepted order `n-1`, and
2. two-square extensions of accepted order `n-2`.

The intermediate `n-1` shape in the two-step route is **not** required to be
accepted.  This is precisely the requested recovery channel for a valid shape
whose one-square predecessor might fail.

```sh
./disk_polyomino --max-n 50 --depth 2 --csv depth2_n50.csv
```

Verify against the OEIS prefix currently recorded through `n = 21`:

```sh
./disk_polyomino --max-n 21 --depth 1 --verify-oeis
./disk_polyomino --max-n 21 --depth 2 --verify-oeis
```

The CSV records, per order, the `+1` candidate count, the independently
constructed `+2` candidate count, their deduplicated union, lattice-convex
survivors, accepted disks, and elapsed seconds.

## Important status

This is an experimental generator, not a proof of hereditary completeness.
`--depth 2` is intentionally present to test whether a disk can be recovered
through a two-cell extension even when every one-cell route is missing.
