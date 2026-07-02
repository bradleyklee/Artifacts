# Transfer: Rust exact hard-disk parity probe

## Purpose

A small proof that the custom offline Rust toolchain can compile and execute a
long, deterministic, exact scientific calculation with output equal to an
independent Go implementation.

## Result

Both programs produced byte-identical output for 100,000 event updates:

```text
SUMMARY events=100000 time=239999/2 ax=1/2 av=1 bx=7 bv=-2 fnv64=e1e99892d632909f
```

The transcript includes the first 12 exact events and an FNV-1a digest of every
post-event record. `diff -u go.out rust.out` returned success.

## Model

- Two equal hard disks, radius `1/2`.
- Container: `[0,8] x [0,3]`.
- Both centers are constrained to `y=3/2`, an invariant centerline.
- Initial state: `A=(1, 1)`, `B=(6, -2)` in x-position/velocity notation.
- Every wall time and disk contact time is rational and reduced exactly.
- Wall impacts flip the incident x velocity; equal-mass disk impacts exchange
  x velocities.

This deliberately validates a 1D invariant subfamily, not the general 2D
quadratic hard-disk collision solver.

## Build

```sh
go run hard_disk.go > go.out
/mnt/data/toolchains/bin/rust-env rustc -O hard_disk.rs -o hard_disk_rust
./hard_disk_rust > rust.out
diff -u go.out rust.out
```

## What this establishes

1. The installed offline Rust 1.96.0 toolchain compiles and runs locally.
2. Rust can perform a long exact-rational event calculation.
3. Its result matches an independently written Go implementation byte-for-byte.

Do not attach a Rust compiler payload to future transfers. This packet is only
source plus expected evidence; the receiving runtime must already expose the
approved Rust toolchain.
