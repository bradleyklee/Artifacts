# Beads Ranked-Memory Use-Case PoC

This is a first-class practical experiment built on the optimized deterministic
1-2 skip-list implementation. It is intentionally separate from both the
implementation and its verification suite.

## Question

Given a fresh task and no Beads documentation in context, does discovery order
make the task-essential Memory records visible sooner?

The ranker never sees the task's `required_all` labels. Those labels are held by
the evaluator only. They certify the first point at which the discovery stream
contains enough pre-labelled source material to make completion possible.

## Corpus

`corpus.IngestDocs` converts a Beads `docs/` checkout into one Memory record per
Markdown page. The PoC Memory projection follows issue #5877's durable concepts:
canonical ID, project ID, title, complete Markdown body, optional key/aliases,
archive time, explicit directional references, and stored provenance.

Markdown links become non-blocking informational references. PageRank is
computed only from that relation graph. The checked-in `corpus/testdata/docs`
is a small source-derived fixture so the experiment runs without network
access; production trials should point `-docs` at a complete pinned Beads docs
checkout.

## Ordering controls

- `alphabetical`: title order, ordinary sorted-slice control.
- `pagerank`: query-independent global graph centrality.
- `lexical`: cheap IDF-weighted query/document overlap.
- `hybrid`: 75% normalized lexical + 25% normalized PageRank.

All non-alphabetical orderings are materialized in the optimized deterministic
skip list with stable ID tie-breaking.

## Run

```sh
go test ./...
go run ./cmd/memtrial \
  -docs corpus/testdata/docs \
  -tasks tasks/tasks.json \
  -out results/pilot.json \
  -emit-corpus results/pilot-memories.json
```

The deterministic harness is not a substitute for an agent trial. Its purpose
is to freeze corpus, task labels, ordering, and metrics before a zero-prior
agent runner is introduced.
