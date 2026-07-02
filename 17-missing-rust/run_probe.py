#!/usr/bin/env python3
"""Survey language/compiler availability with one exact rational workload."""

from __future__ import annotations

import datetime as dt
import hashlib
import os
import pathlib
import shlex
import shutil
import signal
import subprocess
from dataclasses import dataclass

ROOT = pathlib.Path(__file__).resolve().parent
SAMPLES = ROOT / "samples"
RUST = ROOT / "rust"
BUILD = ROOT / "build"
REPORTS = ROOT / "reports"
EXPECTED = "hello 3.1415 world!"


@dataclass(frozen=True)
class Probe:
    name: str
    required: tuple[str, ...]
    command: tuple[str, ...]


PROBES = (
    Probe("Bash", ("bash",), ("bash", str(SAMPLES / "pi.sh"))),
    Probe("AWK", ("awk",), ("awk", "-f", str(SAMPLES / "pi.awk"))),
    Probe("Python", ("python3",), ("python3", str(SAMPLES / "pi.py"))),
    Probe("Node", ("node",), ("node", str(SAMPLES / "pi.js"))),
    Probe("TypeScript", ("ts-node",), ("ts-node", "--compiler-options", '{"module":"CommonJS"}', str(SAMPLES / "pi.ts"))),
    Probe("Ruby", ("ruby",), ("ruby", str(SAMPLES / "pi.rb"))),
    Probe("Perl", ("perl",), ("perl", str(SAMPLES / "pi.pl"))),
    Probe("PHP", ("php",), ("php", str(SAMPLES / "pi.php"))),
    Probe("Tcl", ("tclsh",), ("tclsh", str(SAMPLES / "pi.tcl"))),
    Probe("Go", ("go",), ("go", "run", str(SAMPLES / "pi.go"))),
    Probe(
        "GCC C", ("gcc",),
        ("bash", "-lc", f"gcc -O2 {shlex.quote(str(SAMPLES / 'pi.c'))} -o "
         f"{shlex.quote(str(BUILD / 'pi-gcc'))} && "
         f"{shlex.quote(str(BUILD / 'pi-gcc'))}"),
    ),
    Probe(
        "G++ C++", ("g++",),
        ("bash", "-lc", f"g++ -O2 {shlex.quote(str(SAMPLES / 'pi.cpp'))} -o "
         f"{shlex.quote(str(BUILD / 'pi-gpp'))} && "
         f"{shlex.quote(str(BUILD / 'pi-gpp'))}"),
    ),
    Probe(
        "Clang C", ("clang",),
        ("bash", "-lc", f"clang -O2 {shlex.quote(str(SAMPLES / 'pi.c'))} -o "
         f"{shlex.quote(str(BUILD / 'pi-clang'))} && "
         f"{shlex.quote(str(BUILD / 'pi-clang'))}"),
    ),
    Probe(
        "Clang C++", ("clang++",),
        ("bash", "-lc", f"clang++ -O2 {shlex.quote(str(SAMPLES / 'pi.cpp'))} -o "
         f"{shlex.quote(str(BUILD / 'pi-clangpp'))} && "
         f"{shlex.quote(str(BUILD / 'pi-clangpp'))}"),
    ),
    Probe(
        "Java", ("javac", "java"),
        ("bash", "-lc", f"rm -rf {shlex.quote(str(BUILD / 'java'))}; "
         f"mkdir -p {shlex.quote(str(BUILD / 'java'))}; javac -d "
         f"{shlex.quote(str(BUILD / 'java'))} {shlex.quote(str(SAMPLES / 'Pi.java'))} "
         f"&& java -cp {shlex.quote(str(BUILD / 'java'))} Pi"),
    ),
    Probe(
        "Kotlin", ("kotlinc", "java"),
        ("bash", "-lc", f"kotlinc {shlex.quote(str(SAMPLES / 'Pi.kt'))} "
         f"-include-runtime -d {shlex.quote(str(BUILD / 'pi-kotlin.jar'))} && "
         f"java -jar {shlex.quote(str(BUILD / 'pi-kotlin.jar'))}"),
    ),
    Probe(
        "Swift", ("swiftc",),
        ("bash", "-lc", f"swiftc -O {shlex.quote(str(SAMPLES / 'pi.swift'))} -o "
         f"{shlex.quote(str(BUILD / 'pi-swift'))} && "
         f"{shlex.quote(str(BUILD / 'pi-swift'))}"),
    ),
    Probe(
        "Fortran", ("gfortran",),
        ("bash", "-lc", f"gfortran -O2 {shlex.quote(str(SAMPLES / 'pi.f90'))} -o "
         f"{shlex.quote(str(BUILD / 'pi-fortran'))} && "
         f"{shlex.quote(str(BUILD / 'pi-fortran'))}"),
    ),
    Probe(
        "Rust", ("rustc",),
        ("bash", "-lc", f"rustc --version && rustc -O "
         f"{shlex.quote(str(RUST / 'hello_pi_world.rs'))} -o "
         f"{shlex.quote(str(BUILD / 'pi-rust'))} && "
         f"{shlex.quote(str(BUILD / 'pi-rust'))}"),
    ),
)


def clipped(text: str, limit: int = 2400) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[:limit] + "\n...[clipped]"


def exit_text(code: int | None) -> str:
    if code is None:
        return "not started"
    if code < 0:
        try:
            return f"signal {signal.Signals(-code).name} ({-code})"
        except ValueError:
            return f"signal {-code}"
    return f"exit {code}"


def invoke(command: tuple[str, ...], timeout: int = 90) -> tuple[int | None, str]:
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=os.environ.copy(),
        )
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + (exc.stderr or "")
        return None, f"TIMEOUT after {timeout}s\n{output}"
    return result.returncode, (result.stdout + result.stderr).strip()


def run_probe(probe: Probe) -> tuple[str, str, int | None, str]:
    missing = [name for name in probe.required if shutil.which(name) is None]
    if missing:
        return "unavailable", f"not found in PATH: {', '.join(missing)}", None, ""

    code, output = invoke(probe.command)
    stdout = output.splitlines()
    if code == 0 and stdout[-1:] == [EXPECTED]:
        return "available", "expected output", code, clipped(output)
    return "failed", "unexpected output or nonzero exit", code, clipped(output)


def version_attempt(name: str) -> list[str]:
    path = shutil.which(name)
    if path is None:
        return [f"{name}: not found in PATH"]
    code, output = invoke((path, "--version"), timeout=15)
    lines = [f"{name} path: {path}", f"{name} --version: {exit_text(code)}"]
    lines.append(output or "(no stdout/stderr)")
    return lines


def write_rust_failure(rows: list[tuple[str, str, str, int | None, str]]) -> pathlib.Path:
    rust_row = next(row for row in rows if row[0] == "Rust")
    source = RUST / "hello_pi_world.rs"
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    uname = os.uname()
    proc_version = pathlib.Path("/proc/version")
    kernel_detail = proc_version.read_text(encoding="utf-8", errors="replace").strip() \
        if proc_version.exists() else "unavailable"

    lines = [
        "# Failed Rust Hello-Pi-World Track",
        "",
        "Generated by `python3 run_probe.py`. This file is intentionally verbose",
        "so an unavailable or failing Rust path is preserved beside the exact source.",
        "",
        "## Exact workload",
        "",
        "`hello_pi_world.rs` does exact integer long division of `355 / 113` and",
        "should print `hello 3.1415 world!`. It has no Cargo, crate, network, or",
        "external-library dependency.",
        "",
        "## Current result",
        "",
        f"- Status: **{rust_row[1]}**",
        f"- Detail: {rust_row[2]}",
        f"- Process result: {exit_text(rust_row[3])}",
        f"- Captured probe output: `{rust_row[4] or '(none)'}`",
        f"- Source: `rust/hello_pi_world.rs`",
        f"- SHA-256: `{source_hash}`",
        "",
        "## Tool discovery and version attempts",
        "",
        "```text",
        *version_attempt("rustc"),
        "",
        *version_attempt("cargo"),
        "",
        *version_attempt("rustup"),
        "```",
        "",
        "## Runtime context",
        "",
        "```text",
        f"sysname={uname.sysname}",
        f"release={uname.release}",
        f"machine={uname.machine}",
        f"/proc/version={kernel_detail}",
        f"PATH={os.environ.get('PATH', '')}",
        "```",
        "",
        "## Historical incident boundary",
        "",
        "A separate, earlier test of an uploaded matching Rust 1.96.0 GNU x86_64",
        "bundle observed Cargo launch but `rustc --version` terminate with SIGBUS",
        "(shell exit 135) during compiler startup under a gVisor runtime. That",
        "large bundle is deliberately **not** re-uploaded or retried by this small",
        "probe. See `RUST_INCIDENT.md` for the scoped historical record.",
    ]
    path = RUST / "FAILED_HELLO_WORLD.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_report(rows: list[tuple[str, str, str, int | None, str]],
                 rust_failure: pathlib.Path) -> pathlib.Path:
    REPORTS.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = REPORTS / f"probe-{stamp}.md"
    lines = [
        "# Sandbox Language Capability Probe",
        "",
        f"Generated: {dt.datetime.now(dt.timezone.utc).isoformat()}",
        "",
        "Workload: exact integer long division of rational approximant `355 / 113`.",
        f"Expected program output: `{EXPECTED}`",
        "",
        "| Probe | Status | Detail | Process result |",
        "| --- | --- | --- | --- |",
    ]
    for name, status, detail, code, _output in rows:
        lines.append(f"| {name} | {status} | {detail} | {exit_text(code)} |")

    lines.extend([
        "",
        "## Rust diagnostic artifact",
        "",
        f"Verbose Rust-track details: `{rust_failure.relative_to(ROOT)}`",
        "",
        "## Captured output",
        "",
    ])
    for name, status, _detail, _code, output in rows:
        lines.append(f"### {name} ({status})")
        lines.append("")
        lines.append("```text")
        lines.append(output or "(no captured output)")
        lines.append("```")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    BUILD.mkdir(parents=True, exist_ok=True)
    rows = []
    for probe in PROBES:
        status, detail, code, output = run_probe(probe)
        rows.append((probe.name, status, detail, code, output))
        print(f"{probe.name:12} {status:12} {detail}")
    rust_failure = write_rust_failure(rows)
    report = write_report(rows, rust_failure)
    print(f"\nRust record: {rust_failure}")
    print(f"Report: {report}")
    refresh = subprocess.run(
        ("python3", str(ROOT / "refresh_artifact.py")), cwd=ROOT, check=False
    )
    if refresh.returncode != 0:
        print("warning: could not refresh 17-missing-rust.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
