# Artifact 17 — Missing Rust

## Blurb

This artifact records a small, reproducible language-capability probe for the
ChatGPT code-execution sandbox. Its workload is deliberately minimal: each
track performs exact integer long division of the rational pi approximant
`355 / 113` and must print:

```text
hello 3.1415 world!
```

The observed baseline demonstrates that the environment can execute both
interpreted languages and multiple compiled-language toolchains. Eighteen
tracks completed the identical workload, including Go, C, C++, Java, Kotlin,
Swift, and Fortran.

Rust was the exception in the original investigated sandbox. No native `rustc`,
`cargo`, or `rustup` was present on `PATH`. A separate test of a complete Rust
1.96.0 GNU x86_64 distribution found that `cargo` launched, while
`rustc --version` reproducibly terminated with `SIGBUS` / shell exit 135 during
compiler startup under the observed gVisor runtime. Moving the distribution to
local storage and forcing eager binding did not change that result.

A later transfer from a different context adds an important successful control:
a managed offline Rust toolchain reportedly compiled and ran a dependency-free
100,000-event exact-rational hard-disk calculation, producing byte-identical
output to an independent Go implementation. The source, captured output, and
hashes are included under `evidence/rust-hard-disk-parity-poc/`; this context
cannot see the originating context's compiler mount, so it validates packet
integrity and stored output parity rather than replaying that build.

The combined finding is therefore **context-dependent Rust provisioning**, not
"Rust can never run." The practical defect is that a successful Rust toolchain
is not exposed as a persistent, documented capability across context mounts.
The toolchain payload needed to seed a fresh context is operationally large
(roughly 100 MiB or more), making repeated ad hoc uploads unsuitable for normal
scientific iteration.

This is a bounded capability record, not a claim about every Rust release,
every OpenAI product surface, or every sandbox. Its purpose is to make the
language asymmetry and the successful counterexample reproducible, retain both
forms of evidence alongside minimal source, and distinguish platform
provisioning from an ordinary project or source-code failure.

## Reading order

1. `README.md` — self-contained reproduction instructions and project scope.
2. `reports/latest_probe.md` — captured multi-language baseline.
3. `rust/FAILED_HELLO_WORLD.md` — verbose current Rust-track diagnosis.
4. `RUST_INCIDENT.md` — scoped historical uploaded-toolchain SIGBUS result.
5. `evidence/RUST_LOCAL_SUCCESS.md` — transferred successful local Rust control
   and the boundary between verified packet integrity and replay.
6. `evidence/rust-hard-disk-parity-poc/` — Go/Rust source, outputs, hashes, and
   transfer receipt; run `make verify-transfer`.
7. `TOOLCHAIN_PERSISTENCE.md` — why large per-context toolchain transport is
   the operational blocker.
8. `reports/sandbox_runtime_snapshot.md` — guest-visible runtime, service, and
   kernel-log boundary.
9. `reports/latest_resource_watch.md` and `.csv` — a normal Go compiler-run
   resource trace, collected like a reproducible `top` view.
10. `runtime_watch.py` — rerunnable per-command resource sampler.
11. `run_probe.py` and `samples/` — executable capability probe.

## Guest-visible runtime context

The included runtime snapshot confirms that this is a supervisor-managed guest,
not a systemd-booted VM: `systemctl` cannot connect to a system scope and no
guest journal is available. The guest-visible `dmesg` buffer confirms a
gVisor-branded boot path but contains no Rust/SIGBUS crash entry. This is an
important boundary: the artifact can show the compiler failure and the
guest-visible environment around it, but host-side gVisor crash telemetry must
be retrieved by the runtime operator.

## Resource-control context

A normal `go run samples/pi.go` control was sampled at 20 ms intervals with
`runtime_watch.py`. The control exited successfully after 0.49 s, reached an
observed command-tree RSS peak of about 100 MiB, and showed no guest-visible
memory-pressure signal. This is a baseline, not a performance benchmark. The
watcher exists so a future Rust candidate can be measured under the same
method, rather than compared only by terminal output.

## Reproduction contract

Run `python3 run_probe.py` in the intended sandbox. Treat the generated
report, rather than this historical snapshot, as the result for that runtime.

<!-- BEGIN GENERATED LATEST RECEIPTS -->
## Latest generated run receipts

This block is updated automatically whenever the capability probe or resource
watch runs. It keeps the most recent printable evidence in this main artifact
file. Timestamped originals and the raw resource CSV remain in `reports/`.

### Latest language capability probe

### Sandbox Language Capability Probe

Generated: 2026-07-02T17:32:14.771522+00:00

Workload: exact integer long division of rational approximant `355 / 113`.
Expected program output: `hello 3.1415 world!`

| Probe | Status | Detail | Process result |
| --- | --- | --- | --- |
| Bash | available | expected output | exit 0 |
| AWK | available | expected output | exit 0 |
| Python | available | expected output | exit 0 |
| Node | available | expected output | exit 0 |
| TypeScript | available | expected output | exit 0 |
| Ruby | available | expected output | exit 0 |
| Perl | available | expected output | exit 0 |
| PHP | available | expected output | exit 0 |
| Tcl | available | expected output | exit 0 |
| Go | available | expected output | exit 0 |
| GCC C | available | expected output | exit 0 |
| G++ C++ | available | expected output | exit 0 |
| Clang C | available | expected output | exit 0 |
| Clang C++ | available | expected output | exit 0 |
| Java | available | expected output | exit 0 |
| Kotlin | available | expected output | exit 0 |
| Swift | available | expected output | exit 0 |
| Fortran | available | expected output | exit 0 |
| Rust | unavailable | not found in PATH: rustc | not started |

#### Rust diagnostic artifact

Verbose Rust-track details: `rust/FAILED_HELLO_WORLD.md`

#### Captured output

##### Bash (available)

```text
hello 3.1415 world!
```

##### AWK (available)

```text
hello 3.1415 world!
```

##### Python (available)

```text
hello 3.1415 world!
```

##### Node (available)

```text
hello 3.1415 world!
```

##### TypeScript (available)

```text
hello 3.1415 world!
```

##### Ruby (available)

```text
hello 3.1415 world!
```

##### Perl (available)

```text
hello 3.1415 world!
```

##### PHP (available)

```text
hello 3.1415 world!
```

##### Tcl (available)

```text
hello 3.1415 world!
```

##### Go (available)

```text
hello 3.1415 world!
```

##### GCC C (available)

```text
hello 3.1415 world!
```

##### G++ C++ (available)

```text
hello 3.1415 world!
```

##### Clang C (available)

```text
hello 3.1415 world!
```

##### Clang C++ (available)

```text
hello 3.1415 world!
```

##### Java (available)

```text
hello 3.1415 world!
```

##### Kotlin (available)

```text
hello 3.1415 world!
```

##### Swift (available)

```text
hello 3.1415 world!
```

##### Fortran (available)

```text
hello 3.1415 world!
```

##### Rust (unavailable)

```text
(no captured output)
```

### Latest resource watch

### Resource Watch — go-control

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

#### Summary ranges

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

#### Captured command output

```text
hello 3.1415 world!
```

#### Interpretation

A short-lived failure can disappear between samples; absence of a resource
spike does not explain a crash. Use this as a controlled comparison between
a normal compiler run and a candidate compiler run at the same sampling
interval. A host-side gVisor diagnostic remains outside guest visibility.

<!-- END GENERATED LATEST RECEIPTS -->
