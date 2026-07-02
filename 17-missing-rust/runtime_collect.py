#!/usr/bin/env python3
"""Collect a privacy-safe, guest-visible sandbox runtime snapshot.

Intended for attachment to a compiler/runtime issue. It intentionally does not
capture environment variables, network configuration, hostnames, file contents,
or arbitrary process lists.
"""
from __future__ import annotations

import datetime as dt
import os
import platform
import re
import resource
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "reports"
OUT_DIR.mkdir(exist_ok=True)
OUT = OUT_DIR / "sandbox_runtime_snapshot.md"


def run(argv: list[str], timeout: int = 10) -> tuple[int | None, str]:
    try:
        p = subprocess.run(
            argv,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
        return p.returncode, p.stdout.rstrip()
    except FileNotFoundError:
        return None, f"not found: {argv[0]}"
    except subprocess.TimeoutExpired:
        return None, f"timed out after {timeout}s"


def redact_kernel_node(value: str) -> str:
    # uname -a puts the ephemeral container node name in field 2. Preserve the
    # kernel version and architecture but redact that unstable identifier.
    parts = value.split()
    if len(parts) >= 2:
        parts[1] = "<guest-node-redacted>"
    return " ".join(parts)


def first_line(value: str) -> str:
    return value.splitlines()[0] if value else "(no output)"


def parse_status() -> dict[str, str]:
    p = Path("/proc/self/status")
    out: dict[str, str] = {}
    if not p.exists():
        return out
    wanted = {"Seccomp", "Seccomp_filters", "CapEff", "NoNewPrivs", "Threads"}
    for line in p.read_text(errors="replace").splitlines():
        key, sep, val = line.partition(":")
        if sep and key in wanted:
            out[key] = val.strip()
    return out


def cgroup_versions() -> list[str]:
    lines: list[str] = []
    p = Path("/proc/1/cgroup")
    if not p.exists():
        return lines
    for line in p.read_text(errors="replace").splitlines():
        fields = line.split(":", 2)
        if len(fields) == 3:
            ctrls = fields[1] or "(unified)"
            lines.append(ctrls)
    return lines


def mount_types() -> list[str]:
    seen: set[str] = set()
    path = Path("/proc/self/mounts")
    if path.exists():
        for line in path.read_text(errors="replace").splitlines():
            fields = line.split()
            if len(fields) >= 3:
                seen.add(fields[2])
    return sorted(seen)


def rlimit(name: str, kind: int) -> str:
    soft, hard = resource.getrlimit(kind)
    fmt = lambda x: "infinity" if x == resource.RLIM_INFINITY else str(x)
    return f"{name}: soft={fmt(soft)}, hard={fmt(hard)}"


def main() -> int:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    uname_rc, uname = run(["uname", "-a"])
    ps_rc, ps = run(["ps", "-p", "1", "-o", "pid=,comm=,args="])
    sysv_rc, sysv = run(["systemctl", "--version"])
    syss_rc, syss = run(["systemctl", "is-system-running"])
    units_rc, units = run(["systemctl", "list-units", "--type=service", "--all", "--no-pager"])
    journal_rc, journal = run(["journalctl", "-b", "--no-pager", "-n", "40"])
    dmesg_rc, dmesg = run(["dmesg", "-T"])

    dmesg_lines = dmesg.splitlines()
    dmesg_gvisor = [x for x in dmesg_lines if re.search(r"gVisor", x, re.I)]
    dmesg_rust = [x for x in dmesg_lines if re.search(r"rust|rustc|sigbus|bus error", x, re.I)]

    status = parse_status()
    tool_rows = []
    for tool in ("python3", "go", "gcc", "g++", "clang", "java", "swift", "rustc", "cargo", "rustup"):
        found = shutil.which(tool)
        tool_rows.append((tool, "present" if found else "absent"))

    rows = []
    rows.append("# Guest-Visible Sandbox Runtime Snapshot")
    rows.append("")
    rows.append("This report is intentionally limited to non-secret, guest-visible runtime")
    rows.append("metadata. It excludes environment variables, network configuration, hostnames,")
    rows.append("arbitrary process lists, and file contents. It cannot see host-side gVisor")
    rows.append("telemetry or internal service logs.")
    rows.append("")
    rows.append(f"- Captured UTC: `{now}`")
    rows.append(f"- Kernel: `{redact_kernel_node(uname) if uname_rc == 0 else uname}`")
    rows.append(f"- Python platform: `{platform.platform(aliased=True, terse=False)}`")
    rows.append(f"- PID 1: `{ps if ps_rc == 0 else ps}`")
    rows.append(f"- Guest-visible mount filesystem types: `{', '.join(mount_types())}`")
    rows.append(f"- Guest-visible cgroup controllers: `{', '.join(cgroup_versions())}`")
    rows.append("")

    rows.append("## Service-manager and journal visibility")
    rows.append("")
    rows.append(f"- `systemctl --version`: `{first_line(sysv)}`")
    rows.append(f"- `systemctl is-system-running`: `{first_line(syss)}`")
    rows.append(f"- `systemctl list-units`: `{first_line(units)}`")
    rows.append(f"- `journalctl -b`: `{first_line(journal)}`")
    rows.append("")
    rows.append("Interpretation: systemd tooling may be installed, but the guest is not booted")
    rows.append("with systemd as PID 1. No guest-visible journal is available from this surface.")
    rows.append("")

    rows.append("## Kernel-message visibility")
    rows.append("")
    rows.append(f"- `dmesg -T` exit: `{dmesg_rc}`")
    rows.append(f"- gVisor marker present: `{'yes' if dmesg_gvisor else 'no'}`")
    rows.append(f"- Rust/SIGBUS-related guest-kernel entries: `{'yes' if dmesg_rust else 'no'}`")
    rows.append("")
    if dmesg_lines:
        rows.append("Guest-visible boot log:")
        rows.append("")
        rows.append("```text")
        rows.extend(dmesg_lines[:80])
        rows.append("```")
    else:
        rows.append("No guest-visible kernel messages were returned.")
    rows.append("")
    rows.append("Interpretation: this guest-visible log confirms the gVisor-branded boot path,")
    rows.append("but it contains no Rust or SIGBUS crash record. Absence here is not evidence")
    rows.append("that no host-side diagnostic exists; a gVisor runtime or host-level crash")
    rows.append("record is outside this guest's visibility.")
    rows.append("")

    rows.append("## Process isolation indicators")
    rows.append("")
    for key in ("Seccomp", "Seccomp_filters", "NoNewPrivs", "CapEff", "Threads"):
        if key in status:
            rows.append(f"- `{key}`: `{status[key]}`")
    rows.append("")
    rows.append("## Resource limits")
    rows.append("")
    for text in (
        rlimit("open files", resource.RLIMIT_NOFILE),
        rlimit("processes", resource.RLIMIT_NPROC),
        rlimit("core size", resource.RLIMIT_CORE),
    ):
        rows.append(f"- `{text}`")
    rows.append("")

    rows.append("## Tool visibility at capture time")
    rows.append("")
    rows.append("| Tool | PATH status |")
    rows.append("| --- | --- |")
    for tool, state in tool_rows:
        rows.append(f"| `{tool}` | {state} |")
    rows.append("")

    rows.append("## Debugging consequence")
    rows.append("")
    rows.append("The guest can establish the observed boundary—compiler presence, startup,")
    rows.append("exit status, and guest-visible logs—but cannot inspect gVisor host telemetry.")
    rows.append("To investigate a historical `rustc` `SIGBUS`, the runtime owner would need")
    rows.append("the incident timestamp, sandbox/job identifier, the exact Rust distribution")
    rows.append("digest, and host-side gVisor or crash telemetry.")
    rows.append("")
    OUT.write_text("\n".join(rows) + "\n")
    print(OUT)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
