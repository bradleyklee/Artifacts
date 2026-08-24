# Benchmark 0 — Authority vs navigation priors

This is the frozen first benchmark for ranked Memory discovery.

## Experimental constants

- Corpus is a pre-existing normalized Memory snapshot. The v0 fixture was
  committed before this benchmark specification.
- Discovery is a case-insensitive **binary substring** predicate across key,
  aliases, title, and body.
- Benchmark 0 returns **all** lexical matches in the static corpus order. There
  is no pagination variable yet.
- Search results are compact summaries. Bodies enter context only on explicit
  recall.
- Reference traversal exposes target identity/title/key before recall, never a
  target body.
- Knowledge resolution is not model confidence. Each task has pre-registered
  evidence checkpoints. A checkpoint resolves only when an explicitly recalled
  body contains its frozen evidence.
- Task admission rejects any checkpoint whose evidence already occurs in the
  task, query, or benchmark agent instructions; therefore every admitted trial
  starts at 0% by construction.

## Independent variables

Static Beads ordering:

`alphabetical`, `id`, `random-fixed`, `indegree`, `outdegree`, `pagerank`,
`reverse-pagerank`, `hits-authority`, `hits-hub`.

Agent return-data policy:

- `flat`: recall lexical matches in returned order; never crawl.
- `dfs`: depth-first reference crawl from each lexical seed, source link order.
- `bfs`: breadth-first reference crawl from each lexical seed.
- `shallow-guided`: one reference level; target ordering uses only task/query
  overlap with target title/key.
- `guided-dfs`, `guided-bfs`: full graph crawl, with the same title/key-only
  edge guidance.

The guided policies are intentionally simple stand-ins for an agent that can
choose among links. They use no target body, no hidden checkpoint, no shortest
path, and no rank score.

## Primary observation

For every `(task, ordering, policy)` the benchmark writes an exact trajectory
showing every recall/reference step and the knowledge state after the step:

`0% -> ... -> 100% task-unblocked`.

Primary cost is recalled bodies to first 100% resolution. No-gain recalls and
traversed edges expose branching/search waste.

## Anti-confirmation-bias audit

The intended Git history is:

1. corpus snapshot committed;
2. benchmark tasks, queries, checkpoints, rankers, policies and engine committed;
3. results generated in a later commit.

Do not edit the frozen v0 spec after seeing v0 results. A changed benchmark is
v1 and gets new hashes/results.
