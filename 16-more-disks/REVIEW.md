# Review guide for the next window / independent checker

## Review order

1. Read `cases/four_quadrant_halfedge_octagons/README.md`.
2. Inspect the two source JSON files in `data/search/` and compare them against
   the ternary exports in `data/ternary/` using:

   ```sh
   python3 cases/four_quadrant_halfedge_octagons/tools/extract_ternary.py --check
   ```

3. Compile/run the Go program separately. The stored JSON is the claimed result;
   this package does not claim that a rerun will reproduce byte-identical JSON
   without matching flags/environment.
4. For the square negative control:

   ```sh
   python3 cases/four_quadrant_quarter_edge_squares/code/search.py \
     --output /tmp/squares.json
   diff -u cases/four_quadrant_quarter_edge_squares/data/result.json /tmp/squares.json
   ```

5. Treat `visual/` as presentation work only. Its collision-time ledger is tied
   to that render, not an independent exact search certificate.

## Data convention

- CSV ternary rows are `case,digit_index,digit,channel_map,source`.
- Digit indexing is zero-based.
- The `raw_pair_word` and `lex_min_ternary` were copied from the exact-search
  JSON fields. The extract tool regenerates the CSV from those fields.
- No ternary CSV is provided for square runs because no pair-word/ternary
  encoding was generated in that control experiment.
