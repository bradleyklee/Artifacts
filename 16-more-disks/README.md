# Artifact 16 — cardinal lattice polygon experiments

A Go-first exact-arithmetic artifact for fixed-orientation squares, octagons,
dodecagons, and 24-gons in finite square containers. It packages the low
threshold experiments needed for the current story:

1. squares do not produce a finite-horizon survivor through `L=2,N=4`;
2. ordinary cardinal/lattice dodecagon pairs do not produce one at `L=2` or
   `L=3` through the stated horizon;
3. a centered off-cardinal dodecagon contact yields two ternary-word classes,
   with face 1 / `(E,N)` chosen as lexicographically minimal; its short exact reverse stem is retained separately;
4. ordinary `L=2,N=2` 24-gon starts yield two D4 classes of survivors.

All of these are finite exact computations. `CAP` means only that a trajectory
remained regular and did not return through its listed event horizon.

## Layout

```text
cmd/lattice/                  canonical Go command-line producer
internal/engine/              exact common-field evolver and Go parity tests
internal/artifact/            portable JSON wire schema
data/<family>/                raw Go atlases, manifests, full certificates, sequences
check/                        Python independent-replay reports
analysis/                     D4/time-reversal and ternary audit
scripts/postcheck_go.py       independent Python checker; never calls the Go producer
scripts/render_shorts.py      code-only vertical video renderer
renders/shorts/               two public-facing MP4s and their render manifest
docs/                         contract, status, certificate and transfer material
reference/                    incoming packets retained as non-authoritative references
```

## Build and verify

Only Go, Python 3 standard library, Pillow, and FFmpeg are used.

```sh
make build              # canonical Go binary
make test               # Go exact-arithmetic parity tests
make scan               # reproduce the low exhaustive atlases
make certs              # regenerate the four full positive certificates
make check              # independent Python replay of all committed records
make derive             # rebuild symmetry / ternary derived data
make render             # rebuild the two Shorts
make index manifest     # rebuild index and checksums
```

`make deep-dodecagon` creates the checked compact 7,500-event progress
checkpoint. It is intentionally separate from the ordinary low-atlas build.

Read `docs/DATASET_STATUS.md` before treating any record as evidence. See
`TRANSFER_PACKET.md` for a next-window or independent-rewrite handoff.
