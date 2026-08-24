# Navigation inversion pilot

Corpus: 18 source-derived Beads documentation pages, 49 unique directed
internal citation edges. This corpus is intentionally too small to establish a
power law; it is only a mechanism check before the 180-page site and repo-wide
censuses.

## Flat binary lexical pagination

Page size: 3. Same case-insensitive substring predicate for every ordering.
Mean pages until every pre-labelled essential lexical match is visible across
9 operational tasks:

| prior | mean pages |
| --- | ---: |
| HITS authority | 1.33 |
| indegree | 1.44 |
| PageRank | 1.44 |
| alphabetical | 1.56 |
| stable ID | 1.78 |
| outdegree | 1.89 |
| reverse PageRank | 1.89 |
| fixed random | 2.00 |
| HITS hub | 2.22 |

On this small fixture, authority-oriented orderings are therefore better for
**flat pagination** than hub-oriented orderings.

## Structural navigability

Across every ordered source/target pair, downstream reachability of an entry
node has these Spearman correlations:

| prior | rho(reachability) |
| --- | ---: |
| PageRank | -0.646 |
| indegree | -0.608 |
| reverse PageRank | +0.618 |
| outdegree | +0.359 |
| HITS hub | +0.342 |

The sign reversal is the candidate discovery: ordinary PageRank behaves like
an authority prior, while reverse-PageRank/hub-like scores behave more like
navigation-entry priors.

## Branching penalty and directional skill

A DFS crawler was given a 3-body-read budget. `p` is the abstract probability
that, at each branch, it explores an outgoing edge on a shortest route to the
hidden target first. Unreachable targets count as failures.

Selected Spearman correlations between starting-node score and success:

| p | PageRank | reverse PR | HITS hub | outdegree |
| ---: | ---: | ---: | ---: | ---: |
| 0.00 | +0.271 | -0.070 | -0.311 | -0.311 |
| 0.01 | +0.006 | +0.290 | +0.070 | +0.150 |
| 0.02 | -0.216 | +0.542 | +0.396 | +0.472 |
| 0.05 | -0.397 | +0.532 | +0.527 | +0.570 |
| 0.10 | -0.452 | +0.587 | +0.531 | +0.572 |
| 0.25 | -0.485 | +0.521 | +0.560 | +0.544 |
| 1.00 | -0.446 | +0.447 | +0.578 | +0.539 |

The exact crossover is not trustworthy at N=18, but the mechanism is clear:
without branch-selection ability, high branching is a liability under a tight
read budget; once the crawler has enough directional ability to exploit links,
hub-oriented entry points become an advantage and ordinary PageRank becomes an
inverse signal for crawlability.

## Interpretation to test at scale

This suggests two different static priors may be appropriate for two different
consumer policies:

- **PageRank / authority:** good when the consumer mainly continues lexical
  pagination and wants the answer document itself to arrive early.
- **Reverse PageRank / hub:** potentially good when the consumer treats a
  lexical hit as a launch point and can intelligently traverse references.

The zero-prior LLM experiment should therefore measure not only pages-to-task
success but also **edge-choice precision**: after recalling a node, how often
does the agent choose an outgoing reference that lies on a productive path?
That empirical skill parameter determines whether outlinks are navigation power
or branching noise.
