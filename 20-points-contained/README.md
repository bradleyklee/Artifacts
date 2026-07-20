# A295344: fixed-radius lattice circles

This artifact computes OEIS A295344: the maximum number of integer lattice
points inside or on a closed circle of integer radius `n`.  The production
algorithm fixes one boundary point at the origin and sweeps the circle center
through one square-lattice symmetry sector.  Exact row, region-overlap, and
flood implementations provide independent checks.

## Layout

```text
src/a295344_sweep.cpp    production sweep
src/a295344.cpp          exact row and flood methods
src/a295344_regions.cpp  independent center-region method; optional OpenMP
tools/benchmark.py       row/flood comparison
tools/benchmark_regions.py
data/records.csv         terms and longest maximizing chords through n=300
data/benchmark.csv
data/benchmark_regions.csv
GLOBAL_BLURB.md          repository-index description
```

## Build and run

From the artifact root:

```text
g++ -O3 -march=native -std=c++17 src/a295344_sweep.cpp -o a295344_sweep
./a295344_sweep 300
```

Arguments are `LAST [FIRST]`.  Output is

```text
n  a(n)  longest_chord_squared  seconds
```

Build the verification programs with:

```text
g++ -O3 -march=native -std=c++17 src/a295344.cpp -o a295344
g++ -O3 -march=native -std=c++17 src/a295344_regions.cpp -o a295344_regions
g++ -O3 -march=native -std=c++17 -fopenmp \
    src/a295344_regions.cpp -o a295344_regions_omp
```

## Circular sweep

Fix the boundary lattice point `(0,0)`.  A radius-`n` circle through it has
center

```text
c(theta) = n*(cos(theta),sin(theta)).
```

For another lattice point `p=(a,b)`, inclusion is equivalent to

```text
|p|^2 <= 2*n*p dot (cos(theta),sin(theta)).
```

Only points with `0 < |p| <= 2n` can enter.  Each normally contributes two
frontier events, one entry and one exit.  By square-lattice symmetry it is
enough to sweep `0 <= theta <= pi/4`.

Each point stores its change of state:

| Event | Exact-event bonus | Persistent differential |
|:------|------------------:|------------------------:|
| entry | +1 | +1 |
| exit | 0 | -1 |
| diameter tangency | +1 | 0 |

Events with the same center are grouped.  Because the disk is closed, the
exact event count is evaluated before exits are applied.  Between consecutive
events the count is constant, so one initial count plus these differentials
finds the global maximum without recounting any disk.

The event coordinates are quadratic surds.  A long-double angle proposes their
order only.  Every adjacent distinct pair must then be separated by an exact
dyadic slope comparison.  The certificate uses signed `__int128` arithmetic
and a small built-in 256-bit product comparator.  If any proposed order cannot
be certified, the program aborts instead of returning a term.  The fixed-width
certificate has been bounded and tested for the supplied range `n <= 300`.

For every count maximum, the program retains the largest `a^2+b^2` among all
simultaneous boundary chords attaining that count.  Thus `records.csv` gives a
longest maximizing chord, not an enumeration-order witness.

## Completeness

Center positions are periodic modulo `Z^2`, and the count is invariant under
the dihedral symmetries of the square lattice.  The count is constant in each
cell of the finite boundary-circle arrangement.  The closure of a maximum
cell contains a boundary event, so some maximizing circle passes through a
lattice point.  Translate that point to the origin.  The center then lies on
the sweep circle and, after a lattice symmetry, in `0 <= theta <= pi/4`.
Consequently the sweep examines a representative of every possible maximum.

## Complexity

The radius-`2n` lattice disk contains `O(n^2)` relevant points.  Two events per
point distributed over eight symmetry sectors leave approximately `pi*n^2`
events in the sweep sector.

| Sweep stage | Work |
|:------------|-----:|
| lattice scan and event generation | `O(n^2)` |
| event sort | `O(n^2 log n)` |
| exact adjacent-order certification | `O(n^2)` |
| differential sweep | `O(n^2)` |

Therefore one term uses

```text
time   O(n^2 log n)
memory O(n^2)
```

Computing every term separately through `N` uses `O(N^3 log N)` time.

| Method | One term | Prefix through `N` | Memory |
|:-------|---------:|-------------------:|-------:|
| flood | `O(n^4)` | `O(N^5)` | `O(n^2)` |
| exact rows | `O(n^3 log n)` | `O(N^4 log N)` | `O(1)` |
| regions | `O(n^3)` worst case | `O(N^4)` | `O(n)`–`O(n^2)` |
| sweep | **`O(n^2 log n)`** | **`O(N^3 log N)`** | `O(n^2)` |

The present 64-byte event record uses about 18 MB near `n=300`.

## Verification

The sweep, exact-row, serial-region, and four-thread region implementations
reproduce every term currently available from OEIS, `n=0..47`.  This is the
formal external verification range.  The sweep and exact-row methods also
agree on both counts and longest-chord certificates for every `n=0..300`.
Flood fill supplies a structurally different small-radius check.

The exact-row method enumerates every D4-canonical boundary chord and counts
each disk by exact binary searches on horizontal lattice rows.  The region
method works instead in the center triangle `0 <= y <= x <= 1/2`, separates
always-covered core points from volatile boundary points, and tests all
corners, arc/edge crossings, and arc/arc crossings.  Its hot loop is exact
integer arithmetic and can be parallelized with OpenMP.

## Measurements

Median seconds per individual radius on the supplied runtime:

All programs were compiled with `-O3 -march=native`.  Timings use each
program's internal `steady_clock` interval, excluding process startup and text
parsing.  The table reports the median of 15 runs through `n=47`, five runs at
`n=100`, and three runs at `n=200,300`; the OpenMP region build used four
threads.  These are per-term timings, not cumulative prefix timings.

| n | rows 1T | regions 1T | regions 4T | sweep 1T |
|---:|--------:|-----------:|-----------:|---------:|
| 8 | 0.000108 | 0.000058 | 0.000140 | 0.000083 |
| 16 | 0.000850 | 0.000271 | 0.000248 | 0.000323 |
| 32 | 0.006921 | 0.001561 | 0.000749 | 0.001341 |
| 47 | 0.023831 | 0.004458 | 0.001810 | 0.002854 |
| 100 | 0.261839 | 0.038893 | 0.013018 | 0.014191 |
| 200 | 2.309750 | 0.298905 | 0.091249 | 0.054786 |
| 300 | 8.025610 | 0.917531 | 0.255468 | **0.122577** |

At `n=300`, the certified one-thread sweep is about 65.5 times faster than
rows, 7.5 times faster than serial regions, and 2.1 times faster than the
four-thread region method.

Serial regions overtake rows near `n=8`; four-thread regions become worthwhile
near `n=16`.  The single-thread sweep overtakes the four-thread region method
between `n=100` and `n=200`.

Power-law fits to individual-term timings are:

| Fit range | rows | regions 1T | regions 4T | sweep 1T |
|:----------|-----:|-----------:|-----------:|---------:|
| `32..300` | `n^3.15` | `n^2.87` | `n^2.64` | **`n^2.02`** |
| `47..300` | `n^3.14` | `n^2.88` | `n^2.69` | **`n^2.02`** |
| `100..300` | `n^3.12` | `n^2.88` | `n^2.72` | **`n^1.96`** |

The measured sweep is essentially quadratic through 300.  Its formal bound
remains `O(n^2 log n)` because event sorting must eventually expose its
logarithmic factor.
