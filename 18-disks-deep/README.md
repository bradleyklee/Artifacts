# Artifact 18 — deep disk burns

Artifact 18 retains the exact-arithmetic d12, 24A, and 24B disk-burn producer,
its 80-column progress monitor, three recorded 50,000-collision lanes, their
complexity telemetry, and compact data for independent replay review. The
retained corpus is evidence, not a mutable workspace: fresh searches write to
`reruns/`, leaving the delivered blocks unchanged.

## 1. Run a fresh 50K burn

```bash
make burn-50k
# Optional stable destination:
make burn-50k RUN_DIR=reruns/<name>
```

This launches a fresh 50,000-collision run in each lane through the live
monitor, then seals and structurally checks the resulting compact blocks in the
selected rerun workspace. It never writes into the delivered `blocks/` corpus.

## 2. Result: approximately linear exact-clock complexity growth

The supplied 50,000-collision telemetry measures `total_bits`: the bit length
of one positive common denominator plus the bit lengths of its four associated
common-basis numerators. Ordinary least-squares fits over collisions 1–50,000
show a near-linear trend in every lane:

| lane | fitted slope (bits/collision) | R² | `total_bits` at collision 50,000 |
|---|---:|---:|---:|
| d12 | 0.207019 | 0.997536 | 10,461 |
| 24A | 0.525944 | 0.999772 | 26,279 |
| 24B | 0.525945 | 0.999772 | 26,284 |

- d12: [SVG](complexity/d12_total_bits.svg) · [CSV](complexity/d12_total_bits.csv)
- 24A: [SVG](complexity/24A_total_bits.svg) · [CSV](complexity/24A_total_bits.csv)
- 24B: [SVG](complexity/24B_total_bits.svg) · [CSV](complexity/24B_total_bits.csv)

These series are supplied producer telemetry. Their `total_bits` field is not
recoverable from the compact block rows alone; a full fresh exact replay is the
route to independent regeneration.

## 3. Inspect certified quotient words

```bash
make words-check
make words-print WORD_TERMS=50
```

The six saved 10,000-term integer words retain chronological polygon–polygon
face labels only; wall events are omitted. For an `N`-gon, `mod N/2` identifies
opposite faces and `mod N/4` gives the quadrupole quotient. Thus d12 supplies
mod 6 and mod 3 views, while 24A and 24B supply mod 12 and mod 6 views. The
d12 word includes its documented time-zero centered seed contact before labels
from the 50,000 recorded steps; 24A and 24B have no declared
time-zero pair contact. `make words-check` recomputes and byte-compares the
saved words against all 50,000 recorded events in each lane. It certifies
extraction from the recorded corpus, not independent physical replay.

### First 50 terms

Regenerate this checksum-checked display with `make words-print WORD_TERMS=50`.
`make words-check` is the separate complete 50,000-event derivation check.

```text
Artifact 18 saved integer-word prefixes: first 50 terms
d12 mod 6: 1,3,2,1,0,5,4,2,4,5,5,2,4,5,5,5,3,5,2,3,2,1,4,3,2,2,2,4,4,5,3,3,0,4,2,2,1,2,1,3,2,5,5,1,3,4,0,5,1,3
  base-10 prefix from full retained base-6 stream (10655 residues; converged from saved 10000): 0.260154005969048738373225837397785259882555213919392612120264…
d12 mod 3: 1,0,2,1,0,2,1,2,1,2,2,2,1,2,2,2,0,2,2,0,2,1,1,0,2,2,2,1,1,2,0,0,0,1,2,2,1,2,1,0,2,2,2,1,0,1,0,2,1,0
  base-10 prefix from full retained ternary stream (10655 residues; converged from saved 10000): 0.423359616787198293609629498260695939241264862349149690865629…
24A mod 12: 0,9,9,3,11,11,9,0,5,8,9,3,3,3,10,5,5,5,5,3,9,11,11,4,7,1,8,7,9,11,7,6,7,8,9,10,0,5,3,8,6,6,10,3,3,7,7,6,6,6
24A mod 6: 0,3,3,3,5,5,3,0,5,2,3,3,3,3,4,5,5,5,5,3,3,5,5,4,1,1,2,1,3,5,1,0,1,2,3,4,0,5,3,2,0,0,4,3,3,1,1,0,0,0
  base-10 prefix from full retained base-6 stream (10556 residues; converged from saved 10000): 0.100298464387428808798655748522380295329364169376809065307947…
24B mod 12: 6,9,9,3,7,7,9,6,1,10,9,3,3,3,8,1,1,1,1,3,9,7,7,2,11,5,10,11,9,7,11,0,11,10,9,8,6,1,3,10,0,0,8,3,3,11,11,0,0,0
24B mod 6: 0,3,3,3,1,1,3,0,1,4,3,3,3,3,2,1,1,1,1,3,3,1,1,2,5,5,4,5,3,1,5,0,5,4,3,2,0,1,3,4,0,0,2,3,3,5,5,0,0,0
  base-10 prefix from full retained base-6 stream (10555 residues; converged from saved 10000): 0.099697963367486600437740388202808019428153325393853857945612…
```

Each base-10 line is calculated from the complete retained lane, then compared
with the corresponding saved 10,000-term prefix. Its 60 shown decimal places are
tail-certified: no continuation after the retained data can alter any displayed digit.

## Corpus and independent review

`blocks/` contains 150 sealed 1,000-event compact blocks: 50 per lane. Run
`make corpus-check` for archive/checksum and decoded-chain validation. The
retained Go producer is the reproducible search path; `DATA_FORMAT.md` and
`INDEPENDENT_VERIFICATION.md` define the separate fresh-implementation review
path. `sha256sum -c SHA256SUMS` checks the package inventory.
