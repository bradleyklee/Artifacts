#!/usr/bin/env python3
"""Structural/checksum verifier for pre-compaction ledger blocks."""
from __future__ import annotations
import argparse, gzip, hashlib, json, tarfile, tempfile
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
    with tempfile.TemporaryDirectory(prefix='.check-legacy-') as td:
        with tarfile.open(args.block, 'r:gz') as tf:
            tf.extractall(td, filter='data')
        roots = [p for p in Path(td).iterdir() if p.is_dir()]
        if len(roots) != 1:
            fail('archive must contain exactly one root directory')
        root = roots[0]
        required = ['BLOCK.json','SHA256SUMS','start_state.json','end_state.json',
                    'ledger.ndjson.gz','summary.json','manifest.json','pair_faces.csv']
        missing = [x for x in required if not (root/x).exists()]
        if missing:
            fail('missing ' + ', '.join(missing))
        for line in (root/'SHA256SUMS').read_text(encoding='utf-8').splitlines():
            expected, name = line.split('  ', 1)
            if sha256(root/name) != expected:
                fail('checksum ' + name)
        block = json.loads((root/'BLOCK.json').read_text(encoding='utf-8'))
        start = json.loads((root/'start_state.json').read_text(encoding='utf-8'))
        end = json.loads((root/'end_state.json').read_text(encoding='utf-8'))
        events = int(block['events'])
        prior_hash = start.get('state_hash')
        count = 0
        with gzip.open(root/'ledger.ndjson.gz','rt',encoding='utf-8') as f:
            for count, line in enumerate(f, 1):
                row = json.loads(line)
                if int(row.get('step', -1)) != int(start['step']) + count:
                    fail(f'ledger step mismatch at record {count}')
                # Burner ledgers use the explicit *_state_hash keys.  Accept the
                # earlier short aliases only for archival compatibility.
                pre_hash = row.get('pre_state_hash', row.get('pre_hash'))
                post_hash = row.get('post_state_hash', row.get('post_hash'))
                if pre_hash and prior_hash and pre_hash != prior_hash:
                    fail(f'hash chain mismatch before record {count}')
                if post_hash:
                    prior_hash = post_hash
        if count != events:
            fail(f'ledger count {count} != {events}')
        if prior_hash and end.get('state_hash') and prior_hash != end['state_hash']:
            fail('endpoint hash mismatch')
        print(f"PASS {block.get('name', args.block.name)}: {events} legacy exact records, "
              f"{start['step']}..{end['step']}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
