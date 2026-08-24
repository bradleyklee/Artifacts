# Theory and verification certificate

## Algorithmic source

J. Ian Munro, Thomas Papadakis, and Robert Sedgewick, “Deterministic Skip
Lists,” *Proceedings of the 3rd Annual ACM-SIAM Symposium on Discrete Algorithms
(SODA 1992)*, pp. 367–375. DOI: 10.1145/139404.139478.

The implementation uses the deterministic 1–2 gap discipline: between
successive promoted boundaries at one level there are one or two lower-level
vertices. This is the skip-list analogue of a complete ordered 2–3 tree.

## Structural consequences

Because a promotion level reduces the number of surviving boundaries by a
constant factor, tower height is O(log N). Therefore search, insertion, and
deletion traverse/repair O(log N) levels in the worst case. Summing the number
of vertices present across all levels gives O(N) structural space.

The executable representation encodes each legal horizontal local pattern with
a type tag in `{1,2,3,4,5}`. The validator checks the local grammar together
with exact promotion, ordering, reciprocal links, contiguous towers, sentinel
coverage, reachability, and allocator/key-index consistency.

## Reachable-state census

For n ordered keys, the implementation's canonical reachable structures are:

```text
n : states
0 : 1
1 : 1
2 : 1
3 : 1
4 : 2
5 : 2
6 : 3
7 : 4
8 : 5
9 : 8
10: 14
11: 23
12: 32
13: 43
14: 63
15: 97
16: 149
17: 224
18: 332
19: 489
20: 727
21: 1116
22: 1776
23: 2897
24: 4782
25: 7895
26: 12909
```

This is A014535 shifted by one leaf: OEIS A014535 counts B-trees of order 3
(complete ordered 2–3 trees) with n leaves. The generating function listed for
that sequence satisfies

```text
A(x) = x + A(x^2 + x^3).
```

The matching census is an independent structural cross-check; it is not used as
the implementation's only correctness criterion.

## Deterministic verification ladder

The external suite exercises increasingly global properties:

1. ordinary API semantics plus deliberate invariant corruption;
2. all insertion permutations through n=9;
3. all deletion permutations through n=8 from every distinct full structure;
4. exhaustive mixed insert/delete state graphs;
5. graded transition graph: construct every canonical state at level n and
   verify every insertion/deletion transition, including that each deletion
   lands exactly in the previously enumerated n-1 state set;
6. fuzzing after the deterministic frontier.

The n=26 graded run contains 12,909 canonical level-26 structures and preserves
the same census/deletion-image invariant. See
`verification/graded-graph-b1-n26.txt`.

## Closure-priority verification

Deletion of one local type has several possible-looking repairs. The retained
priority is:

```text
top out
merge right
merge left
recurse right
recurse left
```

Nearby priority variants were executable-tested. Allowing recurse-right to
preempt merge-right admits a four-key counterexample and produces an illegal
`type2 -> type5` transition. Two other nearby priorities survived smaller
bounded universes but have no verification or performance advantage, so the
release retains the better-tested baseline. See `docs/closure-baseline.md`.

## What is proved and what is not

The finite exhaustive suite is strong executable evidence, not a machine-checked
proof for arbitrary N. A formal proof plan is under `lean-transfer/`; it targets
preservation/termination of the abstract rewrite system and a 2–3-tree
correspondence.

The combination used for RC1 is therefore:

```text
published deterministic skip-list theory
+ strong executable representation invariant
+ exhaustive finite transition certificate
+ independent 2–3-tree state-count cross-check
+ differential/reference-model tests and fuzzing
```
