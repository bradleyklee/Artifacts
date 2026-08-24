# Benchmark 0 interpretation — frozen v0 result

## Audit trail

- Corpus/exploratory graph snapshot commit: `0a8aa9d`
- Frozen benchmark specification/engine commit: `b875fef`
- Scored artifacts were generated only after `b875fef`.

Manifest hashes are in `manifest.json`. The benchmark rejects a task if any
checkpoint evidence appears in the initial task/query/agent instructions. Guided
crawlers may inspect target title/key only; they do not see target bodies,
checkpoint evidence, shortest paths, or rank scores when choosing an edge.

This is an anti-confirmation-bias protocol, not a claim that the benchmark
author had literally no prior knowledge of the corpus. The task author knew the
Beads domain and the candidate ranking families. A larger benchmark should add
independently authored or mechanically sampled operational tasks.

## Result

On the 18-node / 49-edge source-derived fixture, the strong form of the
"inverse PageRank" hypothesis is **not supported** by the frozen task benchmark.

With a flat reader, authority-oriented priors are best:

- HITS authority: 2.50 recalled bodies on successful tasks
- indegree: 2.50
- PageRank: 2.75
- reverse PageRank: 3.50
- outdegree: 3.75

All flat rankers fail the same one task (`soft-knowledge-link`) because the
literal query `related` matches only `Dependencies and Gates`; the decisive
`Graph Links` memory is reachable by reference but is not itself a lexical
match. Crawling turns every ranking condition to 9/9 success.

The branching penalty is real. Under unguided DFS:

- PageRank: 4.56 bodies / 3.56 edges
- reverse PageRank: 4.78 / 3.78
- outdegree: 5.00 / 4.00

Under title/key-guided DFS:

- PageRank: 3.33 bodies / 2.33 edges
- HITS hub: 3.00 / 2.00
- outdegree: 3.44 / 2.44
- reverse PageRank: 3.56 / 2.56

Thus **HITS hub improves enough to beat PageRank slightly under guided DFS**, but
raw outdegree and reverse PageRank still do not. HITS hub versus PageRank is
2 task wins, 5 ties, 2 losses; its lower mean is driven by a few large portal
wins rather than broad dominance.

Across the more conservative guided BFS policy, authority wins again:

- HITS authority: 2.33 bodies
- indegree: 2.56
- PageRank: 2.67
- outdegree: 3.11
- reverse PageRank: 3.22
- HITS hub: 3.33

## What the trajectories show

### A hub can be an excellent portal

For `merge-conflict`, HITS-hub places `Merge Conflicts` first and resolves all
four checkpoints in one body. PageRank starts at `Troubleshooting`; guided DFS
then wanders through Doctor, Database Corruption, Sync Concepts, Sync Setup and
Worktrees before finally reaching `Merge Conflicts`: 7 bodies versus 1.

### High outdegree can also be a trap

For `ready-missing`, PageRank begins at `Dependencies and Gates`, resolves 67%,
then follows one guided edge to `bd ready` for 100%: 2 bodies / 1 edge.
Outdegree begins at the five-outlink `How Beads Works` hub. It reaches the same
67% immediately but explores five neighboring bodies before reaching `bd ready`:
7 bodies / 6 edges. Five recalls add no checkpoint knowledge.

### Crawling can recover a lexical miss

For `soft-knowledge-link`, the query `related` returns only `Dependencies and
Gates`. Flat reading remains at 0%. Guided BFS follows its references and reaches
`Graph Links in Beads`; that single body resolves all three checkpoints and the
task moves 0% -> 100%. This is a concrete benefit of preserving reference data
independent of which static ranking wins.

## Relation to the earlier structural inversion

The exploratory graph-only analysis found PageRank negatively correlated with
downstream reachability and reverse PageRank positively correlated. That result
is still a valid structural observation on this fixture: authority and
navigability are different graph properties.

But the frozen task benchmark shows that **more downstream reach is not the same
as lower cost to useful knowledge**. Reachability is beneficial only when the
crawler can choose productive branches cheaply enough. At v0's deliberately
simple title/key guidance level, hubness sometimes helps but branching entropy
usually consumes the gain.

So the current hypothesis becomes narrower and more testable:

> Authority/indegree should be the default cheap Beads pre-order. A hub-oriented
> prior becomes competitive only for consumers whose edge-choice precision is
> high enough to exploit portal nodes without paying their branching cost.

The large 180-page/site and repo-wide citation census is still required before
making a product recommendation or a claim about power-law structure.
