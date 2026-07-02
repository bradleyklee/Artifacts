# Guest-Visible Sandbox Runtime Snapshot

This report is intentionally limited to non-secret, guest-visible runtime
metadata. It excludes environment variables, network configuration, hostnames,
arbitrary process lists, and file contents. It cannot see host-side gVisor
telemetry or internal service logs.

- Captured UTC: `2026-07-02T17:46:25+00:00`
- Kernel: `Linux <guest-node-redacted> 4.4.0 #1 SMP Sun Jan 10 15:06:54 PST 2016 x86_64 GNU/Linux`
- Python platform: `Linux-4.4.0-x86_64-with-glibc2.41`
- PID 1: `    1 supervisord     /usr/bin/python3 /usr/bin/supervisord -n -c /etc/supervisord.conf`
- Guest-visible mount filesystem types: `9p, cgroup, devpts, overlay, proc, sysfs, tmpfs`
- Guest-visible cgroup controllers: `pids, memory, job, devices, cpuset, cpuacct, cpu`

## Service-manager and journal visibility

- `systemctl --version`: `systemd 257 (257.9-1~deb13u1)`
- `systemctl is-system-running`: `offline`
- `systemctl list-units`: `System has not been booted with systemd as init system (PID 1). Can't operate.`
- `journalctl -b`: `No journal files were found.`

Interpretation: systemd tooling may be installed, but the guest is not booted
with systemd as PID 1. No guest-visible journal is available from this surface.

## Kernel-message visibility

- `dmesg -T` exit: `0`
- gVisor marker present: `yes`
- Rust/SIGBUS-related guest-kernel entries: `no`

Guest-visible boot log:

```text
[Thu Jul  2 17:20:04 2026] Starting gVisor...
[Thu Jul  2 17:20:05 2026] Forking spaghetti code...
[Thu Jul  2 17:20:05 2026] Creating process schedule...
[Thu Jul  2 17:20:05 2026] Moving files to filing cabinet...
[Thu Jul  2 17:20:05 2026] Granting licence to kill(2)...
[Thu Jul  2 17:20:06 2026] Gathering forks...
[Thu Jul  2 17:20:06 2026] Mounting deweydecimalfs...
[Thu Jul  2 17:20:06 2026] Creating bureaucratic processes...
[Thu Jul  2 17:20:06 2026] Recruiting cron-ies...
[Thu Jul  2 17:20:06 2026] Reticulating splines...
[Thu Jul  2 17:20:07 2026] Feeding the init monster...
[Thu Jul  2 17:20:07 2026] Setting up VFS...
[Thu Jul  2 17:20:07 2026] Setting up FUSE...
[Thu Jul  2 17:20:08 2026] Ready!
```

Interpretation: this guest-visible log confirms the gVisor-branded boot path,
but it contains no Rust or SIGBUS crash record. Absence here is not evidence
that no host-side diagnostic exists; a gVisor runtime or host-level crash
record is outside this guest's visibility.

## Process isolation indicators

- `Seccomp`: `0`
- `CapEff`: `00000000a00405fb`
- `Threads`: `72`

## Resource limits

- `open files: soft=1048576, hard=1048576`
- `processes: soft=infinity, hard=infinity`
- `core size: soft=infinity, hard=infinity`

## Tool visibility at capture time

| Tool | PATH status |
| --- | --- |
| `python3` | present |
| `go` | present |
| `gcc` | present |
| `g++` | present |
| `clang` | present |
| `java` | present |
| `swift` | present |
| `rustc` | absent |
| `cargo` | absent |
| `rustup` | absent |

## Debugging consequence

The guest can establish the observed boundary—compiler presence, startup,
exit status, and guest-visible logs—but cannot inspect gVisor host telemetry.
To investigate a historical `rustc` `SIGBUS`, the runtime owner would need
the incident timestamp, sandbox/job identifier, the exact Rust distribution
digest, and host-side gVisor or crash telemetry.

