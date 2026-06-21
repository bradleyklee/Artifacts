# Baseline compiled runs

Hardware/runtime: the supplied Linux x86_64 runner. These are only local
baseline measurements, not portable performance guarantees.  The current
program anchors its circle pencils at exposed occupied boundary sites.

| mode | maximum order | whole-run time | peak RSS | final-term time | final candidate union | final accepted |
|---|---:|---:|---:|---:|---:|---:|
| depth 1 | 50 | 0.26 s | 7.8 MiB | 0.0221 s | 243 | 12 |
| depth 2 | 50 | 2.05 s | 11.1 MiB | 0.1840 s | 2,506 | 12 |

## Boundary-anchor regression check

Before the boundary restriction, the predecessor code tried every occupied
pair as a possible pencil anchor.  The present code tries only exposed occupied
boundary pairs.  Direct runs through order 50 found identical values for every
discrete CSV column (`accepted_prev`, `accepted_prev2`, candidate counts,
lattice-convex survivors, and accepted disks) in both depth modes.

For a fixed candidate, exposed-boundary anchors are a subset of all occupied
anchors, so the new predicate cannot add a false positive relative to the old
one.  Since the counts agree at every order beginning from the shared seed,
the retained accepted sets agree inductively through order 50.

The two depth modes have identical accepted counts through order 50 in this
run. That is experimental evidence only. OEIS A147680 is checked only through
its published prefix at order 21.
