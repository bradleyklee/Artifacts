# Baseline compiled runs

Hardware/runtime: the supplied Linux x86_64 runner. These are only local
baseline measurements, not portable performance guarantees.

| mode | maximum order | whole-run time | peak RSS | final-term time | final candidate union | final accepted |
|---|---:|---:|---:|---:|---:|---:|
| depth 1 | 50 | 0.69 s | 6.7 MiB | 0.0789 s | 243 | 12 |
| depth 2 | 50 | 5.01 s | 11.1 MiB | 0.5761 s | 2,506 | 12 |

The two modes have identical accepted counts through order 50 in this run.
That is experimental evidence only.  OEIS A147680 is checked only through its
published prefix at order 21.
