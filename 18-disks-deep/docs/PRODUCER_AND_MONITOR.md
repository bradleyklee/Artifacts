# Artifact 18 producer and monitor

The retained Go producer is `cmd/burner`, backed by `internal/engine` exact
arithmetic and `internal/burner` collision selection. The Python lane wrapper
runs it in serial 1,000-event divisions, seals each result, and immediately
compacts it to the delivered V3 archive layout.

`tools/launch_v2_50k.py` starts d12, 24A, and 24B writers plus the read-only
80-column dashboard/reporter. A run is always directed to a workspace. The
root corpus is therefore fixed evidence, while reruns are reproducible work.

Useful commands:

```bash
make test                # one division per lane
make test TEST_EVENTS=2000  # two divisions per lane
make burn-50k RUN_DIR=reruns/20260703-full
```

The monitor accepts Ctrl-C: it asks writers to finish their current division,
then stops. The reporter derives graphs only from sealed blocks.
