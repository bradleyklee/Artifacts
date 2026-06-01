# 07. tri-searching

This artifact searches equilateral-triangle matching-rule families.  There are
two CCW triangle prototiles, `ABC` and `DEF`; reflected copies are forbidden.
The default `anchored` family requires `AB=DE` and forbids every other join
involving `AB`.  The remaining symmetric joins on `{BC, CA, DE, EF, FD}` supply
15 optional bits, so there are `2^15 = 32768` default rule masks.

A second `unrestricted` family retains mandatory `AB=DE` but permits every
other symmetric edge join, including joins involving `AB`, as one of 20
optional bits.  That follow-up space has `2^20 = 1048576` masks.

A third `free` family makes all 21 unordered symmetric joins optional, with no
mandatory edge join.  It has `2^21 = 2097152` labeled masks.  In this family,
independent cyclic relabeling of `ABC` and `DEF`, together with swapping the
two prototiles, acts by an 18-element symmetry group.  The search tests only
the lexicographically least mask in each orbit, while reporting periodic
coverage back in the full labeled mask space.

The current result is a bounded filtering calculation for this anchored family.
Reflections are forbidden: only the three cyclic CCW rotations of each
prototile are allowed.  At the default bounds, 40 masks remain for further
search.  In addition to the periodic-certificate report, the artifact now also
generates a second PDF showing one depth-7 completion witness for each surviving
mask.

## Result at the default bounds

The Make interface uses a side-scale parameter `PERIODIC_DEPTH=N`; it tests all
ordered periodic parallelograms `W x H` with `W*H <= N^2`.  The default is
`PERIODIC_DEPTH=3`, hence periodic area at most 9, followed by finite completion
through depth 7:

```text
minimal_periodic_certificates = 43
periodically_pruned            = 27504
dead at completion depth 1     = 4148
dead at completion depth 2     = 936
dead at completion depth 3     = 140
survivors through depth 7      = 40
```

Thus, within this 15-bit anchored search space and at these bounds, 27,504
masks contain a periodic certificate with torus area at most 9, and 5,224
additional masks fail finite completion by depth 3.  The remaining 40 masks
complete depth 7 and are not eliminated by the tested periodic tori.

## Initial fully free smoke test

The `free` family has been checked only at the smallest exploratory bounds so
far: periodic scale `N=1` and completion depth 1.  Under the 18-action symmetry
quotient, the `2097152` labeled masks reduce to `117680` canonical masks.  At
these weak bounds:

```text
minimal one-tile certificate orbits = 1
one-tile-pruned labeled masks        = 491520
minimal 1x1 periodic certificate orbits = 3
periodically pruned labeled masks    = 1273609
canonical masks surviving depth 1   = 41708
```

This is only a feasibility check for the free pipeline; it is not yet a final
search result.

## Build

Install the SAT dependency, then run the artifact.  The SVG/PDF renderer uses only the Python standard library:

```bash
python3 -m pip install -r requirements.txt
make all
```

Generated files are:

```text
data/periodic_certificates.txt          canonical periodic witness records
triangle_periodic_certificates.pdf      illustrated certificate report
triangle_survivor_configurations.pdf   survivor depth-completion report
data/periodic_certificates.txt          canonical periodic witness records
data/survivor_configurations.txt        surviving depth-completion witness records
out/periodic_certificate_svgs/          one SVG panel per certificate
out/survivor_configuration_svgs/        one SVG panel per survivor
out/search_summary.txt                  SAT pruning and completion counts
out/survivors.txt                       surviving masks at the chosen bounds
```

The search bounds and SAT backend are parameterizable:

```bash
make all PERIODIC_DEPTH=3 COMPLETION_DEPTH=7 SOLVER=glucose4

# for example, test every torus with area at most 5^2 = 25
make all PERIODIC_DEPTH=5 COMPLETION_DEPTH=7 SOLVER=glucose4

# run the 20-bit follow-up search without generating a potentially huge survivor PDF
make unrestricted PERIODIC_DEPTH=3 COMPLETION_DEPTH=7 SOLVER=glucose4

# explicitly generate separate unrestricted reports after choosing useful bounds
make unrestricted-reports PERIODIC_DEPTH=3 COMPLETION_DEPTH=7 SOLVER=glucose4

# run the fully free 21-bit search on canonical symmetry representatives
make free PERIODIC_DEPTH=1 COMPLETION_DEPTH=1 SOLVER=glucose4

# free periodic certificates are safe to render even at weak bounds
make free-periodic-pdf PERIODIC_DEPTH=1 SOLVER=glucose4

# render free survivors only after a run has reduced the survivor count enough
make free-survivor-pdf PERIODIC_DEPTH=3 COMPLETION_DEPTH=7 SOLVER=glucose4
```

`make verify` checks the recorded default result: 43 minimal periodic
certificates and 40 masks surviving the periodic and finite-completion tests.

## Code organization

`src/triangle_sat_search.py` is the direct geometric SAT search.  Each
triangular cell chooses one of six orientation-preserving states: the three
cyclic rotations of CCW `ABC` and the three cyclic rotations of CCW `DEF`.
Reflected tiles such as `ACB` or `DFE` are not permitted.  Shared edges impose
either a mandatory join in the anchored families, a forbidden join, or one of
the chosen family's optional rule variables.  A particular rule mask is passed
to a reusable SAT instance by assumptions.  Use `--family anchored`,
`--family unrestricted`, or `--family free` when invoking the script directly.
For `free`, the program canonicalizes rule masks under the 18 cyclic/swap
symmetries before SAT solving.

Periodic testing uses wrapped triangular parallelograms.  One repeated-tile
periodic solutions are extracted and counted separately before the general
torus search.  From each satisfying torus the program extracts the optional
joins actually used; this smaller mask is a periodic certificate, and every
rule mask containing it can be pruned.  In the `free` family all symmetry images
of a certificate are pruned as the same orbit.  Completion testing uses
expanding finite patches of 13, 37, 73, ... triangles; an unsatisfiable patch
is a rigorous death at that depth.

`src/triangle_export_periodic_records.py` reruns the periodic certificate
search, reconstructs one witness torus for every inclusion-minimal certificate,
and writes a plain-text record file.  Witness placements are canonicalized by
torus translation before writing.

`src/triangle_render_periodic_report.py` reads those records, generates SVG
panels using triangle geometry and size-scaled interior vertex letters, and
composes them into the PDF report using only the Python standard library.  The
two tile families use light green and light blue backgrounds.  The report
groups panels by witness torus type so that larger witnesses remain readable.

`src/triangle_export_survivor_records.py` reruns the periodic and finite
completion filters, then reconstructs one depth-`D` completion witness for each
surviving mask.  It writes a second plain-text record file describing those
largest currently retained finite configurations.

`src/triangle_render_survivor_report.py` reads the survivor records, renders one
panel per surviving mask using an interior triangular notch on the distinguished
edge and the same light green/light blue tile backgrounds, and assembles a
multi-page PDF showing the largest retained configurations at the chosen
completion depth.

## Reading the records

Each record begins with a mask and the torus on which it is witnessed:

```text
record 1
mask 0x0090
bits 2
torus 1 1
rules BC=FD,CA=EF
...
end
```

For `anchored` and `unrestricted`, the mandatory join `AB=DE` is common to all
records; the `rules` line records only optional joins used by the certificate.
For `free`, every displayed join is optional and certificate masks are written
in their canonical symmetry representative form.
