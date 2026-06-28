# 16-more-disks

A handoff directory collecting the experiments run after Artifact 15
(`15-octagon-collisions`). It is deliberately divided by geometry and status so
that a reviewer can distinguish exact search records from preliminary searches
and from visual-only material.

## Contents

- `cases/l2_five_site_halfedge_octagons_preliminary/`
  - earlier L=2 five-site half-edge octagon ternary catalogue.
  - preliminary; needs an independent audit.
- `cases/four_quadrant_halfedge_octagons/`
  - the four-quadrant, three-body half-edge octagon scan.
  - this is the strongest recent exact search record: raw Go source, full JSON,
    continuation for class 8, and exported ternary CSV.
- `cases/four_quadrant_quarter_edge_squares/`
  - negative control using squares of edge 1 in an outer square of edge 4,
    with starts at `(±1,±1)`. Exact-rational Python search and its generated
    result JSON are included.

## Important status discipline

1. The four-quadrant octagon scan reports *complexity cutoffs*, not a theorem
   of chaos or aperiodicity.
2. The L=2 five-site catalogue is explicitly preliminary.
3. The square control is a bounded exhaustive scan of the stated finite start
   atlas; it is not a theorem about all square billiard initial conditions.
4. `visual/` material is not an independent verifier and must not be cited as
   a collision certificate.

Start with `REVIEW.md`, then each case's `README.md`. `make verify` performs
local consistency checks only; it does not independently rederive the octagon
result.

## v2 completeness correction

See `ADDENDUM_v2.md`. The item-15 certificate corpus and its images are under
`reference_item_15/`. Later exploratory branches explicitly identify whether
they do or do not have self-contained collision certificates.
