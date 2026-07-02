# Sandbox Language Capability Probe

A small, exportable probe for language availability in a constrained
code-execution sandbox. The included suite covers 19 distinct language tracks
that are either interpreted or compiled in the current image. Each sample
performs **exact integer long division**
of the rational pi approximant `355 / 113` and prints its first four fractional
decimal digits. Every successful probe must emit exactly:

```text
hello 3.1415 world!
```

`355 / 113 = 3.141592920...`; it is a familiar rational convergent to pi, and
its first four fractional digits agree with pi. This deliberately avoids
floating-point formatting and library math: every implementation uses the same
small arithmetic kernel—integer quotient, remainder, multiply remainder by
10, emit the next digit, and repeat four times.

The project distinguishes three outcomes:

1. **available** — source compiled or interpreted and produced the
   expected line;
2. **unavailable** — the relevant executable was not found; and
3. **failed** — a tool was found but could not complete the probe.

This is a capability probe, not a benchmark and not a statement of formal
platform support. Re-run it in the target sandbox before relying on any result.

## Artifact 17: Missing Rust

### New: a successful local Rust control in another context

The artifact now includes a transferred, integrity-checked parity packet at
`evidence/rust-hard-disk-parity-poc/`. In its originating context, a managed
offline Rust toolchain reportedly compiled and ran a 100,000-event
exact-rational two-hard-disk control, with byte-identical output to an
independent Go implementation. The local compiler mount is not visible in this
context, so this repository distinguishes packet integrity from independent
replay. Read `evidence/RUST_LOCAL_SUCCESS.md` and run `make verify-transfer`.

This changes the bounded conclusion: Rust is not shown to be universally
impossible in ChatGPT execution contexts. Instead, availability is observed to
be context- and provisioning-dependent. The unresolved product problem is that
the working compiler environment is not a reusable visible capability here;
seeding it into a fresh context has required a large (roughly 100 MiB or more)
toolchain payload. `TOOLCHAIN_PERSISTENCE.md` records that operational boundary.

`17-missing-rust.md` is the short artifact blurb and reading guide. It states
the bounded finding: the observed sandbox runs multiple compiled-language
tracks but exposes no native Rust toolchain, while the separately tested Rust
1.96.0 GNU compiler failed at startup. The detailed evidence remains in
`reports/`, `rust/FAILED_HELLO_WORLD.md`, and `RUST_INCIDENT.md`.

## Runtime evidence

`runtime_collect.py` records a privacy-safe, guest-visible snapshot in
`reports/sandbox_runtime_snapshot.md`. It captures the init process, kernel
version, service-manager/journal visibility, guest-visible dmesg output,
cgroup and mount-type summaries, isolation indicators, resource limits, and
PATH-level tool presence. It intentionally excludes environment variables,
network configuration, hostnames, arbitrary process listings, and file
contents.

The snapshot establishes what the guest can observe; it cannot access gVisor
host telemetry or an internal crash record.

## Resource watch

`runtime_watch.py` is the reproducible equivalent of watching `top` during one
known compiler or runtime command. It samples global memory/load summaries,
current-cgroup memory counters where exposed, and the aggregate resource state
of only the launched command's process tree. It does not record environment
variables, network configuration, hostnames, command arguments, or unrelated
process listings.

A normal Go compile-and-run control is retained in
`reports/latest_resource_watch.md` and `reports/latest_resource_watch.csv`.
Recreate it with:

```bash
python3 runtime_watch.py --label go-control --interval 0.02 -- \
  go run samples/pi.go
```

When a Rust compiler path is available, run the same watcher around both the
version query and the exact smoke compile. Use the same interval for the Go
control and the Rust candidate; a short `SIGBUS` can occur between samples, so
the trace is comparative evidence, not a complete crash explanation.

```bash
python3 runtime_watch.py --label rustc-version --interval 0.02 -- \
  /path/to/rustc --version
python3 runtime_watch.py --label rust-smoke --interval 0.02 -- \
  /path/to/rustc rust/hello_pi_world.rs -O -o build/pi-rust
```

## Quick start

```bash
python3 run_probe.py
```

The runner writes a timestamped Markdown report in `reports/`. It also writes
`rust/FAILED_HELLO_WORLD.md` on every run with verbose Rust-track diagnostics:
tool discovery, executable paths, Rust version attempts where executable,
platform facts, the exact probe source hash, and the recorded result.
Individual language failures are retained in the report so a constrained
environment can be surveyed in one run.

## Rust-specific purpose

`rust/hello_pi_world.rs` is deliberately dependency-free. It lets a
Rust-capable environment prove basic compiler startup and generated-binary
execution without Cargo, crates, a network connection, or a large project
build.

For a compiler discovered through `PATH`, the probe performs both:

```bash
rustc --version
rustc rust/hello_pi_world.rs -O -o build/pi-rust && build/pi-rust
```

## Repository hygiene

The `build/` directory and timestamped reports are ignored by Git. The curated
incident summary, current Rust failure artifact, and observed baseline are
tracked intentionally.

## Export to GitHub

```bash
git init
git add .
git commit -m "Add sandbox language capability probe"
git branch -M main
git remote add origin <YOUR_REPOSITORY_URL>
git push -u origin main
```
