#!/usr/bin/env python3
"""Convert bulky v2 blocks into compact v3 evidence blocks.

Safe default: write compact replacements under --out-dir; never modifies source
blocks.  --replace-in-place is explicit and first moves old archives to a dated
quarantine directory only after the compact archive verifies.
"""
from __future__ import annotations
import argparse, csv, datetime as dt, gzip, hashlib, json, math, os, shutil, struct
import subprocess, sys, tarfile, tempfile, time
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def run_checked(cmd: list[str], cwd: Path) -> None:
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(f"command failed: {' '.join(cmd)}\n{p.stdout}\n{p.stderr}")


def compact_one(source: Path, dest: Path, repo: Path) -> tuple[int, int]:
    """Return (source_bytes, dest_bytes), or raise."""
    run_checked([sys.executable, 'tools/check_block.py', str(source)], repo)
    with tempfile.TemporaryDirectory(prefix='.compact-', dir=dest.parent) as td:
        temp = Path(td)
        with tarfile.open(source, 'r:gz') as tf:
            tf.extractall(temp, filter='data')
        roots = [p for p in temp.iterdir() if p.is_dir()]
        if len(roots) != 1:
            raise RuntimeError('source block has invalid root layout')
        old = roots[0]
        old_block = json.loads((old / 'BLOCK.json').read_text(encoding='utf-8'))
        summary = json.loads((old / 'summary.json').read_text(encoding='utf-8'))
        manifest = json.loads((old / 'manifest.json').read_text(encoding='utf-8'))
        start = json.loads((old / 'start_state.json').read_text(encoding='utf-8'))
        end = json.loads((old / 'end_state.json').read_text(encoding='utf-8'))
        events = int(old_block['events'])
        rows: list[dict] = []
        codes = bytearray()
        faces = bytearray()
        pair_steps: list[int] = []
        with gzip.open(old / 'ledger.ndjson.gz', 'rt', encoding='utf-8') as f:
            for expected, line in enumerate(f, 1):
                row = json.loads(line)
                if int(row['step']) != int(start['step']) + expected:
                    raise RuntimeError(f'ledger step mismatch at record {expected}')
                batch = row.get('batch', [])
                if len(batch) != 1:
                    raise RuntimeError(f'non-singleton batch at step {row["step"]}')
                event = batch[0]
                kind = event.get('kind')
                if kind == 'WALL_FACE':
                    codes.append(0)
                elif kind == 'PAIR_FACE':
                    face = int(event['face'])
                    codes.append(1)
                    faces.append(face)
                    pair_steps.append(expected)
                else:
                    raise RuntimeError(f'nonregular event kind {kind!r} at step {row["step"]}')
                parts = row['time_complexity']['T_parts']
                out = {'step': str(row['step']), 'event_code': str(codes[-1])}
                for part in ('a', 'b', 'c', 'd'):
                    out[f'T_{part}_numerator_bits'] = str(parts[part]['numerator_bits'])
                    out[f'T_{part}_denominator_bits'] = str(parts[part]['denominator_bits'])
                # The common-denominator observable drives the live complexity
                # monitor.  It is calculated from exact_T here, not inferred
                # from reduced-component bit lengths.
                exact_t = row['exact_T']
                rats: dict[str, tuple[int, int]] = {}
                common_den = 1
                for part in ('a', 'b', 'c', 'd'):
                    text = str(exact_t[part])
                    if '/' in text:
                        numerator_text, denominator_text = text.split('/', 1)
                        numerator, denominator = int(numerator_text), int(denominator_text)
                    else:
                        numerator, denominator = int(text), 1
                    rats[part] = (numerator, denominator)
                    common_den = abs(common_den // math.gcd(common_den, denominator) * denominator)
                out['T_common_denominator_bits'] = str(common_den.bit_length())
                for part, (numerator, denominator) in rats.items():
                    out[f'T_common_{part}_numerator_bits'] = str(abs(numerator * (common_den // denominator)).bit_length())
                out['T_common_sum_bits'] = str(
                    int(out['T_common_denominator_bits']) +
                    sum(int(out[f'T_common_{part}_numerator_bits']) for part in ('a', 'b', 'c', 'd'))
                )
                out['T_max_component_bits'] = str(row['time_complexity']['T']['max_numerator_bits'])
                out['running_T_max_component_bits'] = str(row['time_complexity']['running_T']['max_numerator_bits'])
                rows.append(out)
        if len(rows) != events:
            raise RuntimeError(f'ledger contains {len(rows)} events; expected {events}')
        outroot = temp / f'{old_block["name"]}.compact'
        outroot.mkdir()
        for name in ('start_state.json', 'end_state.json', 'single_surface_audit.json'):
            shutil.copy2(old / name, outroot / name)
        (outroot / 'event_codes.u8').write_bytes(bytes(codes))
        (outroot / 'pair_faces.u8').write_bytes(bytes(faces))
        (outroot / 'pair_steps.u16').write_bytes(struct.pack('<' + 'H' * len(pair_steps), *pair_steps))
        fields = list(rows[0])
        with gzip.open(outroot / 'complexity.csv.gz', 'wt', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader(); w.writerows(rows)
        sides = int(manifest['model']['sides']) if isinstance(manifest.get('model'), dict) else int(manifest['model'].get('sides', 0))
        # Some manifests identify only model name. Derive side count robustly.
        if not sides:
            name = str(manifest.get('model', old_block.get('geometry', {}).get('model', '')))
            sides = 24 if '24' in name else 12
        geometry = old_block['geometry']
        geometry['polygon_sides'] = sides
        compact = {
            'schema': 'exact-two-body-compact-block/v3',
            'name': old_block['name'], 'events': events,
            'geometry': geometry,
            'start': {'step': start['step'], 'exact_T': start['exact_T'], 'state_hash': start['state_hash']},
            'end': {'step': end['step'], 'exact_T': end['exact_T'], 'state_hash': end['state_hash']},
            'native_face_alphabet_size': sides,
            'pair_contact_count': len(faces),
            'canonical_evidence': [
                'start_state.json', 'end_state.json', 'event_codes.u8', 'pair_faces.u8',
                'pair_steps.u16', 'complexity.csv.gz', 'single_surface_audit.json', 'receipt.json'
            ],
            'note': 'Compact block retains exact endpoints, native pair-face word, event type stream, and dense exact-clock bit series. Full verbose ledger intentionally omitted.',
        }
        (outroot / 'BLOCK.json').write_text(json.dumps(compact, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        receipt = {
            'schema': 'exact-two-body-compact-receipt/v1',
            'source_block': source.name,
            'source_block_sha256': sha256(source),
            'source_schema': old_block.get('schema'),
            'source_events': events,
            'source_summary_final_state_hash': summary.get('final_state_hash'),
            'derived_by': 'tools/compact_blocks.py',
            'derivation': 'verified source block, then derived compact streams from its exact ledger',
        }
        (outroot / 'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        names = sorted(p.name for p in outroot.iterdir() if p.is_file())
        (outroot / 'SHA256SUMS').write_text(
            ''.join(f'{sha256(outroot / n)}  {n}\n' for n in names), encoding='utf-8'
        )
        staged = dest.with_name('.' + dest.name + '.next')
        with tarfile.open(staged, 'w:gz') as tf:
            tf.add(outroot, arcname=old_block['name'])
        os.replace(staged, dest)
    run_checked([sys.executable, 'tools/check_compact_block.py', str(dest)], repo)
    return source.stat().st_size, dest.stat().st_size


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--blocks-dir', type=Path, default=Path('blocks'))
    ap.add_argument('--out-dir', type=Path, default=Path('compact_blocks'))
    ap.add_argument('--lanes', nargs='*', default=['d12', '24A', '24B'])
    ap.add_argument('--replace-in-place', action='store_true')
    ap.add_argument('--destroy-old', action='store_true', help='after verified compaction, atomically overwrite the bulky source archive')
    ap.add_argument('--confirm', default='')
    ap.add_argument('--keep-going', action='store_true')
    args = ap.parse_args()
    repo = Path('.').resolve()
    source_root = args.blocks_dir.resolve()
    out_root = args.out_dir.resolve()
    if (args.replace_in_place or args.destroy_old) and args.confirm != 'YES':
        raise SystemExit('--replace-in-place/--destroy-old requires --confirm YES')
    if args.destroy_old and not args.replace_in_place:
        raise SystemExit('--destroy-old requires --replace-in-place')
    files: list[tuple[str, Path]] = []
    for lane in args.lanes:
        files += [(lane, p) for p in sorted((source_root / lane).glob('*.block.tar.gz'))]
    if not files:
        raise SystemExit('no source blocks found')
    print(f'Compact scan: {len(files)} blocks; replace={args.replace_in_place}; destroy_old={args.destroy_old}', flush=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    quarantine = repo / 'campaign' / 'trash' / f'bulky_blocks_{stamp}'
    report = {'schema': 'compact-blocks/v1', 'utc': stamp, 'entries': []}
    total_old = total_new = 0
    started = time.monotonic()
    for i, (lane, source) in enumerate(files, 1):
        dest = (source.parent if args.replace_in_place else out_root / lane) / source.name
        if not args.replace_in_place:
            dest.parent.mkdir(parents=True, exist_ok=True)
        label = f'[{i}/{len(files)}] {lane}/{source.name}'
        print(f'{label} verify + compact...', flush=True)
        try:
            old, new = compact_one(source, dest if not args.replace_in_place else dest.with_name('.' + dest.name + '.compact'), repo)
            final = dest if not args.replace_in_place else dest.with_name('.' + dest.name + '.compact')
            if args.replace_in_place:
                if args.destroy_old:
                    # final has already passed the compact checker. os.replace is atomic
                    # on this filesystem and permanently discards only the verified
                    # bulky source archive at the same pathname.
                    os.replace(final, source)
                else:
                    quarantine_target = quarantine / lane / source.name
                    quarantine_target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(source), str(quarantine_target))
                    os.replace(final, source)
            total_old += old; total_new += new
            entry = {'source': str(source), 'compact': str(dest if not args.replace_in_place else source), 'status': 'PASS', 'source_bytes': old, 'compact_bytes': new}
            report['entries'].append(entry)
            elapsed = time.monotonic() - started
            print(f"{label} PASS {old / 1e6:.1f}MB -> {new / 1e6:.3f}MB; elapsed {elapsed:.0f}s", flush=True)
        except Exception as exc:
            report['entries'].append({'source': str(source), 'status': 'FAIL', 'error': str(exc)})
            print(f'{label} FAIL {exc}', flush=True)
            if not args.keep_going:
                break
    report['summary'] = {'source_bytes': total_old, 'compact_bytes': total_new, 'reclaimed_bytes_if_old_purged': max(0, total_old - total_new)}
    out_manifest = repo / 'campaign' / 'compact' / f'{stamp}_manifest.json'
    out_manifest.parent.mkdir(parents=True, exist_ok=True)
    out_manifest.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f"Compact complete: {total_old / 1e6:.1f}MB -> {total_new / 1e6:.3f}MB; manifest {out_manifest.relative_to(repo)}", flush=True)
    return 0 if all(x['status'] == 'PASS' for x in report['entries']) and len(report['entries']) == len(files) else 1

if __name__ == '__main__':
    raise SystemExit(main())
