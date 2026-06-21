# Exact disk-polyomino enumerator (C++)

This folder contains an experimental exact-integer/rational enumerator for
[OEIS A147680](https://oeis.org/A147680): free square-lattice polyominoes whose
lattice sites are exactly the lattice points of a closed Euclidean disk.

Every geometry decision uses signed 128-bit integer expressions and exact
rational parameter bounds. No floating-point comparison decides acceptance.
The calculation is exact provided every intermediate integer product fits in
signed `__int128`. The current code does not dynamically check that bound, so
this remains an implementation limit when extending far beyond the recorded
runs.

Here, a shape is a finite edge-connected collection of square-lattice sites.
It is accepted only if the program finds a closed Euclidean disk containing
exactly those sites and no other square-lattice sites. Selected sites may lie
on the circle; every unselected lattice site must be strictly outside it. The
test concerns lattice sites, not the outline formed by unit squares.

## The geometric test

The program does not fit circles numerically. It uses the following finite,
exact test.

1. **Lattice-convex prefilter.** A disk is convex, so a candidate must contain
   every lattice site in its Euclidean convex hull. The program computes the
   hull and rejects a candidate unless the hull contains no unselected lattice
   site. Its lattice-point count is obtained exactly from the integer hull
   vertices using Pick's theorem and edge gcd counts.

2. **Finite exterior fence.** The exterior fence consists of every unselected
   lattice site one four-neighbor step from the candidate. A witness circle
   must leave every fence site strictly outside. This is the finite exclusion
   set used in every certificate. The intended finite-check lemma is that a
   disk capturing any farther unwanted lattice site would also capture a first
   exterior-fence site along a lattice path back to the candidate.

3. **Every exposed-boundary pair gives a pencil.** An exposed occupied boundary
   site is an occupied site with at least one missing four-neighbor. The program
   tries every unordered pair `A`, `B` of such sites as possible circle-contact
   anchors. All circles through `A` and `B` have centers on the perpendicular
   bisector of the segment between them. The program uses a signed rational
   coordinate along that bisector to describe the full one-parameter pencil.

   A fully surrounded occupied site never needs to be an anchor: a circle
   through it could not also contain both members of an opposite occupied
   neighbor pair. The exposed boundary supplies anchors; the exterior fence is
   the separate set of strict exclusions.

4. **Events are ordered by radius, not signed bisector position.** For each
   remaining selected site and each exterior-fence site, there is at most one
   circle in the pencil that passes through `A`, `B`, and that site. The sweep
   begins with the smallest circle through `A` and `B`, whose diameter is the
   segment `AB`, and increases radius. Equivalently, it increases the absolute
   distance of the center from the midpoint of `AB` along the perpendicular
   bisector. The sign still matters because it identifies which of the two
   same-radius branches changes.

5. **Exact interval test.** Instead of constructing a numerical event ledger,
   the implementation compares the squared distance from each site to the
   moving center with the squared radius of the same moving circle. The common
   quadratic term cancels, leaving a linear condition on the signed bisector
   parameter. Selected sites impose non-strict bounds; exterior-fence sites
   impose strict bounds. The program intersects all of those half-line bounds
   with exact rational arithmetic. A nonempty interval proves that the pair
   has a valid witness circle.

The candidate is accepted if at least one exposed-boundary pair has a feasible
pencil interval.

### Why the bisector parameter is rational and linear

For a chosen anchor pair `A`, `B`, let `M` be their midpoint and let `N` be the
perpendicular integer vector obtained by rotating `B - A` by 90 degrees. Every
center in the pencil has the form `C(t) = M + t*N`, where `t` is a signed
rational parameter. The actual signed distance from `M` along the bisector is
`|N| * t`; for one fixed pair, ordering event circles by increasing radius is
therefore the same as ordering them by increasing `abs(t)`.

For any lattice site `X`, the program compares the squared distance from `X`
to `C(t)` with the squared radius of the circle through `A` and `B`. Each
quantity separately has a quadratic `t*t` term, but the two circles share that
term, so it cancels in the difference. What remains is an expression of the
form `constant + coefficient*t`.

Thus a selected site gives either a closed lower bound or a closed upper bound
on `t`: it must stay inside or on the circle. An exterior-fence site gives the
corresponding strict bound: it must stay outside. A site whose coefficient is
zero never changes status anywhere in that pencil and is either immediately
compatible or immediately disqualifying. The surviving lower and upper bounds
are exact rational numbers, so a nonempty interval is an exact certificate
that some member of the pencil works.

## Inductive enumeration

The enumerator deliberately does not generate all free polyominoes and then
filter them. It grows candidates from earlier accepted levels and canonicalizes
under the eight symmetries of the square.

`--depth 1` uses ordinary hereditary growth: add one edge-adjacent square to
an accepted shape of the preceding order.

`--depth 2` takes the deduplicated union of two routes at the target order:

1. one-square extensions of accepted shapes from the preceding order; and
2. two-square extensions of accepted shapes from two orders earlier.

For the two-step route, the intermediate shape is not required to be accepted.
It is a recovery channel for a valid shape whose one-square predecessor might
not itself be retained by the current search. Every candidate from either route
still passes the full lattice-convex and exposed-boundary-pair circle test.

## Status and validation

This is a research enumerator, not a proof that the hereditary generator or the
two-contact reduction is complete. The following are proof obligations rather
than assumptions silently discharged by the code:

- Every disk polyomino occurs through one of the chosen predecessor routes.
- Every disk polyomino has a witness circle through two exposed occupied
  boundary sites, so that one of the tested pencils finds it.

The program reproduces the OEIS prefix hard-coded through order 21 in both
depth modes. Replacing the earlier all-occupied-pair anchor loop with the
exposed-boundary-pair loop left every discrete count column unchanged through
order 50 in both depth modes. Because the new anchor set is a subset of the old
one, term-by-term equality establishes inductively that the retained accepted
sets also agree through that range. These comparisons are evidence, not a
completeness proof.

### Open question: can depth change the counts?

Yes, in principle. A deeper recovery mode can find a valid disk polyomino whose
deletion paths do not pass through an accepted candidate retained by a shallower
mode. With the same geometric predicate, enlarging the recovery pool should
only add candidates and can therefore only preserve or increase a reported
count; it should not lower one. The agreement of depth 1 and depth 2 through
order 50 is useful evidence, but it does not prove that depth 3 or a larger
recovery depth will never add a new disk polyomino.

## Build

```sh
make
```

Requires a C++20 compiler. Recent GCC and Clang work; no third-party library
is required.

## Run

Ordinary hereditary growth:

```sh
./disk_polyomino --max-n 50 --depth 1 --csv depth1_n50.csv
```

Depth-two growth:

```sh
./disk_polyomino --max-n 50 --depth 2 --csv depth2_n50.csv
```

Check the embedded OEIS prefix through order 21:

```sh
./disk_polyomino --max-n 21 --depth 1 --verify-oeis
./disk_polyomino --max-n 21 --depth 2 --verify-oeis
```

The CSV gives, for each order, the sizes of the previous accepted levels, the
`+1` and `+2` candidate pools, their deduplicated union, lattice-convex
survivors, accepted disks, and elapsed seconds. See `BENCHMARKS.md` for the
recorded local baseline through order 50.
