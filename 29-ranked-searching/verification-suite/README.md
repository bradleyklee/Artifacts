# Verification suite

This is a first-class artifact separate from the Go implementation in
`../implementation`.

It depends on the implementation as an external Go module. The suite does not
share the implementation package or reach into private representation fields.
The implementation exposes only narrowly documented verification aids for
structural signatures, branch tracing, and cloning.

## Deterministic gates

```sh
go test -run '^TestAllInsertionPermutationsThrough9$' -count=1 -v
go test -run '^TestGradedTransitionGraph$' -count=1 -v
```

`TestGradedTransitionGraph` defaults to `n=24`. Raise the frontier explicitly:

```sh
SKIPLIST_GRAPH_MAX_N=26 go test -run '^TestGradedTransitionGraph$' -count=1 -v
```

The graph is graded by number of ordered keys. At every level it verifies every
insertion rank and every deletion rank from every deterministically reachable structural
state. Deletion images must equal the complete preceding level.

The independent 2-3-tree recurrence in `structure_count_test.go` counts all
allowable ordered height-balanced 2-3-tree shapes. Through the current verified
frontier, this count equals the number of deterministically reachable skip-list states.

## Random assurance after deterministic coverage

```sh
go test -run '^TestDeterministicMixedReferenceWalk$' -count=1
go test -run '^$' -fuzz FuzzOperations -fuzztime=30s
```

Random/fuzz testing is deliberately secondary to deterministic state-space
coverage.
