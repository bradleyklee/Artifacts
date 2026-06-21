# Exact disk-polyomino enumerator (C++)

This folder contains an experimental exact-integer/rational enumerator for
[OEIS A147680](https://oeis.org/A147680): free square-lattice polyominoes whose
lattice sites are exactly the lattice points of a closed Euclidean disk.

All geometry decisions use signed 128-bit integer expressions and rational
parameter bounds; no floating-point comparison decides acceptance.  Thus the
calculation is exact provided its intermediate integer products fit in signed
`__int128`.  The current code does not dynamically check that bound, so this is
an implementation limit to retain when extending far beyond the recorded runs.

A shape is a finite, edge-connected set \(P\subset\mathbb Z^2\).  It is accepted
only when the program finds a circle \(C\) satisfying

\[
C\cap\mathbb Z^2=P.
\]

Thus selected points may lie on the circle, while every unselected lattice point
must be strictly outside it.  The test concerns **lattice points**, not the
outline formed by unit squares.

## The geometric test

The program does not fit circles numerically.  It uses the following finite,
exact test.

1. **Lattice-convex prefilter.** A disk is convex, so a possible answer must
   contain every lattice point in its Euclidean convex hull.  The program
   computes the hull and rejects unless

   \[
   \operatorname{conv}(P)\cap\mathbb Z^2=P.
   \]

   The lattice-point count of the hull is obtained exactly from its integer
   vertices using Pick's theorem and the edge gcd counts.

2. **Finite exterior fence.** Let \(E\) be the unselected lattice points at
   four-neighbor distance one from \(P\).  A witness circle must put all of
   \(E\) strictly outside.  This is the finite exterior set used in every
   certificate.  The intended finite-check lemma is that a disk which captured
   any farther unwanted lattice point would also capture some first exterior
   point on a lattice path from \(P\).

3. **Every exposed-boundary pair gives a pencil.** Let

   \[
   \partial_4 P=\{p\in P:\text{at least one four-neighbor of }p\text{ is not in }P\}.
   \]

   The program tests every unordered pair \(A,B\in\partial_4 P\), looking
   for a witness circle having both on its boundary.  A fully surrounded
   lattice site never needs to be an anchor: if a circle passed through \(p\),
   it could not contain both members of an opposite neighbor pair
   \(p+v,p-v\).  Thus a circle contact must be exposed.  The immediate
   exterior lattice boundary is the separate exclusion set \(E\).  All
   circles through \(A\) and \(B\) have centers on the perpendicular bisector
   of \(AB\):

   \[
   c(t)=\frac{A+B}{2}+t\,n,
   \]

   where \(n\) is a fixed perpendicular vector.  The signed coordinate \(t\)
   distinguishes the two branches of the pencil.

4. **Events are ordered by radius, not signed position.** For each other point
   \(X\in(P\setminus\{A,B\})\cup E\), there is at most one event circle
   through \(A,B,X\).  Its center has some signed coordinate \(t_X\), but the
   event radius satisfies

   \[
   r_X^2=\frac{\lVert A-B\rVert^2}{4}+\lVert n\rVert^2t_X^2.
   \]

   Therefore the geometric sweep starts at the diameter circle \(t=0\) and
   proceeds in increasing \(|t|\), equivalently increasing radius, while
   retaining the sign of \(t\) to identify which branch changes.  A point on
   the two opposite half-planes of the chord line has the corresponding
   enter-on-one-branch / leave-on-the-other behavior.

5. **Exact interval test.** Rather than explicitly sorting an event ledger, the
   implementation writes, for each \(X\),

   \[
   \Delta_X(t)=\lVert X-c(t)\rVert^2-\lVert A-c(t)\rVert^2.
   \]

   This is linear in \(t\).  A selected point requires \(\Delta_X(t)\le0\);
   an exterior-fence point requires \(\Delta_X(t)>0\).  Each condition is a
   half-line, all are intersected with exact rational arithmetic, and a
   nonempty interval is a witness for that pair.  This is algebraically the
   same finite pair-pencil sweep described above; it avoids floating-point
   geometry and preserves the strict exclusion of exterior points.

The candidate is accepted if **any exposed-boundary pair** has a feasible
pencil interval.

## Inductive enumeration

The enumerator deliberately does not generate all free polyominoes and then
filter them.  It grows candidates from earlier accepted levels, canonicalizing
under the eight symmetries of the square.

`--depth 1` uses ordinary hereditary growth:

\[
\mathcal D_n\leftarrow\{P\cup\{q\}:P\in\mathcal D_{n-1},\ q\text{ is one edge-adjacent new square}\}.
\]

`--depth 2` uses the deduplicated union of two routes at target order \(n\):

1. one-square extensions of accepted order \(n-1\), and
2. two-square extensions of accepted order \(n-2\).

For the two-step route, the intermediate order-\(n-1\) shape is **not**
required to be accepted.  It is a recovery channel for a valid shape whose
one-square predecessor might not itself be retained by the current search.
Every candidate from either route still passes the full lattice-convex and
exposed-boundary-pair circle test.

## Status and validation

This is a research enumerator, not a proof that the hereditary generator or the
two-contact reduction is complete.  In particular, the following remain proof
obligations rather than assumptions silently discharged by the code:

- every disk polyomino occurs through the chosen one- or two-square predecessor
  routes; and
- every disk polyomino has a witness circle through two exposed occupied
  boundary sites, so that one of the tested pencils finds it.

The program reproduces the OEIS prefix hard-coded through \(n=21\) in both
depth modes.  Replacing the earlier all-occupied-pair anchor loop with the
exposed-boundary-pair loop left every discrete count column unchanged through
\(n=50\), in both depth modes.  Because the boundary-pair anchors are a subset
of the older all-pair anchors, term-by-term equality establishes inductively
that the retained accepted sets also agree through that range.  These
comparisons are evidence, not a completeness proof.

### Open question: can depth change the counts?

Yes, in principle.  A deeper recovery mode can find a valid order-\(n\) disk
whose deletion paths do not pass through any accepted candidate retained by a
shallower mode.  With the same geometric predicate, enlarging the recovery
pool should only add candidates and therefore can only preserve or increase a
reported count; it should not lower one.  The agreement of depth 1 and depth 2
through \(n=50\) is useful evidence, but it does not prove that depth 3 or a
larger recovery depth will never add a new disk polyomino.

Two useful direct closed-disk witnesses beyond the older prefix are:

\[
\{(x,y)\in\mathbb Z^2:x^2+y^2\le13\},\qquad |P|=45,
\]

with row counts \((5,7,7,7,7,7,5)\), and

\[
\{(x,y)\in\mathbb Z^2:x^2+y^2\le16\},\qquad |P|=49,
\]

with row counts \((1,5,7,7,9,7,7,5,1)\).  Both are strict witnesses: the
nearest omitted lattice points lie at larger squared radius.

## Build

```sh
make
```

Requires a C++20 compiler.  Recent GCC and Clang work; no third-party library
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

Check the embedded OEIS prefix through \(n=21\):

```sh
./disk_polyomino --max-n 21 --depth 1 --verify-oeis
./disk_polyomino --max-n 21 --depth 2 --verify-oeis
```

The CSV gives, for each order, the sizes of the previous accepted levels, the
`+1` and `+2` candidate pools, their deduplicated union, lattice-convex
survivors, accepted disks, and elapsed seconds.  See `BENCHMARKS.md` for the
recorded local baseline through \(n=50\).
