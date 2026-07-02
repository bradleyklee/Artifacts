# Transferred Rust Local-Success Evidence

## What this evidence is

`rust-hard-disk-parity-poc.zip` was transferred from a different ChatGPT
context that reported a working local Rust toolchain. Its source and captured
outputs are unpacked in `rust-hard-disk-parity-poc/`.

The packet documents a dependency-free, exact-rational hard-disk billiard
control: two equal disks constrained to the invariant centerline of a
rectangle. It is deliberately small, deterministic, and independently
implemented in Go and Rust.

## Reported successful execution in the originating context

The transfer receipt reports this sequence:

```text
go run hard_disk.go > go.out
/mnt/data/toolchains/bin/rust-env rustc -O hard_disk.rs -o hard_disk_rust
./hard_disk_rust > rust.out
diff -u go.out rust.out
```

The recorded result is byte-identical Go/Rust output through 100,000 events,
including a transcript digest:

```text
SUMMARY events=100000 time=239999/2 ax=1/2 av=1 bx=7 bv=-2
fnv64=e1e99892d632909f
```

This establishes a **reported successful local test case** for the offline Rust
1.96.0 toolchain in its originating context. It is stronger than a version
query: the compiler produced and ran a dependency-free Rust binary carrying a
long exact event calculation, and the stored output agrees byte-for-byte with
an independent Go implementation.

## What has been independently checked in this artifact

This artifact cannot see the originating context's mount or execute its
session-local compiler. It does independently check that:

- the transferred archive SHA-256 is recorded below;
- the extracted source and output files match the packet's `SHA256SUMS`; and
- the stored `go.out` and `rust.out` are byte-identical.

Run from the artifact root:

```bash
make verify-transfer
```

These checks validate the **integrity and internal parity evidence** of the
transfer packet. They do not replay the Rust compilation in this context.

## Reconciliation with the earlier failure

This artifact now retains three distinct, context-scoped observations:

1. In the original investigated sandbox, no Rust toolchain was on `PATH`.
2. In that same investigation, an uploaded Rust 1.96 GNU distribution reached
   compiler startup but `rustc --version` terminated with `SIGBUS` / exit 135.
3. In a different context, the managed offline Rust toolchain at
   `/mnt/data/toolchains/bin/rust-env` reportedly compiled and ran this parity
   control successfully.

These are not evidence that Rust is universally impossible. They are evidence
that Rust availability is **context- and provisioning-dependent**. The
investigated context cannot inspect the other context's `/mnt/data` mount.

## Practical provisioning problem

The parity packet itself is tiny (source plus receipts). The usable compiler is
not. The working compiler environment was reported to require a large Rust
payload—at least roughly 100 MiB—to seed a fresh context, and it is not
currently retained as a visible shared capability across context mounts.

That makes repeated ad hoc provisioning impractical for iterative scientific
work. A developer should be able to rely on a documented, cached, or
platform-provided Rust toolchain rather than repeatedly transporting a large
compiler distribution just to discover whether it will start.

## Platform question raised by this evidence

The successful local test makes the request more specific: if an approved or
managed Rust toolchain can compile and run an exact workload in one context,
what determines whether another code-execution context has no native Rust path
or crashes when given a self-contained GNU Rust distribution? The relevant
answer is a capability/provisioning contract, not generic Rust coding advice.
