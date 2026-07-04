#!/usr/bin/env python3
"""Verify either a legacy ledger block or a compact v3 block.

This is the canonical verifier entry point. It detects the archive schema before
choosing the appropriate structural verifier.
"""
from __future__ import annotations
import argparse, json, subprocess, sys, tarfile, tempfile
from pathlib import Path


def archive_schema(path: Path) -> str:
    with tempfile.TemporaryDirectory(prefix='.detect-block-') as td:
        with tarfile.open(path, 'r:gz') as tf:
            members = [m for m in tf.getmembers() if m.isfile() and m.name.endswith('/BLOCK.json')]
            if len(members) != 1:
                raise SystemExit('FAIL archive must contain exactly one BLOCK.json')
            fh = tf.extractfile(members[0])
            if fh is None:
                raise SystemExit('FAIL cannot read BLOCK.json')
            block = json.loads(fh.read().decode('utf-8'))
    return str(block.get('schema', ''))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('block', type=Path)
    args = ap.parse_args()
    schema = archive_schema(args.block)
    root = Path(__file__).resolve().parent
    if schema == 'exact-two-body-compact-block/v3':
        tool = root / 'check_compact_block.py'
    else:
        tool = root / 'check_legacy_block.py'
    if not tool.exists():
        raise SystemExit(f'FAIL verifier missing for schema {schema!r}: {tool.name}')
    return subprocess.run([sys.executable, str(tool), str(args.block)]).returncode

if __name__ == '__main__':
    raise SystemExit(main())
