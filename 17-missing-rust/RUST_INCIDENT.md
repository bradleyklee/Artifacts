# Rust Compiler Startup Incident

## Historical observed result

In the earlier code-execution investigation, no native Rust toolchain was
present in `PATH`. A complete uploaded Rust 1.96.0 GNU x86_64 toolchain was
then tested separately.

- The archive extracted cleanly.
- `cargo 1.96.0` launched normally.
- `rustc --version` reproducibly terminated with `SIGBUS` / shell exit 135.
- Dynamic loading reached glibc, LLVM, and `librustc_driver`; the failure
  occurred immediately afterward during Rust compiler startup.
- Moving the toolchain to local disk and forcing eager binding did not alter
  the result.
- The environment was identified as a gVisor sandbox on a 4.4-era kernel layer.

## Interpretation

This is evidence of a runtime-compatibility failure for that uploaded Rust
compiler in that environment. It rules out several simple explanations,
including incomplete extraction, wrong target architecture, and a plain
missing-library failure.

It does not establish a universal claim about every Rust release, every
ChatGPT execution surface, or every sandbox configuration. The current session
probe is recorded separately in `rust/FAILED_HELLO_WORLD.md`; it does not
re-upload or retry a large compiler bundle.

## Original evidence paths

The original investigator reported these paths, which are environment-local and
not included in this repository:

```text
/mnt/data/rust-1.96.0-x86_64-unknown-linux-gnu.tar.gz
/tmp/rust-dist/
```

## Later contrasting local-success evidence

A different context subsequently transferred a source-and-receipt packet showing
a managed offline Rust toolchain compiling and running a 100,000-event
exact-rational hard-disk control. The stored Rust output is byte-identical to an
independent Go implementation. That compiler mount is not visible from this
context, so the artifact verifies the packet's hashes and stored output parity
but does not claim to replay it here.

See `evidence/RUST_LOCAL_SUCCESS.md` and
`evidence/rust-hard-disk-parity-poc/`. This changes the interpretation from a
possible universal-runtime suspicion to a narrower, evidence-supported finding:
Rust toolchain availability varies by context/provisioning path.
