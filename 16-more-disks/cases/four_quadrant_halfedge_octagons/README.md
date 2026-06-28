# Four-quadrant half-edge hard octagons

## Geometry

- outer square side: `2 + 2*sqrt(2)`;
- mover: fixed-orientation regular octagon of edge `1/2`;
- allowed starts: the four quadrant centroids
  `(±(1+sqrt(2))/2, ±(1+sqrt(2))/2)`;
- start velocities: cardinal unit vectors;
- search arithmetic: exact `Q(sqrt(2))`;
- initial atlas: N=2 and N=3, reduced under D4.

## Stored exact-search result

- N=2: 16 D4 classes; all `RETURN`.
- N=3: 32 D4 classes after substituting the supplied class-8 continuation:
  12 `RETURN`, 15 `UNKNOWN_CORNER`, 3 `REJECT`, 2 `COMPLEXITY_CUTOFF`.

The two capped cases are N3 class 08 and class 31. Their complete stored
lex-min ternary words are exported to per-digit CSV in `data/ternary/`.

## Review files

- `code/evolve_four_site_search.go` — primary exact search source.
- `data/search/four_site_watch2048.json` — complete enumeration checkpoint.
- `data/search/class_08_continuation_to_cap128.json` — extension that changes
  class 08 from `LOW_COMPLEXITY_WATCH` to `COMPLEXITY_CUTOFF` at batch 2357.
- `data/summary/n3_final_class_summary.csv` — human-readable final class list.
- `tools/extract_ternary.py --check` — confirms the CSV exports are derived
  exactly from stored JSON fields.

## Claim boundary

The `COMPLEXITY_CUTOFF` label means an exact coefficient bit-length exceeded
128. It is evidence of growth under this search and cutoff policy, not a proof
of chaos, nonperiodicity, or normality of the ternary words.
