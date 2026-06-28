# Four-site half-edge search — preliminary exact findings

Geometry: square side `2 + 2*sqrt(2)`; allowed centers are the four quadrant centroids `(±(1+sqrt(2))/2, ±(1+sqrt(2))/2)`; movers are regular fixed-orientation octagons of edge length `1/2`; velocities are cardinal unit vectors.

The evolver is the adapted exact `Q(sqrt(2))` code path used for the L=2 search. This is a first-pass search result, not yet an independently audited artifact.

## Completed enumeration

- N=2: 16 D4 classes, all exact unlabeled returns.
- N=3: 32 D4 classes. Finalized after extending class 8 to the 128-bit cap: {'RETURN': 12, 'UNKNOWN_CORNER': 15, 'COMPLEXITY_CUTOFF': 2, 'REJECT': 3}.

## Complexity-growth cases

- Class 8: `Q[-1,+1] +y; Q[+1,-1] +x; Q[+1,+1] -y`; cap at batch 2357; state bits 129 (position 129, velocity 85); pair collisions 827; all three pair channels active; first 20 lex-min ternary digits `0,1,2,0,0,2,0,0,0,1,0,1,0,1,2,1,2,1,1,2`; mapping `P0/P1->1, P0/P2->2, P1/P2->0`.
- Class 31: `Q[-1,+1] -y; Q[+1,-1] +y; Q[+1,+1] +x`; cap at batch 2045; state bits 129 (position 129, velocity 84); pair collisions 712; all three pair channels active; first 20 lex-min ternary digits `0,1,0,2,1,1,2,1,0,1,1,2,1,2,0,0,2,0,2,2`; mapping `P0/P1->2, P0/P2->1, P1/P2->0`.

The remaining N=3 classes were 12 returns, 15 pair-corner terminals, and 3 rejected shared-component/rule terminals. No unresolved low-complexity watch remains after extending class 8: it too crossed the 128-bit cap.

## Files

- `results/four_site_cap128_watch2048.json`: complete first-pass enumeration, with class 8 at the 2048-batch watch checkpoint.
- `results/class8_to_cap128.json`: independent continuation run for class 8 to the exact 128-bit cap.
- `code/evolve_four_site_search.go`: search source.
