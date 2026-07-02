# Exact hard-disk Go/Rust proof of concept

A tiny, dependency-free parity test. Two equal hard disks of radius `1/2` move
inside `[0,8] × [0,3]` on the invariant centerline `y=3/2`. This is a real
hard-disk billiard subfamily: disk-disk contact and disk-wall reflection are
resolved exactly, using reduced rational arithmetic.

It is intentionally **not** a performance or chaos record. Its purpose is to
prove that the custom offline Rust toolchain can compile and execute a long,
deterministic, scientifically checkable event calculation matching Go.

## Commands

```sh
go run hard_disk.go > go.out
/mnt/data/toolchains/bin/rust-env rustc -O hard_disk.rs -o hard_disk_rust
./hard_disk_rust > rust.out
diff -u go.out rust.out
```

Expected: no diff. Both implementations emit the first 12 certified events and
a 100,000-event FNV-1a transcript digest.

## Scope / limitation

The centerline constraint makes this a 1D invariant slice of planar hard-disk
billiards. It validates toolchain, exact rational state handling, event choice,
wall reflection, equal-mass collision exchange, long-run determinism, and
cross-language certificate equality. It does not validate the general 2D
quadratic collision-time solver.
