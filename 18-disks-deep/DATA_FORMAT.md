# Data format and exact model contract

## Scalar encoding

Every exact scalar is an object with rational-string fields `a`, `b`, `c`, and
`d`, representing

\[
a+b\sqrt2+c\sqrt3+d\sqrt6.
\]

A rational is either an integer decimal string or `numerator/denominator` with
a positive denominator. Coefficients are already reduced when emitted; preserve
that exact meaning, but do not rely on a particular textual pretty-printer.

For independent arithmetic, if `x=(a,b,c,d)` and `y=(A,B,C,D)`, multiplication
in the ordered basis `(1, √2, √3, √6)` is:

```text
1:   aA + 2bB + 3cC + 6dD
√2:  aB + bA + 3(cD + dC)
√3:  aC + cA + 2(bD + dB)
√6:  aD + dA + bC + cB
```

All comparisons, equality tests, collision decisions, and tie detection must be
exact. Floating-point values may be used for display only.

## Geometry and face labels

A body is the fixed-orientation regular `N`-gon

```text
K = { x : n_k · x <= r for k=0,...,N-1 },
```

where `r` is `geometry.model.apothem` in `BLOCK.json`. Face `k` has outward
normal at angle `360*k/N` degrees. Labels increase counterclockwise; face zero
points along positive x.

For the dodecagon, use angles `k*30°`. The first quadrant normal list is

```text
(1,0), (√3/2,1/2), (1/2,√3/2), (0,1)
```

and the remainder follows by the stated angles/symmetry.

For the 24-gon, use angles `k*15°`. The first quadrant normal list is

```text
(1,0)
((√6+√2)/4, (√6-√2)/4)
(√3/2, 1/2)
(√2/2, √2/2)
(1/2, √3/2)
((√6-√2)/4, (√6+√2)/4)
(0,1)
```

and the remainder follows by the stated angles/symmetry.

The container is the axis-aligned square `[-H,H]^2`, with `H` supplied as
`geometry.container.half_side`. For these orientations, the x and y support
radius is the apothem `r`; a center meets an east/west or north/south wall at
coordinate `±(H-r)`.

## Dynamics

The two labelled bodies are `A=state[0]` and `B=state[1]`. Let
`d = position_B - position_A`, `u = velocity_B - velocity_A`.

For every face normal `n_k`, a candidate pair event has

```text
n_k · (d + t u) = 2r,  t > 0,
```

and is valid only when `d+t*u` is in the contact polygon
`{q : n_j·q <= 2r for every j}`. Select the earliest exact candidate. A contact
on two or more pair facets is a terminal corner case, not an ordered collision.

For walls, compute all positive times at which a moving center reaches
`x=±(H-r)` or `y=±(H-r)`. Compare pair and wall candidates exactly. Any
non-singleton/tied event batch is terminal for this corpus and must not be
resolved by arbitrary ordering.

At a wall, negate the corresponding velocity component. At a regular pair
contact on face normal `n`, set

```text
g = n · (v_B - v_A)
v_A' = v_A + n g
v_B' = v_B - n g
```

then continue from the same exact contact time.

## Time-zero seed contact and integer words

The d12 centered seed begins on a regular pair contact. The producer resolves
that contact at exact time zero and records it as `INITIAL_PAIR_FACE`, face 1.
Consequently, the compact d12 blocks start from the **post-contact** state and
cover recorded event steps 1–50,000; they do not contain a byte for step 0 in
`event_codes.u8`. The retained authority is:

```text
supplementary/initial-block-source-records/d12_000001_001000/manifest.json
supplementary/initial-block-source-records/d12_000001_001000/pair_faces.csv
```

The second file must begin with `(pair_contact_index,event_step,face_label) =
(0,0,1)`, matching `seed.time_zero_pair_face` in the manifest. Integer-word
exports include this d12 contact as their first native label, then append
labels selected from the compact blocks. The 24A and 24B lattice seeds declare
no time-zero pair contact. Do not insert a synthetic step-0 event when replaying
a compact block in isolation: its `start_state.json` is already post-seed.

## Compact block layout

Each `blocks/<lane>/<lane>_XXXXXX_YYYYYY.block.tar.gz` contains one root directory
named by `BLOCK.json.name` and exactly these evidence files:

- `BLOCK.json`: schema, exact geometry, endpoint metadata, and event count.
- `SHA256SUMS`: SHA-256 of every evidence member except itself.
- `start_state.json`, `end_state.json`: exact absolute time and labelled state.
- `event_codes.u8`: one byte per local event: `0=WALL_FACE`, `1=PAIR_FACE`.
- `pair_steps.u16`: little-endian unsigned 16-bit **one-based local** steps of
  pair events, strictly increasing.
- `pair_faces.u8`: face labels paired positionally with `pair_steps.u16`.
- `complexity.csv.gz`: post-event exact-clock bit-length telemetry.
- `single_surface_audit.json`: producer regularity declaration.
- `receipt.json`: source-block compaction provenance.

`pair_steps` and `pair_faces` encode no wall identity. Therefore a fresh replay
can compare event kind every step, pair face whenever the kind is pair, and the
exact endpoint state/time. It cannot directly compare a supplied wall-face word
because compact blocks do not contain one.

The producer `state_hash` is retained as cross-reference metadata. A fresh
implementation should compare the decoded exact endpoint fields directly; it
need not reproduce the producer hash serialization.
