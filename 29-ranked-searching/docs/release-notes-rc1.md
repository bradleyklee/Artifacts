# RC1 release notes

## Included

- compact B1 deterministic 1–2 skip-list implementation;
- independent verification suite;
- invariant and 2–3-tree/state-census theory notes;
- raw B0/B1 optimization measurements;
- ranked Memory Beads use case;
- hyperlink-preserving corpus builder;
- query-independent structural rankers;
- mechanical binary lexical discovery;
- agent crawl benchmark with auditable 0% -> 100% knowledge trajectories.

## Provenance policy

RC1 cites the academic algorithmic source directly:

J. Ian Munro, Thomas Papadakis, and Robert Sedgewick, “Deterministic Skip
Lists,” SODA 1992, pp. 367–375, DOI 10.1145/139404.139478.


## Evidence boundary

The skip-list implementation has strong deterministic finite verification and
measured optimization evidence. The Memory ranking/crawling results remain
hypothesis formation: the checked-in 18-node task corpus is a benchmark-smoke
corpus, not enough evidence for choosing PageRank, inverse PageRank, or another
prior. RC1 includes the corpus-expansion machinery so larger implementations can
run the same protocol against much larger authored hyperlink graphs.
