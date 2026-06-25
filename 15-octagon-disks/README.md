# Octagon disks

An exact-arithmetic data artifact for translating unit-edge regular octagons in
finite square 4.8.8 containers.  It preserves two related families: thirteen
complexity-bounded `three-body` trajectories in the L=4 hard-octagon box, and
five C4-symmetric `clock` survivors with four to six bodies.  Every run has a
compact exact initial condition, a full self-contained evolution certificate,
an independent checker report, and a code-generated SVG initial-condition view.
The `three-body` family additionally exposes read-only body-pair and lex-min
ternary words; `clock` retains its pair-contact tables without forcing an
inappropriate ternary encoding.  The stored prefixes are finite certificates,
not proofs of chaos, aperiodicity, or a complete orbit classification.

## Layout

```text
code/                         exact producers, independent checkers, extractors, SVG renderer
data/three-body/initial/      13 compact exact seeds
data/three-body/evolve/       13 self-contained checked event ledgers
data/three-body/check/        independent-checker reports
data/three-body/pairs/        body-pair sequences including mixed pair+wall contacts
data/three-body/ternary/      lex-min ternary words for the three possible body pairs
data/three-body/images/       data-generated initial-condition SVGs
data/clock/initial/           5 compact exact C4 survivor seeds
data/clock/evolve/            5 self-contained checked event ledgers
data/clock/check/             independent-checker reports
data/clock/pairs/             body-pair tables; no ternary reduction
data/clock/images/            data-generated initial-condition SVGs
docs/                         checker and finite-prefix comparison notes
```

All `evolve/*.json` files embed the model contract, exact `Q(sqrt(2))`
encoding, container data, initial state, complexity cutoff, and raw event
ledger.  The checkers never call or import the Go evolvers.  A normal pair
contact must have one active face with strictly positive tangent overlap;
corners and prohibited shared-body batches are terminal rather than silently
resolved.  A disjoint simultaneous pair-plus-wall batch is valid, and the pair
is retained by each extractor.

## Commands

Only Go and Python's standard library are needed.

```sh
make smoke       # one independent check from each family + all SVGs
make check       # independently check every committed certificate
make extract     # rebuild stored pair sequences and three-body ternary words
make render      # rebuild every initial SVG from exact input data
make index       # rebuild index.json
```

`make evolve-three` and `make evolve-clock` retain producer commands for the
stored models.  They write to `/tmp` intentionally: regeneration is expensive
and should be compared with the committed certificates before replacing them.

## Scope

The `three-body` ternary word maps the three unordered body pairs to `0,1,2`
after choosing the lexicographically least body relabeling.  This construction
does not extend to the clock family, whose active body set varies by seed and
may exceed three.  Short-block and cross-section observations are diagnostics,
not claims of randomness or transcendence.
