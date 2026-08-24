# Building the pinned Beads documentation corpus

```sh
cd beads-usecase
./scripts/acquire-pinned-beads-docs.sh \
  ./source/beads-8d86c06 \
  8d86c06bf231cbc0907436a111fb7b75d39ee12d

go run ./cmd/corpusbuild \
  -repo ./source/beads-8d86c06 \
  -source-ref 8d86c06bf231cbc0907436a111fb7b75d39ee12d \
  -scope published-human \
  -out results/corpus-v1/published-human

go run ./cmd/corpusbuild \
  -repo ./source/beads-8d86c06 \
  -source-ref 8d86c06bf231cbc0907436a111fb7b75d39ee12d \
  -scope published-all \
  -out results/corpus-v1/published-all
```

Each output directory contains:

- `manifest.json` — source ref and content/graph/citation hashes;
- `memories.json` — canonical imported Memory records;
- `citations.json` — every authored hyperlink occurrence;
- `navigation.json` — presentation navigation kept out of centrality;
- `graph-stats.json` — degree/concentration/tail diagnostics;
- `degree-ccdf.csv` — exact in/out degree CCDF counts.

Do not run a scored benchmark if the corpus or graph hash differs from the
pre-registered benchmark manifest.
