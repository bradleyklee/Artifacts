# 30. JITI Lisp Fibonacci experiment

This artifact preserves a terminal session using **JITI**, an interactive
Common Lisp application environment, to examine a generated Fibonacci function
and a second function that draws randomized connected lattice regions. It is an
experiment in conversationally developed, inspectable code—not a verified
uniform sampler, and not yet a reimplementation of the earlier Fibonacci
spiral. The unedited session appears in [`terminal-transcript.txt`](terminal-transcript.txt).

## Experiment

The session begins with `./image-repl --store pilot-workspace`, recovering a
workspace using the `gpt-6-luna` model. The interactive `/help` menu advertises
chat, Lisp execution, development, history, rollback, status, and memory commands.
The recorded operations exercise `/functions`, `/execute`, and `/describe`, not
the development loop itself. Three functions are visible: `COUNTER`, `FIBONACCI`,
and `FIBONACCI-DEPICT`.

`FIBONACCI` uses exact-integer fast doubling and correctly returns 3, 5, and 8
for arguments 4, 5, and 6 in the transcript. `FIBONACCI-DEPICT` reports
F(0) through F(N), fills connected regions of Fibonacci area in a square
lattice, and prints an ASCII boundary diagram. For N=6, the reported occupied
area is 20 cells in a 5 × 5 square, leaving five unoccupied cells. Successive
unseeded executions show different packings. `/describe` paginates the 6,544
character definition using offsets 0 and 4096, making the full source visible
without silently truncating the result.

The transcript records **execution and inspection of existing definitions**;
it does not include the original natural-language prompt, a `/develop` turn, or
an independently executed test suite. The source is preserved in the transcript
rather than copied into a separate `.lisp` file, to keep this artifact to the
two original requested files.

## What is wrong or not yet established

1. **Wrong geometric target for a spiral.** The Lisp function builds randomized
   connected polyomino-like regions along a lattice path. It does not construct
   Fibonacci squares, quarter-circle arcs, a continuous spiral, or a Braille
   raster. A successful polyomino picture is not evidence of a Fibonacci spiral.
2. **Uniformity is unsupported.** The code starts with a serpentine Hamiltonian
   path, performs a bounded number of randomized path changes, shuffles labels,
   and partitions the path into Fibonacci-sized regions. Neither uniform
   sampling of paths nor uniform sampling of resulting labeled partitions
   follows from these steps. Different partitions can have different numbers
   of path representations; some valid partitions might be unreachable.
3. **Geometry needs independent verification.** A consecutive segment of a
   valid nearest-neighbor path is connected, but this transcript does not prove
   every path mutation preserves the required invariant or test every emitted
   region for connectivity, exact area, overlap, and bounds.
4. **Randomness and scaling are uncharacterized.** The source uses an explicit
   32-bit linear congruential generator and an optional integer seed. The
   transcript does not test seed reproducibility, small-case frequencies,
   coverage of valid packings, performance at larger N, or the choice of
   random-step budget.
5. **Interactive reliability remains to be demonstrated.** `/help` advertises
   development, recovery, revision history, and rollback, but the captured
   session demonstrates only discovery, introspection, and execution. The
   printed source also has formatting artifacts from the terminal interface.

These are limits of the *observed implementation and evidence*, not established
defects in Common Lisp itself or in JITI's unexercised features.

## Next experiments

- **Specify the intended sample space.** Decide whether the goal is a random
  connected packing, an approximately uniform distribution on a defined set of
  labeled packings, or the geometric Fibonacci spiral. Do not conflate these.
- **Verify the current sampler first.** For small N, enumerate allowable grids
  independently where feasible; check areas, connected components, bounds,
  total occupancy, and duplicate labels. Compare seed-repeated output, observed
  frequencies, and reachability against an explicit baseline. If uniformity is
  required, supply a proof or a validated sampling method rather than inferring
  it from randomness.
- **Recreate the Braille Fibonacci spiral.** Translate the prior construction
  into Lisp using deterministic Fibonacci-square placement, successive
  tangent quarter-circle arcs, and Unicode Braille rasterization. Preserve
  the distinction between geometric construction and terminal display.
  Compare its output and invariants with the earlier Sol implementation,
  including square dimensions, nonoverlap, tangency, endpoint continuity,
  prefix preservation, and bounded raster behavior.
- **Exercise conversational development.** Capture a fresh JITI session that
  starts with a plain-English specification, creates the Lisp definitions,
  runs adversarial tests, repairs failures, and verifies restoration after a
  controlled error. Record commands, outputs, revisions, and any failure modes.
- **Retain two separate benchmarks.** Evaluate the stochastic polyomino
  sampler on distributional properties and the Braille spiral on geometric
  correctness; do not let one serve as the other's acceptance criterion.

## Related work

- Geoffrey Huntley, [Lisp and conversational development](https://ghuntley.com/lisp/).
- [Werketron-Artifacts: 01-Spirale-Fibonacci](https://github.com/bradleyklee/Werketron-Artifacts/tree/main/01-Spirale-Fibonacci),
  with specification, candidates, and verification work.
- [Sol candidate implementation and README](https://github.com/bradleyklee/Werketron-Artifacts/tree/main/01-Spirale-Fibonacci/candidates/sol),
  which builds a Fibonacci-square tiling and Braille arc display. The quarter-circle
  construction approximates a Fibonacci spiral; it is not an exact logarithmic
  golden spiral.

This is a preserved exploratory artifact, not an accepted mathematical result
or a certified JITI capability demonstration.
