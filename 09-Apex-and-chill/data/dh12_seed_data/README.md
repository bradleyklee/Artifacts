# DH12 small seed data for finding 600+ and 800+ examples

This is a data-only packet. It intentionally contains no renderer patch code.

Files:

- `records_600_plus_696_seed.jsonl` — 20 closed/chill 696-ish seed records.
- `records_800_plus_seed.jsonl` — 32 records at 804+ / 846 / 852, selected for operator and depth variety.
- `records_combined_small_seed.jsonl` — combined seed set.
- `index.json` — line-by-line record index with cells, status, depth, operator, hash, source.
- `signpost_genes_69x_to_852.json` — strongest 69x→852 signpost genes from the archived comparison.
- `frequency_hints_from_small_seed.json` — top accept/blank frequencies inside this small packet.
- `matrix_convention_minimal.json` — compact 31×64 convention note.

Suggested use:

1. Load `records_600_plus_696_seed.jsonl` as your 600+ parent pool.
2. Load `records_800_plus_seed.jsonl` as your 800+ / 852 parent pool.
3. Mutate around high-frequency 852 accepts/rejects, but preserve diversity from the 696 parents.
4. Use `signpost_genes_69x_to_852.json` as knobs for 69x→852 moves: these are genes common/accepted in 852 and absent or rejected in the 69x pool.

Important: this packet does not certify a renderer. It is search data only.
