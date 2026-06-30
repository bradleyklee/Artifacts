# Experiment contract

## Shared geometry

The canonical engine evolves fixed-orientation, equal-mass regular polygons in
an axis-aligned square container. Supported shapes are squares, octagons,
dodecagons, and 24-gons. Each has edge length `1/2`; therefore its cardinal
support width is one half of a lattice cell. The declared search family begins
at a `2 x 2` lattice-cell container.

All physics is exact over the common coefficient field
`Q(sqrt(2), sqrt(3))`, with unused coefficients identically zero in the
smaller subfields. No floating-point number participates in event generation,
event ordering, support testing, contact classification, or collision response.

## Collision contract

* Pair collision: equal-mass elastic reflection in one active polygon support
  normal.
* Wall collision: axis-aligned specular reflection at the exact support offset.
* A `PAIR_CORNER`, `WALL_CORNER`, or shared-body same-time batch is terminal.
* A same-time batch with disjoint body supports is resolved as a commuting
  `INDEPENDENT_BATCH`; it must not be misclassified as a shared collision.
* A `CAP` means only that no return or declared terminal was reached through
  the listed finite horizon. It is never a proof of chaos or aperiodicity.

## Exhaustive low families

1. **Square control:** `L=2, N=4`, every distinct-centroid initial placement
   and every ordered cardinal velocity word. `256` raw starts.
2. **Ordinary dodecagon control:** `N=2` centroid/cardinal starts at `L=2`
   and `L=3`. `96` and `576` raw starts, respectively.
3. **Special centered dodecagon family:** two dodecagons initially in an exact
   central face contact, one seed per strictly relative-closing ordered cardinal
   velocity pair and face label. The time-zero face collision is part of the
   certificate and is included as ternary symbol zero.
4. **24-gon threshold family:** `L=2, N=2` centroid/cardinal starts. `96` raw
   starts.
5. **Octagon context family:** `L=2, N=3`, centroid/cardinal starts. `256` raw
   starts. This is retained as a comparison family, not as a video deliverable.

For dodecagons, a ternary digit is `pair_face_label mod 3`; wall contacts do
not contribute a digit. The prescribed centered contact is digit zero in that
word.
