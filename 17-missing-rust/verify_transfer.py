#!/usr/bin/env python3
"""Verify the transferred Rust/Go parity packet without requiring Rust."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
ARCHIVE = EVIDENCE / "rust-hard-disk-parity-poc.zip"
PAYLOAD = EVIDENCE / "rust-hard-disk-parity-poc"
EXPECTED_ARCHIVE_SHA256 = "63345e2f08f1f0d6c5e73068f473fd5245c68e70c7795243e3668b4baf3c4a2a"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    failures: list[str] = []
    got_archive = sha256(ARCHIVE)
    print(f"archive  {got_archive}  {ARCHIVE.relative_to(ROOT)}")
    if got_archive != EXPECTED_ARCHIVE_SHA256:
        failures.append("archive SHA-256 mismatch")

    sums = PAYLOAD / "SHA256SUMS"
    for raw in sums.read_text(encoding="utf-8").splitlines():
        expected, name = raw.split(maxsplit=1)
        path = PAYLOAD / name
        got = sha256(path)
        status = "OK" if got == expected else "MISMATCH"
        print(f"{status:8} {name}")
        if got != expected:
            failures.append(f"SHA-256 mismatch: {name}")

    go_out = (PAYLOAD / "go.out").read_bytes()
    rust_out = (PAYLOAD / "rust.out").read_bytes()
    if go_out == rust_out:
        print("PARITY   stored go.out and rust.out are byte-identical")
    else:
        print("MISMATCH stored go.out and rust.out differ")
        failures.append("stored Go/Rust output differs")

    if failures:
        print("FAIL: " + "; ".join(failures), file=sys.stderr)
        return 1
    print("PASS: transferred packet integrity and stored output parity verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
