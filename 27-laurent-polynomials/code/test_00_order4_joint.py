from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_order_four_guvj_certificate() -> None:
    worker = ROOT / "code" / "public" / "perturbation_case.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(worker),
            "--F",
            "x + y + 1/(x*y) + y**2",
            "--max-order",
            "4",
            "--max-support-level",
            "1",
            "--quiet",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        timeout=180,
    )
    result = json.loads(completed.stdout.strip().splitlines()[-1])
    assert result["status"] == "certificate_found"
    assert result["operator_stats"]["order"] == 4
    assert result["operator_stats"]["shift_degree"] == 9
    assert result["certificate"]["support_family"] == "newton"
    assert result["certificate"]["support_level"] == 1
    assert result["certificate"]["matrix_shape"] == [68, 188]
    assert result["checks"] == {
        "operator_from_joint_exact_identity": False,
        "operator_certified_by_GUVJ_identity": True,
        "divergence_identity_exact": True,
        "recurrence_replay_exact": True,
        "operator_from_finite_term_fit": True,
    }
