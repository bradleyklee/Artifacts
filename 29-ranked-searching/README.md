# Deterministic ranked-memory index — Release Candidate 1

This repository packages a verified deterministic 1–2 skip list, its first-class
Go verification suite, measured representation optimization, and a Memory Beads
search benchmark that uses the skip list as a maintained ranked secondary index.

**RC1 status:** implementation and deterministic verification are release-candidate
quality; the Memory ranking/crawling work is intentionally hypothesis formation.
The current 18-document task run validates the benchmark machinery but is too
small to choose a universal graph prior. The corpus-expansion code is part of the
RC so larger implementations can reproduce the experiment on a pinned corpus.

## Academic basis

The skip-list algorithmic family is:

> J. Ian Munro, Thomas Papadakis, and Robert Sedgewick, “Deterministic Skip
> Lists,” *Proceedings of the 3rd Annual ACM-SIAM Symposium on Discrete
> Algorithms (SODA 1992)*, pp. 367–375. DOI: 10.1145/139404.139478.

The paper establishes deterministic skip-list schemes with logarithmic search,
insert, and delete cost. This repository contains our Go implementation,
stronger executable invariants, exhaustive transition testing, and optimization
measurements.

## Memory system in one picture

```text
                         query-independent graph score
                         (PageRank / indegree / hub / ...)
                                      |
                                      v
+------------------+         +------------------------+
| Go map           |         | deterministic skiplist |
| ID -> Memory     |<-------> | (score, ID) -> ID      |
| canonical body   |         | persistent pre-order   |
+------------------+         +------------------------+
        ^                              |
        | exact recall                 | ordered stream
        |                              v
        |                       mechanical POP/SCAN
        |                              |
        |                       binary lexical test
        |                      key/alias/title/body
        |                         /          \
        |                       no            yes
        |                       |              |
        |                    next pop     compact result
        |                                      |
        +---------------- explicit recall -----+
                                               |
                                               v
                                      agentic interaction
                                      - read body
                                      - follow references
                                      - backtrack / crawl
                                      - request more results
                                               |
                                               v
                                      objective task unblocked
```

There are deliberately three separate layers:

1. **Identity/storage — Go map.** `map[MemoryID]Memory` is the canonical exact
   lookup path for bodies and metadata. Expected lookup/update cost is O(1).
2. **Persistent order — deterministic skip list.** A secondary index stores
   `(rank, stable ID) -> MemoryID`. The rank is computed without seeing the
   query. Insert/delete/rank-change cost is O(log N) worst case for the ordered
   structure; first-element access is O(1), while destructive `PopFirst` also
   pays O(log N) for deletion/repair.
3. **Discovery and reasoning.** Ordered records are mechanically consumed and
   passed through a binary case-insensitive lexical predicate. The predicate
   does **not** produce a relevance score and does not reorder results. Only
   after compact matches are returned does an agent decide what body to recall
   or which reference edge to follow.

The benchmark currently materializes an ordered stream for repeatable trials.
A production implementation can expose the same level-1 skip-list order through
an iterator/cursor; it should not destructively remove records from the
persistent global index merely to serve a query.

## Why map + skip list?

A Go map is excellent for exact identity lookup but carries no maintained rank
order. Sorting a map snapshot costs O(N log N) whenever the order must be
recomputed. The skip list pays more on mutation so that the order is already
maintained when retrieval begins.

For ranked Memory, this gives two different access paths:

```text
exact recall by Memory ID       -> Go map
ordered discovery / top of rank -> skip list
```

Representative local Go 1.23.2 measurements at N=10,000 after the B1 compact
representation optimization:

```text
insert into ranked skip list       ~0.51 us/op
rank update                        ~0.84 us/op
top 10 from maintained order       ~5.0 us
map snapshot + full sort, top 10   ~1.52 ms
```

A plain map remains much cheaper to mutate. The skip list is justified when
bounded/live ordered reads are frequent enough to pay back that maintenance.
See `docs/optimization-b1.md` and the raw files under `verification/`.

## Retrieval complexity

Let:

- `N` = memories in the bounded set,
- `S` = ordered records scanned before the request stops,
- `K` = lexical matches returned,
- `Bscan` = total text bytes inspected by the lexical predicate,
- `E` = authored internal reference edges.

Then the intended retrieval shape is:

| operation | cost |
|---|---:|
| exact Memory lookup in Go map | expected O(1) |
| skip-list search/insert/delete/rank update | O(log N) |
| first ranked element | O(1) |
| ordered scan of `S` records | O(S) structural steps |
| binary lexical filtering | proportional to text inspected (`Bscan`) |
| bounded result accumulation | O(K) output space |
| continuation state | O(1) |
| indegree/outdegree precompute | O(N + E) |
| global HITS, `I` iterations | O(I(N + E)) |
| PageRank, `I` iterations | O(I(N + E)) after dangling-mass aggregation |
| build ranked skip-list index from scores | O(N log N) |

Agentic crawling is intentionally not assigned a fake asymptotic “answer cost.”
Its cost is measured directly as summaries/tokens, bodies recalled, edges
considered/traversed, backtracks, attempts, and time until the objective task
checker first passes.

## The joint search hypothesis

The experiment has two real knobs:

```text
query-independent Beads pre-order r
              x
agent consumption/crawl policy pi
```

The fixed middle mechanism is mechanical ordered consumption followed by binary
lexical filtering. Benchmark 0 sets the pagination bound to `K = infinity`, so
all lexical matches are returned in one ordered result set. This does **not**
remove the pre-order variable: pagination only partitions the same ordered
stream of lexical matches into chunks. For a fixed corpus, query, matcher, and
pre-order, the relative position of every match is identical for `K = 1`,
`K = 10`, or `K = infinity`. Therefore measurements such as first useful-match
position, summaries inspected before recall, bodies recalled before unblocking,
and reference-crawl trajectory still compare the pre-orders directly.

What `K = infinity` deliberately removes is pagination overhead itself: page
round trips, continuation handling, and policies that change behavior at page
boundaries. Benchmark 0 consequently requires agent policies to operate on the
ordered match stream rather than on page boundaries. Later experiments restore
finite `K` and a scan cursor to measure the additional interaction between
pre-order, page size, continuation cost, and agent policy.

The present hypothesis is **not** “PageRank wins.” It is:

- authority-like priors (indegree/PageRank/global authority centrality) may be
  efficient for shallow/flat readers because direct answer pages arrive early;
- portal-like priors (outdegree/reverse PageRank/global hub centrality) may help
  competent crawlers by giving them useful graph entrances;
- high outdegree can also waste context by increasing branch choice and wrong
  dives;
- therefore token efficiency may depend on the *pair* `(r, pi)` rather than on
  one universally best document ordering.

Every structural prior is computed on the frozen graph before a query exists.
Classic query-focused HITS is **not** used; the experimental `global-hits-*`
controls apply the mutual hub/authority equations to the complete frozen graph.

## Hyperlink-preserving corpus contract

The corpus is not just bodies:

```text
documents + authored directed hyperlinks + source provenance
```

The ingester preserves each authored hyperlink occurrence with anchor text,
source line, raw destination, fragment, syntax, and resolution class. Unique
resolved internal cross-document links become the graph used for centrality and
agent crawling. External/unresolved/local-fragment links remain auditable but do
not silently become centrality edges.

Rendered site/sidebar navigation is never treated as an authored citation.
The current expansion target is the authored `docs/` tree from pinned public
Beads commit:

```text
8d86c06bf231cbc0907436a111fb7b75d39ee12d
```

See `beads-usecase/docs/corpus-and-search-protocol-v1.md`.

## Verification

The implementation is checked independently by `verification-suite/`.
Completed deterministic evidence includes:

- every insertion permutation through n=9 (`9! = 362,880` full orders), with
  validation after every insertion;
- every deletion order through n=8 from every distinct full reachable shape:
  201,600 histories / 1,612,800 validated deletion steps;
- exhaustive mixed-operation graphs, including a 12-key run with 14,280
  canonical states and 342,720 transitions;
- graded reachable-state graph through n=26, with exact deletion image back to
  level n-1;
- deliberate corruption tests for backlink, tower, type-grammar, reachability,
  allocator, and ordering failures;
- all local deletion/closure branches exercised;
- `go vet` PASS.

The reachable-state census agrees with the complete ordered 2–3-tree sequence
A014535 after the expected one-leaf shift. See `docs/theory-verification.md`.

## Optimization evidence

B1 changed representation, not the verified 1–2 rewrite semantics:

- per-level maps -> contiguous tower slices;
- node map -> index-addressed arena;
- sentinel nodes stored directly;
- reverse index map -> arena-aligned slice;
- the key-to-index Go map remains the only required hash table in the skip list.

At N=1,000 this reduced build allocation from about 526 KB / 4,935 allocations
to 288 KB / 1,910 allocations. At N=10,000, insert, rank update, and top-10
improved by roughly 3.9x, 4.2x, and 2.5x respectively while the same external
verification suite continued to pass.

## Repository layout

```text
implementation/       deterministic 1-2 skip-list implementation
verification-suite/   independent deterministic/fuzz/benchmark tests
verification/         selected raw verification and performance evidence
docs/                 invariant, theory, optimization, release notes
beads-usecase/         Memory model, hyperlink corpus, structural rankers,
                      binary discovery, crawl benchmark, exact trajectories
lean-transfer/         optional formal-proof transfer plan
```

## Run

```sh
cd implementation && go test ./... && go vet ./...
cd ../verification-suite && go test ./... && go vet ./...
cd ../beads-usecase && go test ./... && go vet ./...
```

For the expensive graded graph:

```sh
cd verification-suite
go test -run TestGradedTransitionGraph -count=1
```

## Release boundary

RC1 makes two different claims:

- **Skip-list claim:** deterministic implementation + strong finite executable
  verification + measured compact-representation optimization.
- **Memory-search claim:** reproducible hypothesis/benchmark code for studying
  the co-dependence of a cheap query-independent Beads ordering and an agent's
  crawl policy under token/context cost. Large-corpus results are still needed
  before recommending a production prior.
