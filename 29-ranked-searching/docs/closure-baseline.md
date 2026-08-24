# Type-2 deletion closure study

## B0: retained deterministic priority

After unlinking a type-2 vertex:

1. if the level has topped out, remove the level;
2. if the right neighbor is type 3, merge right;
3. if the second-left neighbor is type 5, merge left;
4. if a right neighbor exists, recurse right;
5. otherwise recurse left.

B0 passed the 12-key exhaustive reachable-state test:

- 14,280 canonical states;
- 342,720 transitions;
- every deletion branch exercised.

## Nearby priority alternatives

The first experiment kept the same local rewrites and changed only the priority
between `merge-right`, `merge-left`, and `recurse-right`.

| ID | Priority before fallback recurse-left | Result |
|---|---|---|
| B0 | merge-right, merge-left, recurse-right | PASS, U=12 |
| B1 | merge-right, recurse-right, merge-left | PASS, U=10 |
| B2 | merge-left, merge-right, recurse-right | PASS, U=10 |
| B3 | merge-left, recurse-right, merge-right | FAIL |
| B4 | recurse-right, merge-right, merge-left | FAIL |
| B5 | recurse-right, merge-left, merge-right | FAIL |

The passing B1/B2 results establish only bounded executable evidence, not a
proof or a reason to replace B0.

## Minimal bad-family witness

B3/B4/B5 fail after:

    insert 0
    insert 1
    insert 2
    insert 3
    replace 0

Before replacement the structure is:

    L1: START/1 -> 0/2 -> 1/3 -> 2/4 -> 3/5 -> STOP
    L2: START/1 -> 1/2 -> STOP

Allowing recurse-right to preempt the required merge-right repair produces an
illegal lower transition:

    type2 -> type5

This is a concrete verification reason for preserving merge-right precedence
over recurse-right.

## Current decision

Retain B0. B1/B2 are research alternatives only.

Under the project rule, a closure change needs either:

- stronger verification, or
- measured time/memory improvement.

Neither passing alternative currently supplies that evidence.
