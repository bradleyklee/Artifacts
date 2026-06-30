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

## Ternary-word samples

For the centered dodecagon scan, a regular pair-face contact contributes its
face label modulo 3; wall contacts contribute no symbol. The prescribed central
contact at time zero is the first symbol. The complete all-face cap-500 scan
has two distinct 108-symbol words. The first is the lexicographically minimal
class, represented by `face=1, incoming=(E,N)`; the second is obtained by
swapping `1` and `2` while keeping `0` fixed.

**Lex-min class — first 100 of 108 symbols**

```text
1,0,2,1,0,2,1,2,1,2,2,2,1,2,2,2,0,2,2,0,2,1,1,0,2
2,2,1,1,2,0,0,0,1,2,2,1,2,1,0,2,2,2,1,0,1,0,2,1,0
2,0,0,1,1,2,2,0,0,0,0,2,2,1,1,2,1,0,0,2,0,0,1,0,1
1,2,1,1,2,1,1,0,0,2,0,1,1,0,0,2,2,2,0,1,2,0,1,1,0
```

**Paired class — first 100 of 108 symbols**

```text
2,0,1,2,0,1,2,1,2,1,1,1,2,1,1,1,0,1,1,0,1,2,2,0,1
1,1,2,2,1,0,0,0,2,1,1,2,1,2,0,1,1,1,2,0,2,0,1,2,0
1,0,0,2,2,1,1,0,0,0,0,1,1,2,2,1,2,0,0,1,0,0,2,0,2
2,1,2,2,1,2,2,0,0,1,0,2,2,0,0,1,1,1,0,2,1,0,2,2,0
```

The lex-min forward continuation is independently checked through 2,000 event
batches / 418 pair contacts and through a compact 7,500-batch checkpoint /
1,578 pair contacts. The first 100 symbols above are also the prefix of both
longer records. Full comma-separated sequences are in:

```text
data/dodecagon_centered/ternary/centered_dodecagon_f1_EN_cap2000.txt
data/dodecagon_centered/ternary/centered_dodecagon_f1_EN_cap7500.txt
```

The reverse stem emits only the source symbol `1` before two wall contacts and
a terminal pair-corner; see `docs/TERNARY_DATA.md` for the convention and
scope.

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
