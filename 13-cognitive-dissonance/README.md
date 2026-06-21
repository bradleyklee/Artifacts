# Circle-lattice minimal working example

This archive is a small, self-contained reproduction package for two different
ways a closed Euclidean disk can select structure from the square integer
lattice. It is intentionally data-first: exact rational checks read preserved
certificate text, extract normalized witness data, and generate every SVG
figure from that checked data. No image generation, raster tracing, OCR, or
floating-point membership test is used to determine a configuration.

## Problem

The package contains two deliberately separate models. They share circles and
integer coordinates, but they do **not** share the same notion of what a
configuration is.

### N=18 — unit-square / polyomino model

A stored coordinate `(i,j)` names the unit square
`[i,i+1] × [j,j+1]` in the standard lower-left-corner grid. A unit square is
selected exactly when all four of its lattice vertices are in or on the closed
disk. That condition contains the whole square because a disk is convex.

For each of the four supplied witness disks, the checker performs two tests:

1. **At least 18:** all 18 listed unit squares have all four vertices in the
   closed disk.
2. **No more than 18:** it enumerates every lattice vertex in a certified
   finite box containing the disk, then enumerates every possible unit square
   whose four vertices are in the disk. This examines all possible ambient
   interior vertices together, including any that could complete another unit
   square. The resulting induced set has no more than 18 squares.

The implementation additionally checks the stronger exact equality: the
induced set is the listed 18-cell polyomino, with no missing or extra squares.
It also checks that the disk's full lattice-vertex set equals the union of the
listed squares' vertices.

### N=45 — lattice-site / polystick model

A stored coordinate `(i,j)` is a selected physical lattice point of `Z²`, not a
unit square. The circle selects the site set exactly by

`D(C,r) ∩ Z²`.

A polystick picture draws one dot per selected lattice point and unit bars only
between horizontally or vertically adjacent selected points. It never gives
sites filled-square semantics.

For each of the twelve supplied witness disks, the checker performs two tests:

1. **At least 45:** all 45 listed lattice vertices are in or on the closed
   disk.
2. **No more than 45:** it exhaustively enumerates every integer lattice
   vertex in a certified finite box containing the disk. There are no additional
   lattice vertices in or on the disk.

The implementation reconstructs each N=45 circle from its anchor pair and
rational sweep parameter before doing that full-lattice test. It additionally
checks the listed centroid, circle center, radius squared, and the twelve D4
classes.

## Inputs and exact arithmetic

The raw source certificates are preserved unchanged here:

- `data/certificates/n18_bidirectional_vertex_sweep_certificate.txt`
- `data/certificates/n45_site_model_polystick_circle_certificate.txt`

`code/bootstrap_data.py` reads those files and writes normalized JSON fixtures.
`make data-check` repeats the extraction and refuses to continue unless it
matches the committed files:

- `data/n18_witnesses.json`
- `data/n45_witnesses.json`

All exact membership tests use Python's standard-library `fractions.Fraction`:

`(x - Cx)^2 + (y - Cy)^2 <= r^2`

The boundary is included because the disks are closed. For each witness, the
checker derives an integer bounding box that is guaranteed to contain every
lattice point in the disk, then scans that full finite box.

## Build

Only Python's standard library is required for the exact checker and the SVG
renderer.

```sh
make check       # re-extract raw certificate data and run four concise exact checks
make plots       # check first, then write data-generated SVG figures
make previews    # optional PNG contact sheets; requires cairosvg
make build-info  # record interpreter/platform plus SHA-256 digests
make archive     # make check + plots + optional previews + build info + ZIP
```

`make check` prints the two certificate files being read, the two normalized
witness-data files being checked, and only these four summaries:

```text
Check at least 18 unit squares interior: True (4/4)
Check no more than 18 unit squares interior: True (4/4)
Check at least 45 lattice vertices interior: True (12/12)
Check no more than 45 lattice vertices interior: True (12/12)
```

`make plots` says which two plot families it is building and the destination
directory. The renderer always reruns the exact checker before it writes a
figure.

## Outputs

After `make plots`:

- `build/plots/n18_contact_sheet.svg` — four disk-bounded N=18 polyomino
  configurations.
- `build/plots/n45_contact_sheet.svg` — twelve disk-bounded N=45 polystick
  configurations.
- `build/plots/n18_W*.svg` and `build/plots/n45_S*.svg` — individual panels.
- `build/plots/index.html` — local index page linking the SVG outputs.
- `build/verification_report.txt` — the same concise four-line check summary
  printed by `make check`.

SVG is the primary reproducible format. PNGs, where made, are only raster
previews converted from those data-generated SVGs.

## Scope and non-claims

This package verifies the supplied disks and their listed configurations. It
does not prove that these witness lists exhaust every possible circle
configuration outside the hereditary search regimes stated in the original
certificates. In particular, exact verification of the listed N=18 and N=45
configurations is not by itself a global optimality or classification proof.
