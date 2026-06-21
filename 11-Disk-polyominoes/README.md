# Exact disk-polyomino enumerator

This directory contains an experimental C++ enumerator for
[OEIS A147680](https://oeis.org/A147680): free square-lattice polyominoes
whose occupied lattice sites are exactly the lattice points of a closed
Euclidean disk.

## What is counted

A candidate is a finite, nonempty, 4-connected set of occupied lattice sites

$$
P\subset\mathbb Z^2.
$$

Here 4-connected means that sites are connected by horizontal and vertical
unit steps.  The associated ordinary unit-square polyomino is

$$
\mathcal U(P)=\bigcup_{(i,j)\in P}[i,i+1]\times[j,j+1].
$$

The target circle condition is about the *sites* in $P$, not the planar square
union $\mathcal U(P)$.  It asks for $C\in\mathbb R^2$ and $r\ge0$ with

$$
P=\{z\in\mathbb Z^2 : \lVert z-C\rVert^2\le r^2\}.
$$

Thus every $p\in P$ is on or inside the circle, while every
$q\in\mathbb Z^2\setminus P$ is strictly outside it.  The implemented
boundary-pair test supplies an exact certificate for this condition whenever it
accepts; whether it finds every such disk is an open question below.

Shapes are identified up to translation, rotation, and reflection.

## Necessary convex-hull screen

Before the pencil test, the program rejects $P$ unless

$$
P=\mathrm{conv}(P)\cap\mathbb Z^2.
$$

This is necessary: a disk is convex, so every lattice point in the convex hull
of its occupied sites must also belong to the disk.  The code evaluates this
screen exactly by counting the lattice points of the integer convex hull via
Pick's theorem; it does not enumerate a bounding box.

## Exact circle-pencil test

Let

$$
D=\{(1,0),(-1,0),(0,1),(0,-1)\}.
$$

The immediate exterior fence is

$$
E(P)=\{q\in\mathbb Z^2\setminus P:\ \exists p\in P,\ \lVert q-p\rVert_1=1\}.
$$

The exposed occupied boundary sites are

$$
\partial_4P=\{p\in P:\ \exists d\in D,\ p+d\notin P\}.
$$

For every unordered pair $\{A,B\}\subset\partial_4P$, the program considers
the complete pencil of circles through $A$ and $B$.  Put

$$
M=\frac{A+B}{2},\qquad
N=\bigl(-(B_y-A_y),\ B_x-A_x\bigr).
$$

Every center in that pencil is

$$
C(t)=M+tN,\qquad t\in\mathbb R,
$$

and its squared radius is

$$
r(t)^2=\lVert A-M\rVert^2+t^2\lVert N\rVert^2.
$$

So $t$ and $-t$ give the two circles of the same radius; radius levels are
ordered by $|t|$, not by signed position on the perpendicular bisector.

For any lattice site $X$, define

$$
\delta_X(t)=\lVert X-C(t)\rVert^2-r(t)^2.
$$

Expanding gives

$$
\delta_X(t)=\lVert X-M\rVert^2-\lVert A-M\rVert^2
            -2t\,N\mathbin\cdot(X-A).
$$

The $t^2$ terms cancel.  Thus $\delta_X(t)$ is affine in $t$:

- each $p\in P$ requires $\delta_p(t)\le0$;
- each $q\in E(P)$ requires $\delta_q(t)>0$.

Every nonconstant condition supplies an exact rational lower or upper bound on
$t$.  The program intersects these bounds, retaining their open or closed
endpoints.  A feasible interval gives a realizing member of the pencil.

Checking $E(P)$ is enough for this test.  Lattice points in a Euclidean disk
are 4-connected; therefore, if a purported realizing disk contained any
unwanted lattice site, a 4-neighbor path within the disk would first leave
$P$ at a site of $E(P)$.

## Exact arithmetic

No floating-point value decides geometry.  The hull screen, pencil
coefficients, and rational bounds use signed 128-bit integer expressions;
only elapsed-time reporting uses `double`.  The calculation is exact provided
all intermediate products fit in `__int128`.  The code does not yet check this
bound dynamically, so overflow remains an implementation limit for much
larger runs.

## Inductive enumeration

The program grows candidates from accepted predecessors.

| Mode | Candidate pool at order $n$ |
|---|---|
| `--depth 1` | Add one edge-adjacent square to every accepted shape at order $n-1$. |
| `--depth 2` | Take the deduplicated union of the depth-1 pool and all two-square extensions of accepted shapes at order $n-2$. |

In the two-square route, the intermediate order-$n-1$ shape need not itself
pass.  Every candidate then receives the hull screen and the boundary-pair
pencil test above.

## Status and open questions

The executable verifies its embedded OEIS prefix through $n=21$ in both
depth modes.  Depth 1 and depth 2 agreed through the recorded $n=50$ runs.
This is evidence, not a completeness proof.

The two central open questions are:

1. Does every disk polyomino have a realizing circle through two exposed
   occupied boundary sites?
2. Can a larger predecessor-recovery depth find a disk polyomino missed by
   depth 1 and depth 2?

For a fixed certificate predicate, increasing recovery depth can preserve or
increase the reported counts, but cannot decrease them.

## Build and run

Requires a C++20 compiler and no third-party library.

```sh
make
./disk_polyomino --max-n 50 --depth 1 --csv depth1_n50.csv
./disk_polyomino --max-n 50 --depth 2 --csv depth2_n50.csv
```

To verify the embedded OEIS prefix:

```sh
./disk_polyomino --max-n 21 --depth 1 --verify-oeis
./disk_polyomino --max-n 21 --depth 2 --verify-oeis
```
