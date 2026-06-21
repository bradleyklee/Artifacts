# Exact disk-polyomino enumerator

This directory contains an experimental C++ enumerator for
[OEIS A147680](https://oeis.org/A147680): free square-lattice polyominoes whose
occupied lattice sites are exactly the lattice points of a closed Euclidean disk.

Let $P\subset\mathbb Z^2$ be finite and edge-connected.  The program accepts
$P$ when it finds $C\in\mathbb R^2$ and $r\ge0$ with

$$
P=\{X\in\mathbb Z^2:\ \lVert X-C\rVert^2\le r^2\}.
$$

Only lattice sites matter here, not the outline of the unit squares.  Selected
sites may lie on the circle; every unselected lattice site must be strictly
outside it.

## Exact arithmetic

All geometric accept/reject decisions use signed 128-bit integer expressions
and exact rational bounds.  Floating point is used only to print elapsed time.
Thus the calculation is exact provided every intermediate product fits in
`__int128`.  The code does not yet check that bound dynamically, so overflow is
an implementation limit for much larger runs.

## Certificate test

The program does not numerically fit a circle.  It reduces each candidate to a
finite family of one-parameter circle pencils.

### 1. Lattice-convexity

A disk is convex, so a necessary condition is

$$
P=\operatorname{conv}(P)\cap\mathbb Z^2.
$$

The code computes the integer convex hull and counts its lattice sites with
Pick's theorem:

$$
\#\bigl(\operatorname{conv}(P)\cap\mathbb Z^2\bigr)
=A+\frac B2+1,
$$

where $A$ is the hull area and $B$ is its number of boundary lattice
sites.  A candidate fails immediately when this count is not $\#P$.

### 2. Exterior fence

The immediate exterior lattice boundary is

$$
E(P)=\{q\in\mathbb Z^2\setminus P:\ \lVert q-p\rVert_1=1
\text{ for some }p\in P\}.
$$

A witness must exclude every site of $E(P)$.  This is the finite exclusion
set used by the program.  The reduction relies on the fact that the lattice
sites of a disk are edge-connected: a disk containing an omitted lattice site
would also contain a first omitted neighbor on a lattice path back to $P$.

### 3. Exposed boundary anchors

The exposed occupied boundary is

$$
\partial_4P=\{p\in P:\ p+d\notin P
\text{ for some }d\in\{(1,0),(-1,0),(0,1),(0,-1)\}\}.
$$

For every unordered pair $\{A,B\}\subset\partial_4P$, the program tests
the pencil of all circles through $A$ and $B$.  This is the actual anchor
set in the code; it does not test fully surrounded occupied sites.

### 4. One pencil, one rational parameter

Put

$$
M=\frac{A+B}{2},\qquad d=B-A,\qquad N=(-d_y,d_x).
$$

Every circle through $A$ and $B$ has center

$$
C(t)=M+tN,\qquad t\in\mathbb R.
$$

Its squared radius is

$$
r(t)^2=\lVert A-C(t)\rVert^2
=\lVert A-M\rVert^2+t^2\lVert N\rVert^2.
$$

Hence the two centers $C(t)$ and $C(-t)$ give the two circles of the
same radius through $A,B$, and event radii are ordered by $|t|$.

For any lattice site $X$, compare its squared distance from the moving
center with the squared radius:

$$
\begin{aligned}
\Delta_X(t)
&=\lVert X-C(t)\rVert^2-\lVert A-C(t)\rVert^2\\
&=\lVert X-M\rVert^2-\lVert A-M\rVert^2
 -2t\,N\mathbin\cdot(X-M).
\end{aligned}
$$

The $t^2$ terms cancel.  Thus $\Delta_X(t)$ is linear in $t$:

$$
X\in P\Rightarrow\Delta_X(t)\le0,
\qquad
q\in E(P)\Rightarrow\Delta_q(t)>0.
$$

Each site supplies one exact rational lower or upper bound on $t$, or
immediately rules out the pencil.  Their intersection is an exact interval.
A nonempty interval is a certificate for that anchor pair.  The candidate is
accepted when at least one exposed-boundary pair has such an interval.

## Inductive enumeration

Shapes are canonicalized under the eight symmetries of the square.  The program
grows only from earlier accepted shapes rather than first enumerating all free
polyominoes.

| Mode | Candidate pool at order $n$ |
|---|---|
| `--depth 1` | Add one edge-adjacent square to every accepted shape of order $n-1$. |
| `--depth 2` | Take the deduplicated union of the depth-1 pool and all two-square extensions of accepted shapes of order $n-2$. |

In the two-square route, the intermediate $n-1$ shape need not be accepted.
Every candidate still passes the full lattice-convexity and pencil test.

## Evidence and open questions

The executable verifies its embedded OEIS prefix through $n=21$ in both
depth modes.  Replacing the earlier all-occupied-pair search with exposed
boundary pairs left every discrete CSV count unchanged through $n=50$, in
both modes.  Depth 1 and depth 2 also gave the same accepted counts through
$n=50$.

These are regression checks, not completeness proofs.  The main open questions
are:

1. Does every disk polyomino admit a realizing circle through two exposed
   occupied boundary sites?
2. Can a larger predecessor-recovery depth find a disk polyomino missed by
   depth 1 and depth 2?

With the same certificate predicate, a larger recovery pool can only preserve
or increase reported counts.  Agreement through $n=50$ is evidence that the
current shallow modes are adequate there; it is not a theorem about later
orders.

## Build and run

Requires a C++20 compiler and no third-party library.

```sh
make
./disk_polyomino --max-n 50 --depth 1 --csv depth1_n50.csv
./disk_polyomino --max-n 50 --depth 2 --csv depth2_n50.csv
```

To check the embedded OEIS prefix:

```sh
./disk_polyomino --max-n 21 --depth 1 --verify-oeis
./disk_polyomino --max-n 21 --depth 2 --verify-oeis
```

The CSV records the predecessor sizes, the `+1` and `+2` pools, their
union, lattice-convex survivors, accepted disks, and elapsed time.  See
`BENCHMARKS.md` for the recorded local runs through $n=50$.
