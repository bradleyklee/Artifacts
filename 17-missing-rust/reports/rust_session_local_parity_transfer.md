# Rust Session-Local Parity Transfer Receipt

**Source packet:** `../evidence/rust-hard-disk-parity-poc.zip`  
**Packet SHA-256:** `63345e2f08f1f0d6c5e73068f473fd5245c68e70c7795243e3668b4baf3c4a2a`

## Packet integrity checked in this artifact

The extracted Go source, Rust source, Go output, and Rust output match the
packet's included `SHA256SUMS`. The stored Go and Rust output files are
byte-identical.

The packet reports that another context used:

```text
/mnt/data/toolchains/bin/rust-env rustc -O hard_disk.rs -o hard_disk_rust
```

and then produced the same 100,000-event exact-rational hard-disk transcript
as Go. The shared final certificate is:

```text
SUMMARY events=100000 time=239999/2 ax=1/2 av=1 bx=7 bv=-2
fnv64=e1e99892d632909f
```

## Scope

This is transfer evidence of a successful **different-context** local Rust
execution. This artifact has not rerun that compiler because its session-local
mount is not visible here. It therefore supports a context-dependent
provisioning conclusion, not a claim that this exact sandbox has a verified
working Rust compiler.

See `../evidence/RUST_LOCAL_SUCCESS.md` for the full distinction and
`../RUST_INCIDENT.md` for the earlier SIGBUS incident.
