#!/usr/bin/env python3
"""Basic bounded search around uploaded DH12 seed records.

This is the release-facing local search target.  It consumes the uploaded seed
records, performs deterministic one-rule local edits around the best closed
parents, and writes candidate JSON files that replay as closed chills.
"""
from __future__ import annotations
import argparse, collections, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mini_dh12_sparse_search import load_records, replay, digest, materialize  # noqa:E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--records', nargs='+', required=True)
    ap.add_argument('--outdir', required=True)
    ap.add_argument('--keep-min', type=int, default=800)
    ap.add_argument('--max-trials', type=int, default=80)
    ap.add_argument('--max-found', type=int, default=5)
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    recs = load_records(args.records)
    seed_hashes = {r['_digest'] for r in recs}
    parents = [r for r in recs if r['_eval']['terminal_births'] == 0 and r['_eval']['unknown'] == 0]
    parents = sorted(parents, key=lambda r: (-r['_eval']['cells'], r['_digest']))

    out_counts = collections.defaultdict(collections.Counter)
    key_counts = collections.Counter()
    for r in parents:
        for k, v in r['_acc'].items():
            out_counts[k][v] += 1
            key_counts[k] += 1
        for k in r['_rej']:
            key_counts[k] += 1
    universe = sorted(key_counts)

    def default_out(k):
        return out_counts[k].most_common(1)[0][0] if out_counts[k] else 'H.0'

    trials = []
    found = []
    seen = set(seed_hashes)

    def try_candidate(acc, rej, op, parent_hash, edit_key):
        rej = {k for k in rej if k not in acc}
        h = digest(acc, rej)
        if h in seen:
            return False
        ev = replay(acc, rej)
        row = {
            'hash': h,
            'operator': op,
            'parent': parent_hash,
            'edit_key': list(edit_key) if edit_key else None,
            'cells': ev['cells'],
            'terminal_births': ev['terminal_births'],
            'terminal_unknown_frontier': ev['unknown'],
            'step': ev['terminal_step'],
            'accept': len(acc),
            'reject': len(rej),
        }
        trials.append(row)
        if ev['terminal_births'] == 0 and ev['unknown'] == 0 and ev['cells'] >= args.keep_min:
            seen.add(h)
            cand = materialize(acc, rej, ev, op, [parent_hash], seed=0)
            found.append(cand)
            (outdir / f'candidate_{len(found):04d}_{ev["cells"]:05d}_{h}.json').write_text(json.dumps(cand, indent=2, sort_keys=True) + '\n')
            return True
        return False

    for p in parents:
        if len(trials) >= args.max_trials or len(found) >= args.max_found:
            break
        parent_hash = p.get('rule_hash', p['_digest'])
        for k in sorted(p['_rej']):
            if len(trials) >= args.max_trials or len(found) >= args.max_found:
                break
            if out_counts[k]:
                acc = dict(p['_acc'])
                rej = set(p['_rej'])
                rej.discard(k)
                acc[k] = default_out(k)
                try_candidate(acc, rej, 'BASIC_REJECT_TO_ACCEPT', parent_hash, k)
        for k in sorted(p['_acc']):
            if len(trials) >= args.max_trials or len(found) >= args.max_found:
                break
            acc = dict(p['_acc'])
            rej = set(p['_rej'])
            acc.pop(k, None)
            rej.add(k)
            try_candidate(acc, rej, 'BASIC_ACCEPT_TO_REJECT', parent_hash, k)
        for k in universe:
            if len(trials) >= args.max_trials or len(found) >= args.max_found:
                break
            if k not in p['_acc'] and k not in p['_rej'] and out_counts[k]:
                acc = dict(p['_acc'])
                rej = set(p['_rej'])
                acc[k] = default_out(k)
                try_candidate(acc, rej, 'BASIC_ADD_ACCEPT', parent_hash, k)

    summary = {
        'ok': len(found) > 0,
        'purpose': 'basic bounded local search for more same-family closed-chill DH12 records',
        'loaded_records': len(recs),
        'valid_parent_records': len(parents),
        'trials': len(trials),
        'keep_min': args.keep_min,
        'new_closed_chill_ge_keep_min': len(found),
        'found_by_cells': dict(collections.Counter(str(r['cells']) for r in found)),
        'best_new_cells': max([r['cells'] for r in found], default=0),
        'candidate_dir': str(outdir),
        'found_index': [
            {'file': f'candidate_{i+1:04d}_{r["cells"]:05d}_{r["rule_hash"]}.json', 'hash': r['rule_hash'], 'cells': r['cells'], 'op': r['operator']}
            for i, r in enumerate(found)
        ],
        'top_trials': sorted(trials, key=lambda x: (x['cells'], -x['terminal_unknown_frontier']), reverse=True)[:20],
    }
    (outdir / 'basic_search_summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    (outdir / 'basic_search_trials.jsonl').write_text('\n'.join(json.dumps(x, sort_keys=True) for x in trials) + ('\n' if trials else ''))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
