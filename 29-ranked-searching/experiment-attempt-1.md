# Memory Retrieval Experiment: Attempt 1

## Summary

This note records the first end-to-end experiment on query-independent memory
ordering and agent-side search policy over the Beads documentation corpus. The
experiment is exploratory rather than a fully rigorous statistical study. Its
purpose is to identify promising retrieval strategies and to establish a
reproducible baseline for a later replication.

The main result is that **agent search policy matters more than the structural
sort order** on this corpus. Among the tested policies, a bounded guided search
with escalation achieved the lowest practical context cost while retaining full
task coverage. Structural ordering produced smaller effects, generally on the
order of a few percent relative to a random-order baseline.

When results are averaged over five agent policies that achieved full success
for every random seed, **reverse PageRank was the best structural ordering**, at
about **5.86% lower mean context cost than random ordering**. Stable ID ordering
was close behind at **4.99%**, and global HITS authority saved **3.77%**.
Ordinary PageRank was about **9.23% worse than random** in the same comparison.

These ordering effects are not yet statistically separated from ordinary random
permutation variance. The strongest conclusion from Attempt 1 is therefore not
that a particular graph ranking has been proven best, but that retrieval should
be optimized as a joint system:

```text
sort order + agent search policy -> context cost to objective unblocking
```

## Corpus

The primary corpus is the human-authored published documentation from
`gastownhall/beads` at immutable commit:

```text
8d86c06bf231cbc0907436a111fb7b75d39ee12d
```

The exact parsed corpus contains:

- 71 human-authored documents;
- 244 unique authored internal edges;
- 544 raw hyperlink occurrences;
- 302 resolved internal hyperlink occurrences;
- 52 unresolved internal links retained for audit; and
- 156 external links retained for audit.

Generated CLI documentation was kept separate because generator structure can
introduce degree and centrality patterns that are not authored navigation
choices. A 180-document corpus including generated CLI pages was used only as a
secondary robustness check.

The exact graph confirmed that authority-like and portal-like documents are
structurally distinct. For example, the Dolt backend page has high incoming
support and is the top global HITS authority, while the FAQ has the largest
out-degree and is the top global HITS hub. This distinction survived replacement
of the earlier approximate link projection by the exact authored graph.

## Benchmark

The final Attempt 1 workload contains 10 admitted tasks. Admission requires that
both the lexical seed and every required evidence checkpoint are actually
supported by the frozen corpus. This check was added after an earlier draft of
the benchmark accidentally included three unsupported checkpoint strings.

The primary cost measure is **context bytes consumed until objective task
unblocking**. The cost proxy includes delivered summaries, recalled document
bodies, and inspected reference metadata. Success is determined by the task
checker rather than model confidence.

The experiment varies two independent choices:

1. a query-independent document sort order; and
2. an agent-side search policy.

Sort orders tested include stable ID, alphabetical, indegree, outdegree,
PageRank, reverse PageRank, global HITS authority, global HITS hub, and random
permutations.

The policy family includes flat reading, bounded guided search, guided
escalation, and depth-first and breadth-first graph search variants. Because
there are infinitely many possible agent policies, these policies should be
understood as a representative finite ensemble rather than an exhaustive set.

## Random baseline

A single fixed random ordering is too noisy to serve as the baseline. Attempt 1
therefore uses **64 deterministic random sort orders**.

For each agent policy, a structural sort is compared with the mean performance
of those same 64 random orders under the same policy. This isolates the effect
of ordering from the effect of agent behavior.

Five policies achieved 10/10 task success for all 64 random seeds:

- BFS;
- DFS;
- guided BFS;
- guided DFS; and
- guided escalation.

Averaged over these five policies, the random-order mean was:

```text
188,318 context bytes
```

This five-policy subset provides the cleanest full-coverage comparison between
sort orders.

## Structural sort results

| Sort order | Mean context | Savings vs random |
|---|---:|---:|
| reverse PageRank | 177,282 B | +5.86% |
| stable ID | 178,930 B | +4.99% |
| global HITS authority | 181,217 B | +3.77% |
| indegree | 192,909 B | -2.44% |
| global HITS hub | 200,008 B | -6.21% |
| alphabetical | 200,933 B | -6.70% |
| outdegree | 201,497 B | -7.00% |
| PageRank | 205,691 B | -9.23% |

Here positive savings mean less context than the mean random ordering.

Reverse PageRank is therefore the best structural sort in this particular
full-coverage policy average. The effect is modest: approximately 5.9% relative
to random ordering.

The result should not yet be interpreted as a statistically established ranking
advantage. Reverse PageRank lies around the 37.5th percentile of the 64 random
sorts in the corresponding aggregate comparison, meaning that a substantial
fraction of arbitrary random permutations happened to perform at least as well.
One historically fixed random seed was also unusually favorable and beat all of
the structural sort averages.

This random variability is an important part of the result rather than a reason
to discard the experiment. It establishes the scale that a structural ranking
must beat in a larger replication.

## Agent policy result

The agent policy effect is substantially larger than the sort-order effect.
Using random ordering as the common reference, mean full-coverage costs were
approximately:

| Agent policy | Random-order mean context |
|---|---:|
| guided escalation | 115,123 B |
| guided DFS | 197,367 B |
| DFS | 206,884 B |
| BFS | 210,302 B |
| guided BFS | 211,917 B |

Guided escalation begins with a bounded selective crawl and widens the search
only if the task remains blocked. This policy preserves cheap cases while still
recovering a deliberately constructed zero-lexical-overlap task that shallow
search cannot solve.

The strongest practical pair observed in the current deterministic matrix was:

```text
stable ID + guided escalation
```

with mean context cost:

```text
106,467 bytes
```

This is about **7.5% below the random-order mean using the same guided-escalation
policy**. However, stable ID is still well within the distribution of random
permutations, so this should be treated as a candidate configuration rather than
a demonstrated universal winner.

Global HITS authority plus guided escalation cost about 120,334 bytes and was
therefore about 4.5% worse than the random guided-escalation mean. This is an
example of why sort order and agent policy must be evaluated jointly rather than
assuming that a structurally attractive ranking will help every search policy.

## What Attempt 1 supports

Attempt 1 supports the following practical conclusions.

1. **Search policy is the dominant effect observed so far.** A selective search
   with escalation can reduce context substantially compared with immediate
   DFS/BFS-style crawling.
2. **Structural ordering has a smaller but potentially useful effect.** On a
   corpus of only 71 documents, several-percent savings may still matter, but
   these gains need replication.
3. **Reverse PageRank is the best structural sort in the clean five-policy
   average**, saving about 5.86% relative to mean random ordering.
4. **Ordinary PageRank is not supported by this attempt.** It performs about
   9.23% worse than random in the same comparison.
5. **No structural sort has yet separated convincingly from the random-order
   distribution.** The present task set is too small to establish a general
   ranking theorem or universal winner.
6. **The appropriate object of optimization is the pair of sort order and agent
   search policy**, not either component in isolation.

## Working hypothesis for replication

The next attempt should test the following practical hypothesis without further
retuning on this corpus:

> A bounded guided search with escalation will remain the best policy family in
> practice, while structural pre-ordering will provide a smaller secondary
> improvement over the mean random-order baseline. Reverse PageRank, stable ID,
> and global HITS authority are the leading sort candidates from Attempt 1.

The replication should preserve a random-order ensemble rather than a single
random seed and should evaluate the same fixed ordering-policy combinations on
more tasks, another corpus, or both. The important quantity is the percentage
change in context cost relative to the policy-matched random mean while
maintaining objective task success.

## Scope of the claim

This is an exploratory systems result. It is not a proof that reverse PageRank,
stable ID, or guided escalation is universally optimal. The corpus is small,
the task set contains only 10 admitted tasks, and the agent-policy ensemble is
representative rather than exhaustive.

The artifact is intended to preserve the result of Attempt 1 clearly enough to
support replication without requiring readers to inspect the full experimental
codebase.
