# A295344: fixed-radius lattice circles

This artifact computes the maximum number of integer lattice points inside or
on a closed circle of integer radius `n` (OEIS A295344).

## Files

- `a295344.cpp` — compiled exact enumerator with `row` and `flood` methods.
- `benchmark.py` — reproducible timing and agreement comparison.
- `records.csv` — terms, maximizing chord witnesses, and production timings.
- `benchmark.csv` — median per-term timings for both methods.

## Build and run

```text
g++ -O3 -march=native -std=c++17 a295344.cpp -o a295344
./a295344 row 100
./a295344 flood 30
python3 benchmark.py
```

Arguments are `METHOD LAST [FIRST]`.  Each output row is
`n count a b seconds`.  The witness chord joins `(0,0)` to `(a,b)`.

## Exact row method

For every D4-canonical chord `(a,b)`, where `a >= b >= 0` and
`a^2+b^2 <= 4n^2`, a radius-`n` center is

```text
c = ((a-b*r)/2, (b+a*r)/2),
r = sqrt((4n^2-a^2-b^2)/(a^2+b^2)).
```

The other center has the same count under `z -> (a,b)-z`.  On each integer
row, the included points form one interval.  The program finds an included
integer nearest `c_x`, then uses exact binary searches for the interval ends.
All comparisons reduce to signed `__int128` integer comparisons after
squaring.  Floating point is not used by the geometric calculation.

The search is exhaustive: center positions are periodic modulo `Z^2`; the
coverage count is constant in each cell of the finite boundary-circle
arrangement; and the closure of a maximum cell contains an intersection of two
boundary circles.  Hence some maximizing circle passes through two lattice
points and occurs in the chord search.

A variational test at one witness can certify only a local maximum arrangement
cell.  Restricting centers to one lattice unit cell removes translated copies
but folds all relevant boundary arcs into that cell; it does not remove the
other local maxima.  Global maximality therefore comes from the exhaustive
chord enumeration, not from the witness alone.

## Independent flood method

For the same candidate circle, flood fill starts at the known included point
`(0,0)` and follows four-neighbor lattice edges using the same exact inclusion
predicate.  It is structurally independent of row interval counting.  Its
cost grows roughly as `O(n^4)` over all candidates, so it is intended for
cross-checking rather than production.

The flood is complete because every included lattice point can be moved, one
coordinate step at a time, toward a nearest lattice point to the center without
increasing its distance from the center.  That nearest point is inside for
integer radius `n >= 1`; reversing these paths connects the entire discrete
disk to `(0,0)`.

The published OEIS prefix through `n=47`, the exact-row results, and the flood
results agree.  See `benchmark.csv` for the measured crossover.

## Timing comparison

Median seconds per radius on the current compiled runtime:

| n | exact row | flood fill | flood / row |
|---:|----------:|-----------:|------------:|
| 1  | 0.0000021 | 0.0000021 | 0.98 |
| 2  | 0.0000044 | 0.0000064 | 1.44 |
| 4  | 0.0000178 | 0.0000321 | 1.80 |
| 8  | 0.0001086 | 0.0003019 | 2.78 |
| 16 | 0.0008350 | 0.0040012 | 4.79 |
| 32 | 0.0070075 | 0.0559937 | 7.99 |
| 48 | 0.0253189 | 0.2697030 | 10.65 |
| 64 | 0.0630832 | 0.8600210 | 13.63 |
| 96 | 0.2254400 | 4.2386900 | 18.80 |

Flood fill is competitive only at `n=1`; exact rows lead from `n=2` onward.
