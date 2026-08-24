# Corpus and search protocol hypothesis v1

Status: **hypothesis formation**, not a ranking recommendation.

## Deliverable boundary

This repository is intended to give a larger Memory Beads implementation two
things it can reproduce independently:

1. a deterministic, hyperlink-preserving corpus/search benchmark; and
2. a falsifiable hypothesis about the co-dependent Beads-side and agent-side
   protocol that minimizes context consumed before a task becomes executable.

The benchmark does not require the production store to use this Go skip list or
these exact centrality algorithms. Corpus, graph, search trace, and outcome are
hashed/exported so another implementation can reproduce the experiment.

## Corpus contract

A corpus is not just document bodies. It is:

```
documents + authored directed hyperlinks + provenance
```

For every Markdown/MDX document the ingester records the complete body and a
canonical Memory ID. For every authored hyperlink occurrence it records source,
source line, visible anchor text, raw destination, fragment, parser syntax, and
resolution class.

The centrality graph contains only **unique resolved internal cross-document
edges**. The raw citation table additionally retains repeated occurrences,
unresolved internal links, external links, and same-document fragments. Images
and links appearing only inside code are not crawl edges.

Mintlify `docs.json` navigation is kept separately. It may identify the
published page set and redirects, but sidebar/presentation navigation is not an
authored citation and never enters PageRank/HITS by default.

### Reproducible source

Corpus runs must name an immutable source commit. The current hypothesis-formation
snapshot is:

```
repository: https://github.com/gastownhall/beads
commit:     8d86c06bf231cbc0907436a111fb7b75d39ee12d
```

Use `scripts/acquire-pinned-beads-docs.sh DEST COMMIT` to create a sparse pinned
checkout, then `cmd/corpusbuild` to produce the corpus, citation table, graph
statistics, and hashes.

Useful scopes:

- `published-human`: published documentation excluding generated CLI pages;
- `published-all`: complete published docs including generated CLI pages;
- `docs`: every Markdown/MDX document under `docs/`, published or not;
- `repo`: broad repository Markdown robustness corpus.

The human/all split tests whether generated command pages manufacture a degree
tail or centrality result.

## Fixed discovery mechanism

Discovery is not a semantic ranker. Given a query-independent pre-order `r`, a
query string `q`, and a corpus `M`, Beads walks `r(M)` and applies one binary
case-insensitive substring predicate over key, aliases, title, and body.

Benchmark 0 may return every match to remove pagination as a confounder. Later
runs restore the production-style bounded mechanism: pop, test, append matches
until `K`, then continue from the scan cursor.

## The two optimization knobs

The intended experiment varies only:

```
Beads structural pre-order r  ×  agent consumption/crawl policy π
```

Candidate query-independent priors include alphabetical/stable-ID/random nulls,
indegree, outdegree, PageRank, reverse PageRank, and global HITS authority/hub.
"Global HITS" here means the HITS spectral equations on the complete frozen
corpus graph. It is deliberately not Kleinberg's query-focused root/base-set
retrieval procedure.

Candidate agent policies include flat sequential reading, shallow crawl, DFS,
BFS, and stronger budget-aware/adaptive crawling. An agent may use information
actually exposed by compact reference metadata (for example target title and
anchor text); it may not inspect an unread target body to choose an edge.

## Objective

For task `T`, ordering `r`, and agent policy `π`, minimize the cost at the first
objective unblocking state:

```
J(r, π; T) =
    recalled body tokens
  + separately reported summary/edge metadata tokens
  + failure / budget-exhaustion outcome
```

We report components rather than hiding them inside one arbitrary scalar:

- lexical matches/summaries inspected;
- complete bodies recalled;
- reference edges considered/traversed;
- no-gain reads and backtracks;
- bytes/tokens admitted to context;
- attempts/actions;
- exact first successful environment/checker state.

Tasks, lexical queries, budgets, checkpoints, corpus hash, and graph hash are
frozen before scored ranking conditions run. A task is admitted only when the
fresh agent cannot complete it from the task plus memory-search instructions
alone.

## Current hypothesis

The small validation corpus suggests a tradeoff worth testing at scale, not a
conclusion:

1. **Authority priors** (indegree/PageRank/global-HITS-authority) should be good
   when the agent mainly consumes lexical results sequentially: authoritative
   pages are more likely to contain a direct answer.
2. **Hub/portal priors** (outdegree/reverse-PageRank/global-HITS-hub) can improve
   a capable crawler because a lexical hit can be an entrance to useful
   downstream knowledge.
3. Portal value competes with **branching entropy**. High outdegree may be worse
   for a weak crawler because each extra plausible edge can consume context
   before the productive branch is found.
4. Therefore the best Beads ordering may be conditional on the consuming
   agent's crawl policy. The object of optimization is the pair `(r, π)`, not a
   universal document rank.
5. Raw outdegree may be too noisy; a hub score that rewards links to authorities
   is a plausible better portal prior. This must be tested on a much larger
   authored-link graph before being recommended.

A useful falsification would be that the same authority ordering dominates
across flat, DFS, BFS, and stronger real-LLM policies once corpus size grows. A
useful discovery would be a stable policy-dependent crossover: authority wins
for shallow readers while a portal prior wins for sufficiently competent
crawlers at lower total token cost.

## Evidence status

The existing 18-node/49-edge run is a validation of tracing and benchmark
semantics only. It is too small to establish a citation power law or choose a
production prior. Large-corpus runs should publish degree CCDFs, isolates,
Gini/concentration, unresolved-link rate, and human-only versus generated-doc
results before interpreting PageRank/HITS comparisons.
