# Reports Index

Generated: 2026-07-02T17:46:52.524248+00:00

This directory contains executed receipts produced in this sandbox.

| File | What it is |
| --- | --- |
| `latest_probe.md` | Latest full language-capability probe, including captured program output. |
| `latest_resource_watch.csv` | Raw 20 ms samples for the latest Go control watch. |
| `latest_resource_watch.md` | Latest non-interactive top-style watch for the Go compile/run control. |
| `observed_baseline.md` | Scope note separating current observations from the earlier Rust SIGBUS incident. |
| `probe-20260702T174645Z.md` | Timestamped retained run receipt. |
| `probe-run-console.txt` | Console receipt from the current full probe invocation. |
| `resource-watch-go-console.txt` | Console receipt from the current Go resource watch invocation. |
| `resource-watch-go-control-20260702T174648Z.csv` | Timestamped retained run receipt. |
| `resource-watch-go-control-20260702T174648Z.md` | Timestamped retained run receipt. |
| `sandbox_runtime_snapshot.md` | Guest-visible runtime, service-manager, journal, dmesg, and tool discovery snapshot. |
| `rust_session_local_parity_transfer.md` | Integrity receipt for the successful Rust control transferred from another context. |

## Scope boundary

There is no fresh raw Rust SIGBUS trace in this directory because the failing 1.96.0 bundle was not re-uploaded and rerun. The only Rust result in the current probe is PATH absence; the prior SIGBUS is explicitly labeled historical in `RUST_INCIDENT.md` and `rust/FAILED_HELLO_WORLD.md`.

A separate transferred packet records a successful Rust execution in another
context; see `rust_session_local_parity_transfer.md` and
`../evidence/RUST_LOCAL_SUCCESS.md`.
