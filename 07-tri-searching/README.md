# 07. tri-searching

This artifact searches a restricted family of equilateral-triangle matching
rules.  There are two triangle prototiles, `ABC` and `DEF`.  The edge join
`AB=DE` is mandatory and is the only permitted join involving `AB`.  The
remaining symmetric joins on `{BC, CA, DE, EF, FD}` supply 15 optional bits, so
there are `2^15 = 32768` rule masks.

The current result is a bounded no-go calculation for this anchored family:
every mask is either witnessed periodic on a small torus or cannot complete a
small finite growth patch.

## Result at the default bounds

The default command tests all ordered periodic parallelograms `W x H` with
`W*H <= 10`, then tests finite completion through depth 7:

```text
minimal_periodic_certificates = 49
periodically_pruned            = 28531
dead at completion depth 1     = 2863
dead at completion depth 2     = 1054
dead at completion depth 3     = 320
survivors                       = 0
```

Thus, within this 15-bit anchored search space, every rule mask either contains
a periodic certificate with torus area at most 10, or fails to fill the
completion-depth-3 patch.  This is a bounded computational result for this
specific rule family, not a no-go theorem for triangle matching systems in
general.

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
out/periodic_certificate_svgs/          one SVG panel per certificate
out/search_summary.txt                   SAT pruning and completion counts
out/survivors.txt                        surviving masks; empty at default bounds
```

The search bounds and SAT backend are parameterizable:

```bash
make all PERIODIC_DEPTH=10 COMPLETION_DEPTH=7 SOLVER=glucose4
```

`make verify` checks the recorded default result: 49 minimal periodic
certificates and zero masks surviving the periodic and finite-completion tests.

## Code organization

`src/triangle_sat_search.py` is the direct geometric SAT search.  Each
triangular cell chooses one of twelve oriented states: six orientations of
`ABC` and six of `DEF`.  Shared edges impose either the mandatory join,
a forbidden join involving `AB`, or one of the 15 optional rule variables.
A particular rule mask is passed to a reusable SAT instance by assumptions.

Periodic testing uses wrapped triangular parallelograms.  From each satisfying
torus the program extracts the optional joins actually used; this smaller mask
is a periodic certificate, and every rule mask containing it can be pruned.
Completion testing uses expanding finite patches of 13, 37, 73, ... triangles;
an unsatisfiable patch is a rigorous death at that depth.

`src/triangle_export_periodic_records.py` reruns the periodic certificate
search, reconstructs one witness torus for every inclusion-minimal certificate,
and writes a plain-text record file.  Witness placements are canonicalized by
torus translation before writing.

`src/triangle_render_periodic_report.py` reads those records, generates SVG
panels using triangle geometry and interior vertex labels, and composes them
into the PDF report using only the Python standard library.  The report groups panels by witness torus type so that
the larger `3x3` witnesses remain readable.

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

The mandatory join `AB=DE` is common to all records and is shown in the PDF
panels.  The `rules` line records only optional joins used by the certificate.
