# Certificate contract

Each `data/<family>/evolve/<id>.json` is one portable event certificate.  Its
`model` section fixes unit-edge octagon geometry, the exact `Q(sqrt(2))` scalar
field, container convention, collision law, strict-contact rule, and
conservation contract.  Its `instance` section records the compact initial
state.  Its `evolution` section is an append-only exact event ledger: each row
contains absolute time, all same-time contacts, and complete pre/post states.

The checker begins from the embedded initial state, independently enumerates
all body--body and body--wall candidates, confirms the globally earliest batch,
requires positive edge overlap for ordinary pair contacts, computes the
post-collision velocity map, and verifies free-flow and collision invariants.
Wall collisions preserve kinetic energy but exchange momentum with the fixed
container; pair-only batches preserve total body momentum.  The cutoff witness
checks that the final recorded state is within the exact coefficient bound and
the next resolvable post-state exceeds it.
