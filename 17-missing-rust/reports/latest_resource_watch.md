# Resource Watch — go-control

A non-interactive, reproducible equivalent of watching `top` during one
known command. It records guest-visible aggregate memory/load/cgroup state
and only the launched command's process tree. It excludes environment
variables, network configuration, hostnames, command arguments, and
unrelated process listings.

- Started UTC: `2026-07-02T17:46:48+00:00`
- Command: `go run samples/pi.go`
- Result: `exit 0`
- Timed out: `no`
- Elapsed: `0.481451 s`
- Samples: `12` at requested `0.020 s` interval
- Full time series: `reports/latest_resource_watch.csv`

## Summary ranges

- Command-tree RSS: `0.0 B`
  to `150.7 MiB`
- Current cgroup memory: `n/a`
  to `n/a`
- Guest MemAvailable: `3.1 GiB`
  to `3.2 GiB`
- Load average (1m): `0.0` to `0.0`
- Memory PSI some/avg10: `n/a` to `n/a`
- Peak observed command-tree processes: `5`
- Peak observed command-tree threads: `38`

## Captured command output

```text
hello 3.1415 world!
```

## Interpretation

A short-lived failure can disappear between samples; absence of a resource
spike does not explain a crash. Use this as a controlled comparison between
a normal compiler run and a candidate compiler run at the same sampling
interval. A host-side gVisor diagnostic remains outside guest visibility.
