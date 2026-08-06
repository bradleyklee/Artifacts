#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = dict(os.environ)
ENV.setdefault("TERM", "dumb")
ENV["PYTHONDONTWRITEBYTECODE"] = "1"


def run(command: list[str], cwd: Path | None = None) -> None:
    display = "+ " + " ".join(command)
    for line in textwrap.wrap(
        display,
        width=80,
        subsequent_indent="  ",
        break_long_words=False,
        break_on_hyphens=False,
    ):
        print(line, flush=True)
    subprocess.run(command, cwd=cwd or ROOT, env=ENV, check=True)


unittest_command = [
    sys.executable,
    "-m",
    "unittest",
    "discover",
    "-s",
    "tests",
    "-p",
    "test_*.py",
]

# Stage 1: derive the target database. The model scans must consume the
# generated target list rather than an unexplained hand-maintained list.
run(
    [sys.executable, "generate_configurations.py", "--check"],
    ROOT / "code" / "classification",
)
run(unittest_command, ROOT / "code" / "classification")

# Stage 2: verify every complete case through one exact public interface.
run(
    [sys.executable, "verify_complete_cases.py"],
    ROOT / "code" / "certificates",
)
run(unittest_command, ROOT / "code" / "certificates")

# Stage 3: measure both plane-Hamiltonian families against the generated
# 56-target nonconstant-J four-fibre slice.
run([sys.executable, "run_scan.py"], ROOT / "code" / "plane_scan")
run(
    [sys.executable, "search_curves.py", "--known-only"],
    ROOT / "code",
)
run(unittest_command, ROOT / "code" / "plane_scan")

# Stage 4: recompute period and Laurent data.
run(
    [sys.executable, "compute_periods.py", "--quick"],
    ROOT / "code" / "period_scan",
)
run(
    [sys.executable, "verify_recorded_search.py"],
    ROOT / "code" / "laurent_search",
)

# Stage 5: compile every Python source. This is intentionally stdlib-only.
run([sys.executable, "syntax_check.py"], ROOT / "code")
print("ALL RELEASE CHECKS PASSED", flush=True)
