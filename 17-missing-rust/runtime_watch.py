#!/usr/bin/env python3
"""Sample guest-visible resource state while one known command runs.

This is a bounded, privacy-safe alternative to interactive ``top`` for a
reproducible sandbox artifact. It records only global memory/load summaries,
current-cgroup counters, and the launched process tree's aggregate resource
state. It never records environment variables, network settings, hostnames,
or unrelated process listings.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return None


def read_kv(path: Path) -> dict[str, str]:
    text = read_text(path)
    if not text:
        return {}
    out: dict[str, str] = {}
    for line in text.splitlines():
        key, sep, value = line.partition(":")
        if sep:
            out[key.strip()] = value.strip()
    return out


def parse_kib(value: str | None) -> int | None:
    if not value:
        return None
    fields = value.split()
    if not fields:
        return None
    try:
        return int(fields[0])
    except ValueError:
        return None


def parse_int(value: str | None) -> int | None:
    if value is None or value == "max":
        return None
    try:
        return int(value.strip())
    except ValueError:
        return None


def human_bytes(value: int | None) -> str:
    if value is None:
        return "n/a"
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    amount = float(value)
    for unit in units:
        if amount < 1024.0 or unit == units[-1]:
            return f"{amount:.1f} {unit}"
        amount /= 1024.0
    return "n/a"


def proc_ppid(pid: int) -> int | None:
    text = read_text(Path("/proc") / str(pid) / "stat")
    if not text:
        return None
    # The process name can contain spaces and parentheses. The PPID is the
    # first field following the final closing parenthesis and the state.
    end = text.rfind(")")
    fields = text[end + 2 :].split()
    if len(fields) < 2:
        return None
    try:
        return int(fields[1])
    except ValueError:
        return None


def proc_comm(pid: int) -> str:
    return (read_text(Path("/proc") / str(pid) / "comm") or "?").strip()


def descendants(root_pid: int) -> list[int]:
    parent_map: dict[int, int] = {}
    try:
        entries = list(Path("/proc").iterdir())
    except OSError:
        return [root_pid]
    for entry in entries:
        if not entry.name.isdigit():
            continue
        pid = int(entry.name)
        ppid = proc_ppid(pid)
        if ppid is not None:
            parent_map[pid] = ppid
    found = {root_pid}
    changed = True
    while changed:
        changed = False
        for pid, ppid in parent_map.items():
            if ppid in found and pid not in found:
                found.add(pid)
                changed = True
    return sorted(found)


def process_metrics(pids: Iterable[int]) -> dict[str, int | str]:
    rss_kib = 0
    hwm_kib = 0
    threads = 0
    read_bytes = 0
    write_bytes = 0
    labels: list[str] = []
    live = 0
    for pid in pids:
        status = read_kv(Path("/proc") / str(pid) / "status")
        if not status:
            continue
        live += 1
        rss_kib += parse_kib(status.get("VmRSS")) or 0
        hwm_kib += parse_kib(status.get("VmHWM")) or 0
        threads += parse_int(status.get("Threads")) or 0
        io = read_kv(Path("/proc") / str(pid) / "io")
        read_bytes += parse_int(io.get("read_bytes")) or 0
        write_bytes += parse_int(io.get("write_bytes")) or 0
        labels.append(f"{pid}:{proc_comm(pid)}")
    return {
        "tree_processes": live,
        "tree_rss_kib": rss_kib,
        "tree_hwm_kib": hwm_kib,
        "tree_threads": threads,
        "tree_read_bytes": read_bytes,
        "tree_write_bytes": write_bytes,
        "tree_labels": ";".join(labels),
    }


def memory_metrics() -> dict[str, int | None]:
    info = read_kv(Path("/proc/meminfo"))
    keys = ("MemTotal", "MemAvailable", "MemFree", "Buffers", "Cached")
    return {f"mem_{key.lower()}_kib": parse_kib(info.get(key)) for key in keys}


def load_metrics() -> dict[str, float | None]:
    text = read_text(Path("/proc/loadavg"))
    if not text:
        return {"load1": None, "load5": None, "load15": None}
    fields = text.split()
    values: list[float | None] = []
    for field in fields[:3]:
        try:
            values.append(float(field))
        except ValueError:
            values.append(None)
    while len(values) < 3:
        values.append(None)
    return {"load1": values[0], "load5": values[1], "load15": values[2]}


def cgroup_metrics() -> dict[str, int | None]:
    root = Path("/sys/fs/cgroup")
    values: dict[str, int | None] = {}
    for name in ("memory.current", "memory.peak", "memory.max"):
        values[f"cgroup_{name.replace('.', '_')}_bytes"] = parse_int(
            read_text(root / name)
        )
    return values


def psi_metrics() -> dict[str, float | None]:
    text = read_text(Path("/proc/pressure/memory"))
    values = {"psi_some_avg10": None, "psi_full_avg10": None}
    if not text:
        return values
    for line in text.splitlines():
        fields = dict(item.split("=", 1) for item in line.split()[1:] if "=" in item)
        try:
            avg10 = float(fields["avg10"])
        except (KeyError, ValueError):
            continue
        if line.startswith("some "):
            values["psi_some_avg10"] = avg10
        if line.startswith("full "):
            values["psi_full_avg10"] = avg10
    return values


def sample(root_pid: int, elapsed_s: float) -> dict[str, object]:
    row: dict[str, object] = {"elapsed_s": round(elapsed_s, 6)}
    row.update(memory_metrics())
    row.update(load_metrics())
    row.update(cgroup_metrics())
    row.update(psi_metrics())
    row.update(process_metrics(descendants(root_pid)))
    return row


def exit_text(code: int) -> str:
    if code >= 0:
        return f"exit {code}"
    sig = -code
    try:
        return f"signal {signal.Signals(sig).name} ({sig})"
    except ValueError:
        return f"signal {sig}"


def clipped(text: str, limit: int = 4000) -> str:
    text = text.strip()
    if not text:
        return "(no stdout/stderr)"
    return text if len(text) <= limit else text[:limit] + "\n...[clipped]"


def ranges(rows: list[dict[str, object]], key: str) -> tuple[object, object]:
    values = [row[key] for row in rows if row.get(key) is not None]
    if not values:
        return "n/a", "n/a"
    return min(values), max(values)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record resource samples for one command in this sandbox."
    )
    parser.add_argument("--label", default="command", help="safe output label")
    parser.add_argument("--interval", type=float, default=0.02)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.interval <= 0:
        parser.error("--interval must be positive")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if not args.command or args.command[0] != "--" or len(args.command) == 1:
        parser.error("use: runtime_watch.py [options] -- command arg...")

    command = args.command[1:]
    safe_label = "".join(
        char if char.isalnum() or char in "-_" else "-" for char in args.label
    ).strip("-") or "command"
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = f"resource-watch-{safe_label}-{stamp}"
    csv_path = REPORTS / f"{stem}.csv"
    md_path = REPORTS / f"{stem}.md"
    latest_md = REPORTS / "latest_resource_watch.md"
    latest_csv = REPORTS / "latest_resource_watch.csv"

    started_utc = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    started = time.monotonic()
    timed_out = False
    try:
        proc = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
        )
    except FileNotFoundError:
        print(f"not found: {command[0]}", file=sys.stderr)
        return 127

    rows: list[dict[str, object]] = []
    while proc.poll() is None:
        elapsed = time.monotonic() - started
        rows.append(sample(proc.pid, elapsed))
        if elapsed >= args.timeout:
            timed_out = True
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            break
        time.sleep(args.interval)

    output, _ = proc.communicate()
    finished = time.monotonic()
    rows.append(sample(proc.pid, finished - started))
    code = proc.returncode

    fieldnames = sorted({key for row in rows for key in row})
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    rss_min, rss_max = ranges(rows, "tree_rss_kib")
    cg_min, cg_max = ranges(rows, "cgroup_memory_current_bytes")
    avail_min, avail_max = ranges(rows, "mem_memavailable_kib")
    load_min, load_max = ranges(rows, "load1")
    psi_min, psi_max = ranges(rows, "psi_some_avg10")
    peak_tree = max((int(row.get("tree_processes") or 0) for row in rows), default=0)
    peak_threads = max((int(row.get("tree_threads") or 0) for row in rows), default=0)

    lines = [
        f"# Resource Watch — {safe_label}",
        "",
        "A non-interactive, reproducible equivalent of watching `top` during one",
        "known command. It records guest-visible aggregate memory/load/cgroup state",
        "and only the launched command's process tree. It excludes environment",
        "variables, network configuration, hostnames, command arguments, and",
        "unrelated process listings.",
        "",
        f"- Started UTC: `{started_utc.isoformat()}`",
        f"- Command: `{' '.join(command)}`",
        f"- Result: `{exit_text(code)}`",
        f"- Timed out: `{'yes' if timed_out else 'no'}`",
        f"- Elapsed: `{finished - started:.6f} s`",
        f"- Samples: `{len(rows)}` at requested `{args.interval:.3f} s` interval",
        "- Full time series: `reports/latest_resource_watch.csv`",
        "",
        "## Summary ranges", "",
        f"- Command-tree RSS: `{human_bytes(int(rss_min) * 1024) if rss_min != 'n/a' else 'n/a'}`",
        f"  to `{human_bytes(int(rss_max) * 1024) if rss_max != 'n/a' else 'n/a'}`",
        f"- Current cgroup memory: `{human_bytes(int(cg_min)) if cg_min != 'n/a' else 'n/a'}`",
        f"  to `{human_bytes(int(cg_max)) if cg_max != 'n/a' else 'n/a'}`",
        f"- Guest MemAvailable: `{human_bytes(int(avail_min) * 1024) if avail_min != 'n/a' else 'n/a'}`",
        f"  to `{human_bytes(int(avail_max) * 1024) if avail_max != 'n/a' else 'n/a'}`",
        f"- Load average (1m): `{load_min}` to `{load_max}`",
        f"- Memory PSI some/avg10: `{psi_min}` to `{psi_max}`",
        f"- Peak observed command-tree processes: `{peak_tree}`",
        f"- Peak observed command-tree threads: `{peak_threads}`",
        "",
        "## Captured command output", "", "```text", clipped(output), "```", "",
        "## Interpretation", "",
        "A short-lived failure can disappear between samples; absence of a resource",
        "spike does not explain a crash. Use this as a controlled comparison between",
        "a normal compiler run and a candidate compiler run at the same sampling",
        "interval. A host-side gVisor diagnostic remains outside guest visibility.",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    latest_md.write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")
    latest_csv.write_text(csv_path.read_text(encoding="utf-8"), encoding="utf-8")
    print(md_path)
    print(csv_path)
    refresh = subprocess.run(
        ("python3", str(ROOT / "refresh_artifact.py")), cwd=ROOT, check=False
    )
    if refresh.returncode != 0:
        print("warning: could not refresh 17-missing-rust.md", file=sys.stderr)
    return 0 if code == 0 and not timed_out else (124 if timed_out else code)


if __name__ == "__main__":
    raise SystemExit(main())
