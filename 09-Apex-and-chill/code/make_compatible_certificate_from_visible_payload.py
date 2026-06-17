#!/usr/bin/env python3
"""Convert the PDF-visible reconstructed payload into verifier-compatible certificate JSON.

Input is produced by visible_pdf_scrape_rederive_pdfonly_v88_plus.py.  This
script does not read the original certificate.  It normalizes the PDF-derived
seed/accept/reject rules, replays them, writes growth counts, and emits a
payload accepted by verify_reduced_certificate_from_payload_v88.py.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

DIRS_AXIAL = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
BLOCKED = {(0, 0)}


def parse_coord(s: str) -> tuple[int, int]:
    q, r = s.split(',')
    return int(q), int(r)


def split_key(s: str) -> tuple[str, ...]:
    return tuple(s.split('|'))


def plus_state(st: str, k: int) -> str:
    if st == '*':
        return '*'
    typ, idx = st.split('.')
    return f'{typ}.{(int(idx) + k) % 6}'


def plus_inv_state(st: str, k: int) -> str:
    if st == '*':
        return '*'
    typ, idx = st.split('.')
    return f'{typ}.{(int(idx) - k) % 6}'


def plus_key(raw: tuple[str, ...], k: int) -> tuple[str, ...]:
    out = ['*'] * 6
    for p, st in enumerate(raw):
        out[(p + k) % 6] = plus_state(st, k)
    return tuple(out)


def plus_canon(raw: tuple[str, ...]) -> tuple[tuple[str, ...], int]:
    cands = [plus_key(tuple(raw), k) for k in range(6)]
    best = min(cands)
    return best, cands.index(best)


def frontier(state: dict[tuple[int, int], str]) -> set[tuple[int, int]]:
    out: set[tuple[int, int]] = set()
    for q, r in state:
        for dq, dr in DIRS_AXIAL:
            c = (q + dq, r + dr)
            if c not in state and c not in BLOCKED:
                out.add(c)
    return out


def replay(seed_axiom: dict[str, str], accept_rules: list[dict], reject_rules: list[dict], max_steps: int = 1000):
    state = {parse_coord(k): v for k, v in seed_axiom.items()}
    accept = {split_key(r['canonical_neighbor_key']): r['output'] for r in accept_rules}
    reject = {split_key(r['canonical_neighbor_key']) for r in reject_rules}
    history = []
    used_accept = set()
    used_reject = set()
    unknown = []
    for t in range(max_steps):
        births = {}
        unknown = []
        rejected_frontier = 0
        for q, r in sorted(frontier(state)):
            raw = tuple(state.get((q + dq, r + dr), '*') for dq, dr in DIRS_AXIAL)
            key, k = plus_canon(raw)
            if key in accept:
                births[(q, r)] = plus_inv_state(accept[key], k)
                used_accept.add(key)
            elif key in reject:
                rejected_frontier += 1
                used_reject.add(key)
            else:
                unknown.append({'cell': [q, r], 'canonical_key': list(key), 'rotation_k': k})
        history.append({
            't': t,
            'births': len(births),
            'placed': len(state) + len(births),
            'rejected_frontier': rejected_frontier,
            'unknown_frontier': len(unknown),
        })
        if not births:
            return state, history, unknown, used_accept, used_reject
        state.update(births)
    raise RuntimeError(f'max_steps exceeded: {max_steps}')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--in-json', required=True, type=Path)
    ap.add_argument('--out-json', required=True, type=Path)
    args = ap.parse_args()

    src = json.loads(args.in_json.read_text())
    seed = src['seed_axiom_from_transformed_visible_main']
    accept_rules = src['accept_rules']
    reject_rules = src['reject_rules']

    acc_keys = {r['canonical_neighbor_key'] for r in accept_rules}
    rej_keys = {r['canonical_neighbor_key'] for r in reject_rules}
    overlap = sorted(acc_keys & rej_keys)
    if overlap:
        raise SystemExit(f'accept/reject overlap: {overlap[:5]}')

    state, history, unknown, used_accept, used_reject = replay(seed, accept_rules, reject_rules)
    reconstructed_a = [len(seed) // 6] + [h['placed'] // 6 for h in history if h['births'] > 0]
    diffs = [b - a for a, b in zip(reconstructed_a, reconstructed_a[1:])]

    payload = {
        'artifact': 'apex852_visible_pdf_rederived_compatible_certificate',
        'source': src.get('source_pdf'),
        'derivation': 'PDF-visible/vector reconstruction only; generated from visible_pdf_rederived_payload.json, not from the official embedded certificate.',
        'canonicalization': 'v88 plus convention: slot p -> p+k; state index i -> i+k; center excluded from rule key.',
        'seed_axiom': seed,
        'accept_rules': accept_rules,
        'reject_rules': reject_rules,
        'verification': {
            'final_cells': len(state),
            'terminal_step': history[-1]['t'],
            'terminal_births': history[-1]['births'],
            'terminal_unknown_frontier': history[-1]['unknown_frontier'],
            'used_accept_outputs': len(used_accept),
            'used_reject_rules': len(used_reject),
        },
        'growth_counts': {
            'a_sequence': reconstructed_a,
            'first_differences': diffs,
        },
        'normalization_report': {
            'input_payload': str(args.in_json),
            'accept_rules': len(accept_rules),
            'reject_rules': len(reject_rules),
            'accept_reject_overlap': len(overlap),
            'unknown_terminal': len(unknown),
        },
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    print(json.dumps({
        'ok': True,
        'out_json': str(args.out_json),
        'final_cells': len(state),
        'terminal_step': history[-1]['t'],
        'terminal_births': history[-1]['births'],
        'terminal_unknown_frontier': history[-1]['unknown_frontier'],
        'used_accept_outputs': len(used_accept),
        'used_reject_rules': len(used_reject),
        'a_sequence_len': len(reconstructed_a),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
