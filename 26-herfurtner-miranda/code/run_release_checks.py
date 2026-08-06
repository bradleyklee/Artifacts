#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = dict(os.environ)
ENV.setdefault("TERM", "dumb")
ENV["PYTHONDONTWRITEBYTECODE"] = "1"


def run(command: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd or ROOT, env=ENV, check=True)


# Stage 1: derive the target database.  The model scans must never consume an
# unexplained hand-maintained list.
run([sys.executable, "generate_configurations.py", "--check"], ROOT / "code" / "classification")
run(
    [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"],
    ROOT / "code" / "classification",
)

# Stage 2: verify retained algebraic certificates.
run([sys.executable, "verify_promoted_cases.py"], ROOT / "code" / "certificates")
run([sys.executable, "verify_legacy_cases.py"], ROOT / "code" / "certificates")

# Stage 3: measure the two intended plane-Hamiltonian families against the
# generated 56-target nonconstant-J four-fibre slice.
run([sys.executable, "run_scan.py"], ROOT / "code" / "plane_scan")
run(
    [sys.executable, "run_model_search.py", "--known-only"],
    ROOT / "code",
)
run(
    [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"],
    ROOT / "code" / "plane_scan",
)

# Stage 4: recompute period and Laurent data.
run([sys.executable, "compute_periods.py", "--quick"], ROOT / "code" / "period_scan")
run([sys.executable, "verify_recorded_search.py"], ROOT / "code" / "laurent_search")

# Stage 5: compile every Python source.  This is intentionally stdlib-only;
# pytest is not required for a release audit.
run([sys.executable, "syntax_check.py"], ROOT / "code")
print("ALL RELEASE CHECKS PASSED", flush=True)
