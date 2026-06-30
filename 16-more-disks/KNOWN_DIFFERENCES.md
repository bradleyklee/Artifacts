# Known differences and non-authority material

## Canonical versus legacy paths

`cmd/lattice` plus `internal/engine` is the production source of truth for this
artifact. The older Python `lattice_collision` package and the incoming transfer
zips are retained to make comparison and independent reconstruction easier; they
are not authoritative for a new result.

The crucial evolved rule is simultaneous-contact handling. A same-time batch
whose body supports are disjoint is physically commuting and is resolved as an
`INDEPENDENT_BATCH` or `INDEPENDENT_WALL_BATCH`. A pair corner, a two-wall hit
on one body, and any shared-body same-time batch remain terminal. Some older
reports stopped on all non-singleton batches, so their survivor/terminal totals
must not be substituted for v2 tables.

## Evidence strength

* A full v2 certificate includes exact pre/post states for every batch.
* The 4,000-, 6,000-, and 7,500-batch dodecagon records are compact progress certificates: all exact
  batches, times, hashes, final exact state, and metrics are retained, but its
  per-row coordinate copies are intentionally omitted.
* An atlas is an exhaustive finite scan under one named family and cap; it is
  not an exhaustive scan of all initial conditions.
* `CAP` always means finite regular survival to the cap. It is not a proof of
  chaos, randomness, aperiodicity, or an infinite trajectory.

## Visual scope

The Shorts are code-rendered from independently checked v2 certificate files.
They show selected finite prefixes. They do not visualize an asserted limiting
orbit or interpolate physics with floating point; floating point enters only
when exact coordinates are projected to pixels.
