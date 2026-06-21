# Disk polyominoes: recorded counts, exact test, and checks

This folder contains a C++20 search for **disk polyominoes**: finite
square-lattice point sets that are exactly the lattice sites contained in some
closed Euclidean disk.  It is an experimental record for
[OEIS A147680](https://oeis.org/A147680), not a proof that the hereditary
search is complete at every recorded order.

## What is being counted

The program represents a polyomino as a finite, 4-connected set of occupied
lattice sites $P \subseteq \mathbb{Z}^2$.  The unit-square drawing of a
polyomino is only a visualization; the recognition problem is about the point
set $P$ itself.

A candidate passes when there are a center $C \in \mathbb{R}^2$ and a radius
$r \geq 0$ such that, for every lattice site $z$,

$$
z \in P \iff (z_x-C_x)^2+(z_y-C_y)^2 \leq r^2.
$$

The program tests every occupied site for inclusion and the immediate
unoccupied 4-neighbor fence for exclusion.  It first applies a necessary
lattice-convexity screen: a disk must contain every lattice site in the
Euclidean convex hull of $P$.

## Recorded count sequence

The executable emits orders $n \geq 1$.  If the empty polyomino is included,
prepend $a(0)=1$.

Both recorded hereditary modes give the following same accepted-count column
through $n=50$:

| orders $n$ | recorded counts $a(n)$ |
|---|---|
| 1–10 | 1, 1, 1, 2, 2, 2, 1, 2, 2, 3 |
| 11–20 | 3, 4, 4, 4, 4, 4, 4, 3, 3, 4 |
| 21–30 | 5, 6, 6, 7, 7, 7, 6, 7, 7, 8 |
| 31–40 | 8, 8, 8, 7, 7, 6, 7, 7, 7, 7 |
| 41–50 | 8, 9, 11, 12, 12, 12, 11, 12, 12, 12 |

The machine-readable runs are:

- [`results/depth1_n50.csv`](results/depth1_n50.csv)
- [`results/depth2_n50.csv`](results/depth2_n50.csv)

The values through $n=21$ match the OEIS prefix embedded in the source.  The
values from $n=22$ through $n=50$ are this artifact's recorded search output;
they are not presented as a proven complete extension.

## Recognition method

For each unordered pair of occupied sites $A,B$, the program considers the
entire pencil of circles through $A$ and $B$.  The center moves along the
perpendicular bisector of $AB$.  With rational coordinate $t$ on that line,
the difference between the squared distance of a lattice site $X$ and the
squared radius of the circle has the form

$$
d_X(t)=\alpha_X+\beta_Xt.
$$

The quadratic terms cancel.  Therefore each selected site imposes a closed
rational interval condition on $t$, while each immediate exterior site imposes
a strict rational interval condition.  Intersecting these conditions decides
whether this pair supplies a witness circle.

This release tests **all unordered pairs of occupied sites**, not merely hull
vertices or exposed boundary sites.  That is deliberately conservative: a
boundary-pair reduction is plausible, but it is not required for the recorded
counts in this package.

All geometry decisions use signed 128-bit integer expressions and exact
rational comparisons.  No floating-point comparison decides acceptance.  This
claim is conditional on intermediate products fitting in signed `__int128`;
the program does not add an overflow guard for arbitrarily large future runs.

## How the counts were checked

There are three different checks in the package.  They are useful evidence,
but none replaces a completeness proof.

1. **Published-prefix check.** Both `--depth 1` and `--depth 2` reproduce the
   embedded OEIS A147680 prefix through $n=21$.  Fresh package logs are stored
   in [`results/package_depth1_verify_n21.txt`](results/package_depth1_verify_n21.txt)
   and [`results/package_depth2_verify_n21.txt`](results/package_depth2_verify_n21.txt).

2. **Recovery-depth check.** Depth 1 and depth 2 have identical accepted-count
   columns through $n=50$.  Depth 2 is deliberately more permissive: at order
   $n$ it adds all two-square extensions of accepted order $n-2$ shapes, even
   when their intermediate order $n-1$ form was not accepted.  Agreement means
   that this added recovery channel did not change the recorded counts through
   the tested range.

3. **Exact witness arithmetic.** Every acceptance decision is an exact rational
   interval-feasibility decision.  The circle comparison does not depend on a
   sampled curve, a tolerance, or a floating-point optimization routine.

The first two are cross-checks of the program's output.  They are **not** an
independent enumeration of all possible polyominoes at every order, and they do
not prove that depth 3 or deeper recovery could never add a new shape.

## Enumeration modes

The search canonically identifies shapes under the eight symmetries of the
square lattice.

- `--depth 1` builds order $n$ from one-square extensions of accepted order
  $n-1$ shapes.
- `--depth 2` takes the deduplicated union of those extensions with all
  two-square extensions of accepted order $n-2$ shapes.

At order $50$, depth 1 tested 243 candidates and depth 2 tested 2,506.  Both
accepted 12.  In the fresh package rebuild on the supplied Linux x86_64 runner,
complete runs through $50$ took 1.18 seconds and 8.39 seconds respectively.
See [`BENCHMARKS.md`](BENCHMARKS.md) for the timing record.

## Small-order witness gallery

This code-drawn figure compares circles with translated axis-aligned ellipses
for every free triomino, tetromino, and pentomino accepted by at least one of
those two models.  It is included as a visual check on lattice-site semantics,
not as part of the disk count proof.

![Exact circle and axis-aligned ellipse witnesses for small polyominoes](results/circle_vs_axis_ellipse_tri_tet_pent.png)

The vector version is [`results/circle_vs_axis_ellipse_tri_tet_pent.svg`](results/circle_vs_axis_ellipse_tri_tet_pent.svg).
Each plotted curve comes from exact rational data; the curve is sampled with
floating point only for drawing.  The equations, centers, radii, and failed
fence sites are listed in
[`results/circle_vs_axis_ellipse_tri_tet_pent_certificates.md`](results/circle_vs_axis_ellipse_tri_tet_pent_certificates.md).

## Build and run

```sh
make

# One-square hereditary growth.
./disk_polyomino --max-n 50 --depth 1 --csv depth1_n50.csv

# One-square growth plus two-square recovery.
./disk_polyomino --max-n 50 --depth 2 --csv depth2_n50.csv

# Compare against the embedded OEIS prefix through n = 21.
./disk_polyomino --max-n 21 --depth 1 --verify-oeis
./disk_polyomino --max-n 21 --depth 2 --verify-oeis
```

A C++20 compiler is required.  The code uses no third-party C++ library.
