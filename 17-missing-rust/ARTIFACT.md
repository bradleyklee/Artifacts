# Artifact Manifest

- **Identifier:** 17-missing-rust
- **Claim type:** bounded runtime-capability observation
- **Canonical overview:** `README.md`
- **Short blurb:** `17-missing-rust.md`
- **Executable probe:** `run_probe.py`
- **Current raw result:** `reports/latest_probe.md`
- **Rust current-run diagnostic:** `rust/FAILED_HELLO_WORLD.md`
- **Rust historical incident:** `RUST_INCIDENT.md`
- **Transferred local-success evidence:** `evidence/RUST_LOCAL_SUCCESS.md`
- **Transferred parity packet:** `evidence/rust-hard-disk-parity-poc/`
- **Toolchain-persistence analysis:** `TOOLCHAIN_PERSISTENCE.md`
- **Transfer integrity command:** `make verify-transfer`
- **Guest-visible runtime snapshot:** `reports/sandbox_runtime_snapshot.md`
- **Runtime snapshot collector:** `runtime_collect.py`
- **Resource-watch collector:** `runtime_watch.py`
- **Normal compiler control:** `reports/latest_resource_watch.md` and `.csv`
- **Verification command:** `python3 run_probe.py`

The runner overwrites the current Rust diagnostic and creates a timestamped
report for the runtime in which it is executed. Do not generalize a result to a
different product surface without rerunning the probe there.

## Status after the transferred local-success control

The original sandbox observation remains: no Rust is exposed on `PATH`, and an
uploaded GNU Rust 1.96 compiler crashed at startup in that context. The
transferred parity packet adds a separate successful local-toolchain result from
another context. Treat this artifact as evidence of context-dependent toolchain
provisioning, not as a universal Rust impossibility claim.
