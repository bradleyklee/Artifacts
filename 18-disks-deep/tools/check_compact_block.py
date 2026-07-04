#!/usr/bin/env python3
"""Standalone structural/checksum verifier for compact exact two-body blocks."""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, struct, tarfile, tempfile
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def fail(msg: str) -> None:
    raise SystemExit('FAIL ' + msg)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('block', type=Path)
    args = ap.parse_args()
    with tempfile.TemporaryDirectory(prefix='.check-compact-') as td:
        with tarfile.open(args.block, 'r:gz') as tf:
            tf.extractall(td, filter='data')
        roots = [p for p in Path(td).iterdir() if p.is_dir()]
        if len(roots) != 1:
            fail('archive must contain exactly one root directory')
        root = roots[0]
        needed = {
            'BLOCK.json', 'SHA256SUMS', 'start_state.json', 'end_state.json',
            'event_codes.u8', 'pair_faces.u8', 'pair_steps.u16',
            'complexity.csv.gz', 'single_surface_audit.json', 'receipt.json',
        }
        missing = sorted(x for x in needed if not (root / x).exists())
        if missing:
            fail('missing ' + ', '.join(missing))
        for line in (root / 'SHA256SUMS').read_text(encoding='utf-8').splitlines():
            expected, name = line.split('  ', 1)
            if sha256(root / name) != expected:
                fail('checksum ' + name)
        block = json.loads((root / 'BLOCK.json').read_text(encoding='utf-8'))
        if block.get('schema') != 'exact-two-body-compact-block/v3':
            fail('unsupported schema')
        events = int(block['events'])
        start = json.loads((root / 'start_state.json').read_text(encoding='utf-8'))
        end = json.loads((root / 'end_state.json').read_text(encoding='utf-8'))
        if start.get('state_hash') != block['start']['state_hash']:
            fail('start-state hash metadata mismatch')
        if end.get('state_hash') != block['end']['state_hash']:
            fail('end-state hash metadata mismatch')
        codes = (root / 'event_codes.u8').read_bytes()
        if len(codes) != events:
            fail(f'event-code length {len(codes)} != {events}')
        if any(c not in (0, 1) for c in codes):
            fail('event_codes contains nonregular event marker')
        faces = (root / 'pair_faces.u8').read_bytes()
        raw_steps = (root / 'pair_steps.u16').read_bytes()
        if len(raw_steps) % 2:
            fail('pair_steps length is not even')
        steps = list(struct.unpack('<' + 'H' * (len(raw_steps) // 2), raw_steps))
        if len(faces) != len(steps):
            fail('pair face/step count mismatch')
        if sum(codes) != len(faces):
            fail('pair code count mismatch')
        sides = int(block['geometry']['polygon_sides'])
        prior = 0
        for step, face in zip(steps, faces):
            if not (1 <= step <= events) or step <= prior:
                fail('pair steps not strictly increasing/in range')
            if codes[step - 1] != 1:
                fail(f'pair step {step} not marked pair')
            if face >= sides:
                fail(f'face {face} outside 0..{sides - 1}')
            prior = step
        with gzip.open(root / 'complexity.csv.gz', 'rt', newline='', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        if len(rows) != events:
            fail(f'complexity row count {len(rows)} != {events}')
        for i, row in enumerate(rows, 1):
            if int(row['step']) != int(block['start']['step']) + i:
                fail(f'complexity step mismatch at row {i}')
        audit = json.loads((root / 'single_surface_audit.json').read_text(encoding='utf-8'))
        if not audit.get('accepted'):
            fail('single-surface audit failed')
        print(
            f"PASS {block['name']}: {events} events, {len(faces)} pair faces, "
            f"{block['start']['step']}..{block['end']['step']}"
        )
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
