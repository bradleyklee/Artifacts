# Representation invariant

## Semantic object

The structure is an ordered association:

    key -> value

Keys provide identity. Values determine skip-list order.

The order function uses this sign convention:

- `+1`: left value precedes right value,
- `0`: equivalent order,
- `-1`: left value follows right value.

Equal values are inserted after existing equal values.

## Horizontal type grammar

The representation stores a type tag `t` in `{1,2,3,4,5}` at each non-stop vertex on a level.

The accepted transitions are:

    1 -> 2 -> (1 | 3 | STOP)
    3 -> 4 -> 5 -> (1 | 3 | STOP)

At a non-top level, type 1 and type 3 vertices are exactly the vertices promoted
to the next level.

Therefore two consecutive promoted boundaries have either:

- one intervening vertex: `1,2` pattern, or
- two intervening vertices: `3,4,5` pattern.

This is the executable form of the deterministic 1–2 invariant.

## Global invariants checked

At operation boundaries:

1. start index `0` and stop index `-1` exist;
2. every real node has a unique key/index mapping;
3. every live index is reachable on level 1;
4. every horizontal next pointer has the reciprocal previous pointer;
5. every level record is reachable from the start sentinel;
6. real-node towers are contiguous from level 1;
7. every non-top promotion matches the lower type exactly;
8. the type grammar holds on every level;
9. values are ordered across every adjacent level edge;
10. allocator live/free bookkeeping covers all assigned positive indices.

The validator checks both local grammar and global representation consistency.
