# Exact disk-polyomino enumerator (C++)

This artifact contains an exact-arithmetic, experimental enumerator for
[OEIS A147680](https://oeis.org/A147680): free square-lattice polyominoes whose
occupied lattice sites are exactly the lattice points of a closed Euclidean disk.

A candidate is a finite 4-connected set of occupied sites.  The circle test
requires every occupied site to be inside or on the circle and every immediate
unoccupied 4-neighbor to be strictly outside.  The test is about lattice sites,
not the union-of-unit-squares outline.

All geometric acceptance decisions use signed 128-bit integer expressions and
exact rational interval bounds.  No floating-point comparison decides whether a
candidate passes.  This is exact provided intermediate products remain within
`__int128`; the code does not dynamically guard against overflow at arbitrary
future sizes.

## Small-order comparison figure

The following figure is generated from exact lattice-site data and exact rational
circle/ellipse certificates.  It shows every free triomino, tetromino, and
pentomino accepted by at least one of two models: closed Euclidean disks and
translated axis-aligned ellipses.  Green curves pass their model's inclusion
criterion.  Red circles are best near-fits from the exact occupied-pair pencil
search; their red hollow sites are immediate exterior sites that the circle still
includes or touches.

![Exact circle and axis-aligned-ellipse witnesses for all small accepted shapes](results/circle_vs_axis_ellipse_tri_tet_pent.png)

The SVG is better for inspection and zooming:
[`results/circle_vs_axis_ellipse_tri_tet_pent.svg`](results/circle_vs_axis_ellipse_tri_tet_pent.svg).
The equations and exact rational certificates are recorded in
[`results/circle_vs_axis_ellipse_tri_tet_pent_certificates.md`](results/circle_vs_axis_ellipse_tri_tet_pent_certificates.md).

The figure is a small-order comparison artifact.  It does not turn the
axis-aligned-ellipse search into a theorem or alter the disk enumerator's
recognition predicate.

## Circle recognition

For every unordered pair of occupied sites `A, B`, the program tests the full
pencil of circles through them.  Their centers lie on the perpendicular bisector
of `AB`.  With a rational parameter `t` along that bisector, the comparison
between an arbitrary site `X` and a boundary site `A` has the form

$$
\lVert X-c(t)\rVert^2-\lVert A-c(t)\rVert^2=\alpha+\beta t.
$$

The quadratic terms cancel.  Each occupied site supplies a closed rational
half-line in `t`; each immediate exterior site supplies a strict rational
half-line.  The program intersects these conditions exactly.  A nonempty
interval is a circle witness for that pair.

Before the pencil test, a lattice-convex hull screen rejects a necessary class
of failures: a disk must contain every lattice point in the Euclidean convex
hull of its occupied sites.

## Inductive enumeration

The program grows canonical free polyominoes under the eight square symmetries.

- `--depth 1` extends accepted order `n-1` shapes by one square.
- `--depth 2` takes the deduplicated union of those one-square extensions and
  two-square extensions of accepted order `n-2` shapes.  The intermediate
  order `n-1` shape on the two-step route need not itself be accepted.

Both modes still subject every generated candidate to the full lattice-convex
screen and exact pair-pencil test.

## Status

This is a research enumerator, not a completeness proof.  In particular, the
following are open proof obligations:

- Does every disk polyomino occur through one of the retained predecessor
  routes?
- Does every disk polyomino have a witness circle through one tested occupied
  pair?
- Can increasing recovery depth change the reported counts by recovering a disk
  polyomino whose shallower predecessor was not retained?

The program reproduces its embedded OEIS prefix through `n = 21` in both depth
modes.  Recorded depth-1 and depth-2 runs agree through `n = 50`; this is
experimental evidence, not a proof.

## Build

```sh
make
```

Requires a C++20 compiler.  Recent GCC and Clang work; no third-party C++
library is required.

## Run

```sh
# Ordinary one-step hereditary growth.
./disk_polyomino --max-n 50 --depth 1 --csv depth1_n50.csv

# One-step growth plus the two-step recovery channel.
./disk_polyomino --max-n 50 --depth 2 --csv depth2_n50.csv

# Check the embedded OEIS prefix through n = 21.
./disk_polyomino --max-n 21 --depth 1 --verify-oeis
./disk_polyomino --max-n 21 --depth 2 --verify-oeis
```

The CSV output records candidate counts, lattice-convex survivors, accepted
disks, and elapsed seconds by order.  See `BENCHMARKS.md` for the recorded
local baseline through `n = 50`.
