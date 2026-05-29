# Spectre SAT tools

This directory contains a standalone SAT route for generating much larger finite
patch data for the reduced two-hex model.

The main point is to stop relying on the Python backtracking search for large
balls.  The script writes a solver-agnostic DIMACS CNF file.

## Generate CNF

```bash
python3 spectre_sat.py cnf --radius 10 --out out/r10.cnf
```

This also writes:

```text
out/r10.map
```

The `.map` file maps SAT variables back to:

```text
q r orient tile rot labels
```

## Solve with an external solver

Install one of:

- kissat
- cadical
- minisat
- glucose
- cryptominisat5
- picosat

Examples:

```bash
kissat out/r10.cnf > out/r10.model
python3 spectre_sat.py decode --model out/r10.model --map out/r10.map --out out/r10.dat
python3 spectre_sat.py draw --dat out/r10.dat --out out/r10.svg
```

Or, if a supported solver is on PATH:

```bash
python3 spectre_sat.py all --radius 10 --outdir out
```

## What the CNF encodes

For every hex cell in a radius-R hex ball:

- exactly one of 12 tile states is chosen:
  - H0 rot 0..5
  - H1 rot 0..5
- the central 7-hex supertile is fixed
- every adjacent edge must satisfy the 33 reduced directed edge rules
- every fully present three-hex vertex must satisfy the reduced vertex rules

## Why this matters

The Python backtracking code reached radius 8, but larger finite balls are better
handled by CDCL SAT solvers.  This tool is meant to produce radius 10, 12, 15,
etc. candidate data locally, then decode/draw it with the same supertile-boundary
scanner.


## No matplotlib required

The `draw` subcommand now writes SVG directly and does not import matplotlib:

```bash
python3 spectre_sat.py draw --dat out/r10.dat --out out/r10.svg
```

Optional center tile labels:

```bash
python3 spectre_sat.py draw --dat out/r10.dat --out out/r10.svg --labels
```


## Cleaner drawing defaults

The SVG renderer now draws red outlines only by default.  This avoids the dense
red smear caused by filling every embedded supertile.

Clean outline drawing:

```bash
python3 spectre_sat.py draw --dat out/r10.dat --out out/r10.svg --linewidth 1.4
```

If overlaps are important, prefer numbers instead of fill:

```bash
python3 spectre_sat.py draw --dat out/r10.dat --out out/r10_counts.svg --overlap-numbers
```

Subtle overlap fill is optional and off by default:

```bash
python3 spectre_sat.py draw --dat out/r10.dat --out out/r10_shaded.svg   --overlap-fill --overlap-alpha 0.06 --linewidth 1.2
```


## Stroke-size fix

SVG stroke widths are in the same coordinate units as the hex geometry.  A hex
edge has length about `1`, so a linewidth like `1.4` is huge and will look like
red paint.  Use small values:

```bash
python3 spectre_sat.py draw --dat out/r10.dat --out out/r10.svg
```

Default red line width is now:

```text
0.045
```

Useful range:

```bash
python3 spectre_sat.py draw --dat out/r10.dat --out out/r10_thin.svg --linewidth 0.025
python3 spectre_sat.py draw --dat out/r10.dat --out out/r10_med.svg  --linewidth 0.045
python3 spectre_sat.py draw --dat out/r10.dat --out out/r10_bold.svg --linewidth 0.070
```

The red outlines now use:

```text
stroke-linecap="butt"
stroke-linejoin="miter"
```

so they no longer have rounded ends.


## Current draw defaults

The bad edit that disabled overlap fill by default has been reverted.

Current drawing behavior:

```text
overlap fill: on by default
red outline width: 0.045 SVG geometry units
line caps: butt
line joins: miter
```

Normal command:

```bash
python3 spectre_sat.py draw --dat out/r10.dat --out out/r10.svg
```

Disable fill only when explicitly wanted:

```bash
python3 spectre_sat.py draw --dat out/r10.dat --out out/r10_no_fill.svg --no-overlap-fill
```

Thin outlines:

```bash
python3 spectre_sat.py draw --dat out/r10.dat --out out/r10_thin.svg --linewidth 0.025
```


## Updated defaults

The draw defaults now use:

```text
overlap fill: ON
overlap fill color: black
overlap alpha scale: 0.18
red outline width: 0.070 SVG geometry units
linecap: butt
linejoin: miter
```

Normal command:

```bash
python3 spectre_sat.py draw --dat out/r10.dat --out out/r10.svg
```

Thinner outlines if needed:

```bash
python3 spectre_sat.py draw --dat out/r10.dat --out out/r10_thin.svg --linewidth 0.045
```

Disable overlap fill only if explicitly wanted:

```bash
python3 spectre_sat.py draw --dat out/r10.dat --out out/r10_no_fill.svg --no-overlap-fill
```
