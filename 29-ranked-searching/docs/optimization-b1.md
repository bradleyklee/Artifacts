# B1 compact Go representation

Branch: `opt/compact-go-b1`

Goal: make the verified deterministic 1-2 skip list look and behave more like
an idiomatic low-level Go container without changing the local rewrite algorithm.

## Accepted representation changes

1. Per-node `map[level]*link` towers became contiguous `[]link` towers.
2. User nodes moved from `map[index]*node` to an index-addressed arena.
3. The stop/start sentinels are stored directly rather than as map entries.
4. The reverse internal-index-to-key table became an arena-aligned slice.
5. The only hash table required by the data structure is now the public
   key-to-index lookup map.

The five horizontal type tags, insertion cases, deletion cases, type-2 closure
priority, missing-index reuse order, and public ordering semantics are unchanged.

Deletion performs the same horizontal rewrite but delays truncating the removed
level until promoted levels have been moved or recursively deleted. This is a
representation-ordering change required to keep tower slices contiguous.

## Verification gate

B1 passed the external first-class verification suite, including:

- all insertion permutations through n=9;
- all deletion permutations through n=8 from every distinct full shape;
- exhaustive fixed-universe mixed insert/delete graphs;
- exhaustive mixed key/value graph;
- deliberate validator corruptions;
- graded transition graph through n=26 with the same full state census and
  complete deletion image at every level;
- all deletion/closure branches;
- `go vet`.

The full B1 verification suite completes in about 22 seconds in the current
container. The n=26 graded graph completes in about 13 seconds.

## Performance result

Representative local Go 1.23.2 measurements:

| workload | B0 | B1 | change |
|---|---:|---:|---:|
| build N=1000 bytes/op | ~526 KB | ~288 KB | -45% |
| build N=1000 allocs/op | ~4,935 | ~1,910 | -61% |
| insert N=10000 | ~2.00 us | ~0.51 us | ~3.9x faster |
| rank update N=10000 | ~3.54 us | ~0.84 us | ~4.2x faster |
| top-10 N=10000 | ~12.4 us | ~5.0 us | ~2.5x faster |

A maintained rank index still costs substantially more to mutate than a plain
Go map. Its benefit is bounded/live ordered retrieval, not exact lookup or a
one-shot full dump.

Raw data:

- `verification/workload-performance-baseline.txt`
- `verification/workload-performance-b1-arena.txt`
- `verification/benchmark-b1-arena-go1.23.2.txt`
- `verification/graded-graph-b1-n26.txt`
- `verification/external-full-test-b1.txt`
