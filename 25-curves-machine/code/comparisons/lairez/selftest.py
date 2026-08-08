#!/usr/bin/env python3
"""Dependency-free regression checks for the comparison adapter."""

import json
import tempfile
from pathlib import Path

from adapter import ROOT, emit_magma, load_case, write_case


def main() -> None:
    cases = sorted((ROOT / "cases").glob("*.json"))
    assert {"triangle_square", "square_hexagon", "square_only", "hexagon_only",
            "triangle_hexagon"} <= {p.stem for p in cases}
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        for path in cases:
            case = load_case(path)
            text = emit_magma(case)
            assert "f := 2/(E-alpha);" in text
            assert "Res_{2H=alpha} 2 dp dq/(2H-alpha)" in text
            assert f"KNOWN_ORDER {case.get('known_operator_order', 'UNKNOWN')}" in text
            target = write_case(path, out)
            assert target.read_text(encoding="utf-8") == text
            json.loads(path.read_text(encoding="utf-8"))
    print("ADAPTER_SELFTEST_PASS")


if __name__ == "__main__":
    main()
