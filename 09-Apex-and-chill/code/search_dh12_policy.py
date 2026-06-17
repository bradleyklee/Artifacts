#!/usr/bin/env python3
"""DH12 sparse policy search with mutate / mate / adopt operators.

This is the release-facing search target for 09-Apex-and-chill.  It uses the
same operator architecture described in the transfer notes:

- MUTATE: a random walk around one parent, informed by prior frequencies and
  signpost genes.
- MATE: an interior/averaging walk on the axis between two parent species.
- ADOPT_UP / ADOPT_DOWN: exterior walks on the same two-parent axis, where
  UP/DOWN are determined by the lifetime differential, not by arbitrary A/B side.
- ADOPT_EQUAL: exterior walk on either side when the two parents have equal lifetime.

The script writes machine-readable JSON/JSONL artifacts, but progress output is
plain and explicit so a human can see which method is running and what it finds.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import random
import sys
import textwrap
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mini_dh12_sparse_search import load_records, replay as full_replay, digest, materialize, SEED, DIRS, frontier, canon, inv_rot_state  # noqa: E402

def emit(tag: str, message: str = "") -> None:
    """Print progress lines wrapped for an 80-column terminal."""
    prefix = f"[{tag}] "
    width = 80
    if not message:
        print(prefix.rstrip(), flush=True)
        return
    wrapped = textwrap.wrap(str(message), width=width - len(prefix)) or [""]
    print(prefix + wrapped[0], flush=True)
    pad = " " * len(prefix)
    for part in wrapped[1:]:
        print(pad + part, flush=True)


Key = Tuple[str, ...]
Status = Tuple[str, Optional[str]]  # ('A', out), ('R', None), or ('B', None)


def key_from_list(xs: Sequence[str]) -> Key:
    return tuple(xs)


def short_parent_id(r: dict) -> str:
    return r.get('rule_hash') or r.get('_hash') or r.get('_digest') or 'unknown'


def status_of(acc: Dict[Key, str], rej: Set[Key], key: Key) -> Status:
    if key in acc:
        return ('A', acc[key])
    if key in rej:
        return ('R', None)
    return ('B', None)


def put_status(acc: Dict[Key, str], rej: Set[Key], key: Key, status: Status, default_out: str = 'H.0') -> None:
    tag, out = status
    if tag == 'A':
        acc[key] = out or default_out
        rej.discard(key)
    elif tag == 'R':
        acc.pop(key, None)
        rej.add(key)
    else:
        acc.pop(key, None)
        rej.discard(key)


def status_key(st: Status) -> str:
    return st[0] + ((':' + st[1]) if st[0] == 'A' and st[1] else '')


def compact_status(st: Status) -> str:
    if st[0] == 'A':
        return f"A->{st[1]}"
    if st[0] == 'R':
        return 'R'
    return 'blank'


def bounded_replay(acc: Dict[Key, str], rej: Set[Key], max_steps: int = 70, max_cells: int = 2000) -> dict:
    """Replay used during search, with an early abort for open giants.

    Full verification is still done by the certificate verifier.  The search loop
    only needs to distinguish closed chills from open/still-growing candidates;
    aborting very large open trials keeps `make search` interactive.
    """
    state = dict(SEED)
    hist = []
    useda = set()
    usedr = set()
    unknown = []
    aborted = False
    for t in range(max_steps):
        births = {}
        unknown = []
        rejc = 0
        for q, r in sorted(frontier(state)):
            raw = tuple(state.get((q+dq, r+dr), '*') for dq, dr in DIRS)
            key, k = canon(raw)
            if key in acc:
                births[(q, r)] = inv_rot_state(acc[key], k)
                useda.add(key)
            elif key in rej:
                rejc += 1
                usedr.add(key)
            else:
                unknown.append((q, r, key, k))
        next_cells = len(state) + len(births)
        hist.append({'t': t, 'births': len(births), 'placed': next_cells, 'unknown_frontier': len(unknown), 'rejected_frontier': rejc})
        if not births:
            break
        state.update(births)
        if len(state) > max_cells:
            aborted = True
            hist[-1]['aborted_max_cells'] = max_cells
            break
    if not hist:
        hist.append({'t': 0, 'births': 0, 'placed': len(state), 'unknown_frontier': 0, 'rejected_frontier': 0})
    terminal_births = hist[-1]['births']
    if aborted and terminal_births == 0:
        terminal_births = 1
    return {
        'cells': len(state),
        'terminal_step': hist[-1]['t'],
        'terminal_births': terminal_births,
        'unknown': hist[-1]['unknown_frontier'],
        'rejected_frontier': hist[-1]['rejected_frontier'],
        'used_accept': len(useda),
        'used_reject': len(usedr),
        'state': state,
        'history': hist,
        'aborted_max_cells': max_cells if aborted else None,
    }


def load_signposts(path: Optional[str]) -> Dict[Key, dict]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    rows = json.loads(p.read_text())
    out = {}
    for row in rows:
        k = key_from_list(row['key'])
        out[k] = row
    return out


def weighted_choice(rng: random.Random, items: Sequence[Key], weights: Sequence[float]) -> Key:
    # random.choices is deterministic but can be opaque; this keeps zero/NaN safe.
    clean = [max(0.0, float(w)) if math.isfinite(float(w)) else 0.0 for w in weights]
    total = sum(clean)
    if total <= 0:
        return rng.choice(list(items))
    x = rng.random() * total
    acc = 0.0
    for item, w in zip(items, clean):
        acc += w
        if x <= acc:
            return item
    return items[-1]


class PriorStats:
    def __init__(self, parents: Sequence[dict], signposts: Dict[Key, dict]):
        self.parents = list(parents)
        self.signposts = signposts
        self.out_counts: Dict[Key, collections.Counter] = collections.defaultdict(collections.Counter)
        self.status_counts: Dict[Key, collections.Counter] = collections.defaultdict(collections.Counter)
        self.key_counts: collections.Counter = collections.Counter()
        self.cells_by_key_status: Dict[Key, Dict[str, List[int]]] = collections.defaultdict(lambda: collections.defaultdict(list))
        self.key_by_group: Dict[str, Set[Key]] = {'accept': set(), 'reject': set(), 'blank': set(), 'signpost': set()}
        for r in parents:
            cells = int(r['_eval']['cells'])
            acc, rej = r['_acc'], r['_rej']
            keys = set(acc) | set(rej)
            for k, v in acc.items():
                self.out_counts[k][v] += 1
                self.status_counts[k]['A'] += 1
                self.key_counts[k] += 1
                self.cells_by_key_status[k]['A'].append(cells)
                self.key_by_group['accept'].add(k)
            for k in rej:
                self.status_counts[k]['R'] += 1
                self.key_counts[k] += 1
                self.cells_by_key_status[k]['R'].append(cells)
                self.key_by_group['reject'].add(k)
            # Explicit blanks are observed by absence relative to the current key universe later.
        for k in signposts:
            self.key_counts[k] += 1
            self.key_by_group['signpost'].add(k)
        self.universe: List[Key] = sorted(set(self.key_counts) | set(signposts))
        n = max(1, len(parents))
        for k in self.universe:
            seen = self.status_counts[k]['A'] + self.status_counts[k]['R']
            blank = max(0, n - seen)
            if blank:
                self.status_counts[k]['B'] = blank
                self.key_by_group['blank'].add(k)
                # Approximate blank-associated cells by parent cells where absent.
                for r in parents:
                    if k not in r['_acc'] and k not in r['_rej']:
                        self.cells_by_key_status[k]['B'].append(int(r['_eval']['cells']))

    def default_out(self, k: Key) -> str:
        if self.out_counts[k]:
            return self.out_counts[k].most_common(1)[0][0]
        row = self.signposts.get(k)
        if row and row.get('out852'):
            return row['out852']
        return 'H.0'

    def majority_status(self, k: Key) -> Status:
        c = self.status_counts[k]
        tag, _ = c.most_common(1)[0] if c else ('B', 0)
        if tag == 'A':
            return ('A', self.default_out(k))
        if tag == 'R':
            return ('R', None)
        return ('B', None)

    def score_status(self, k: Key, tag: str) -> float:
        vals = self.cells_by_key_status[k].get(tag) or []
        if not vals:
            return 0.0
        return sum(vals) / len(vals)

    def key_weight(self, k: Key, prefer: Optional[str] = None) -> float:
        c = self.status_counts[k]
        n = max(1, len(self.parents))
        freq = (c.get('A', 0) + c.get('R', 0)) / n
        # Entropy favors knobs that vary; frequency keeps common useful genes visible.
        probs = [c.get(x, 0) / n for x in ('A', 'R', 'B') if c.get(x, 0)]
        entropy = -sum(p * math.log(p + 1e-12) for p in probs)
        sp = self.signposts.get(k)
        signpost_bonus = 0.0
        if sp:
            signpost_bonus = 2.0 + float(sp.get('lift', 0.0))
        prefer_bonus = 0.0
        if prefer:
            prefer_bonus = c.get(prefer, 0) / n
        return 0.25 + 2.0 * freq + 2.5 * entropy + signpost_bonus + 1.5 * prefer_bonus

    def choose_key(self, rng: random.Random, prefer: Optional[str] = None, candidates: Optional[Iterable[Key]] = None) -> Key:
        items = sorted(set(candidates) if candidates is not None else self.universe)
        weights = [self.key_weight(k, prefer=prefer) for k in items]
        return weighted_choice(rng, items, weights)

    def choose_status_from_prior(self, rng: random.Random, k: Key, temperature: float = 0.15) -> Status:
        c = self.status_counts[k]
        # Prefer the status associated with larger records, but leave randomness.
        scored = []
        for tag in ('A', 'R', 'B'):
            count = c.get(tag, 0)
            mean_cells = self.score_status(k, tag)
            scored.append((tag, count + temperature, max(0.0, mean_cells - 600.0)))
        weights = [(cnt * (1.0 + cellscore / 180.0)) for _, cnt, cellscore in scored]
        tag = weighted_choice(rng, [x[0] for x in scored], weights)
        if tag == 'A':
            return ('A', self.default_out(k))
        if tag == 'R':
            return ('R', None)
        return ('B', None)


def parent_weight(r: dict) -> float:
    ev = r['_eval']
    # Reward larger closed records but keep 696 diversity alive.
    return max(1.0, (ev['cells'] - 630) ** 2 / 2000.0 + ev['used_accept'] + ev['used_reject'] / 2.0)


def choose_parent(rng: random.Random, parents: Sequence[dict]) -> dict:
    return rng.choices(list(parents), weights=[parent_weight(r) for r in parents], k=1)[0]


def lifetime(r: dict) -> int:
    """Search lifetime used to orient the differential axis.

    For these finite records the natural lifetime is the terminal replay step.
    The cell count is size; it is not used to decide UP/DOWN.
    """
    return int(r['_eval'].get('terminal_step', 0))


def lifetime_relation(a: dict, b: dict) -> str:
    la, lb = lifetime(a), lifetime(b)
    if la < lb:
        return 'UP_FROM_A_TO_B'
    if la > lb:
        return 'DOWN_FROM_A_TO_B'
    return 'EQUAL_LIFETIME'


def build_lifetime_pair_pool(parents: Sequence[dict], relation: str) -> List[Tuple[dict, dict, float]]:
    """Precompute adopt pair pools so search does not rescan all pairs each trial."""
    top = sorted(parents, key=lambda r: (-r['_eval']['cells'], lifetime(r), short_parent_id(r)))[:min(50, len(parents))]
    pairs: List[Tuple[dict, dict, float]] = []
    for i, a in enumerate(top):
        for b in top[i+1:]:
            if relation == 'UNEQUAL' and lifetime(a) == lifetime(b):
                continue
            if relation == 'EQUAL' and lifetime(a) != lifetime(b):
                continue
            d = hamming_status_distance(a, b) if '_acc' in a and '_acc' in b else 1
            cells_bonus = max(1, min(a['_eval']['cells'], b['_eval']['cells']) - 650)
            life_gap_bonus = 1 + abs(lifetime(a) - lifetime(b))
            weight = max(1.0, d) * (1.0 + cells_bonus / 300.0) * life_gap_bonus
            pairs.append((a, b, weight))
    return pairs


def choose_pair_from_pool(rng: random.Random, pool: Sequence[Tuple[dict, dict, float]], parents: Sequence[dict]) -> Tuple[dict, dict]:
    if not pool:
        return choose_pair(rng, parents)
    idx = weighted_choice(rng, list(range(len(pool))), [x[2] for x in pool])
    return pool[idx][0], pool[idx][1]


def choose_pair_with_lifetime_relation(rng: random.Random, parents: Sequence[dict], relation: str) -> Tuple[dict, dict]:
    """Choose a parent pair with unequal/equal lifetime when possible."""
    return choose_pair_from_pool(rng, build_lifetime_pair_pool(parents, relation), parents)


def hamming_status_distance(a: dict, b: dict) -> int:
    keys = set(a['_acc']) | set(a['_rej']) | set(b['_acc']) | set(b['_rej'])
    return sum(status_key(status_of(a['_acc'], a['_rej'], k)) != status_key(status_of(b['_acc'], b['_rej'], k)) for k in keys)


def choose_pair(rng: random.Random, parents: Sequence[dict]) -> Tuple[dict, dict]:
    # Favor one good/high record and one diverse record, like the prior mating runs.
    top = sorted(parents, key=lambda r: (-r['_eval']['cells'], short_parent_id(r)))[:min(40, len(parents))]
    a = choose_parent(rng, top)
    candidates = [b for b in top if b is not a]
    if not candidates:
        return a, a
    weights = []
    for b in candidates:
        d = hamming_status_distance(a, b)
        cells_bonus = max(1, b['_eval']['cells'] - 650)
        weights.append(max(1.0, d) * (1.0 + cells_bonus / 300.0))
    b = weighted_choice(rng, candidates, weights)
    return a, b


def mutate_candidate(rng: random.Random, p: dict, stats: PriorStats, max_edits: int) -> Tuple[Dict[Key, str], Set[Key], dict]:
    acc = dict(p['_acc'])
    rej = set(p['_rej'])
    # The old mutation walk used short random walks, with occasional longer jumps.
    n_edits = min(max_edits, rng.choice([1, 1, 2, 2, 3, 4, 5, 8]))
    edits = []
    for _ in range(n_edits):
        mode = rng.random()
        if mode < 0.30 and rej:
            k = stats.choose_key(rng, prefer='A', candidates=rej)
            old = status_of(acc, rej, k)
            put_status(acc, rej, k, ('A', stats.default_out(k)))
        elif mode < 0.55 and acc:
            k = stats.choose_key(rng, prefer='R', candidates=acc)
            old = status_of(acc, rej, k)
            # Most accept removals become reject, some become unknown/blank.
            put_status(acc, rej, k, ('R', None) if rng.random() < 0.70 else ('B', None))
        elif mode < 0.78:
            absent = [k for k in stats.universe if k not in acc and k not in rej]
            if not absent:
                continue
            k = stats.choose_key(rng, prefer='A', candidates=absent)
            old = status_of(acc, rej, k)
            # Signposts and accept-heavy keys tend to be accept insertions.
            st = stats.choose_status_from_prior(rng, k)
            if k in stats.signposts and rng.random() < 0.85:
                st = ('A', stats.default_out(k))
            put_status(acc, rej, k, st)
        else:
            k = stats.choose_key(rng)
            old = status_of(acc, rej, k)
            st = stats.choose_status_from_prior(rng, k)
            put_status(acc, rej, k, st)
        edits.append({'key': list(k), 'from': compact_status(old), 'to': compact_status(status_of(acc, rej, k))})
    return acc, {k for k in rej if k not in acc}, {'edits': edits, 'walk_length': n_edits}


def mate_candidate(rng: random.Random, a: dict, b: dict, stats: PriorStats, max_edits: int) -> Tuple[Dict[Key, str], Set[Key], dict]:
    # MATE is an interior/averaging walk on the A--B axis.
    # In this sparse categorical representation, the axis coordinates are the
    # rule keys where A and B disagree; an interior point keeps A on some
    # coordinates and takes B on the rest.  No off-axis repair edits are made.
    alpha = rng.uniform(0.10, 0.55)
    acc = dict(a['_acc'])
    rej = set(a['_rej'])
    keys = sorted(set(a['_acc']) | set(a['_rej']) | set(b['_acc']) | set(b['_rej']))
    axis_keys = []
    moved = []
    for k in keys:
        sa = status_of(a['_acc'], a['_rej'], k)
        sb = status_of(b['_acc'], b['_rej'], k)
        if status_key(sa) == status_key(sb):
            continue
        axis_keys.append(k)
        # Interior averaging: move from A toward B with probability alpha,
        # modulated gently by the learned prior weight on that coordinate.
        p = min(0.95, alpha * min(1.75, stats.key_weight(k) / 4.5))
        if rng.random() < p:
            before = status_of(acc, rej, k)
            put_status(acc, rej, k, sb, stats.default_out(k))
            moved.append({'key': list(k), 'from': compact_status(before), 'to': compact_status(status_of(acc, rej, k))})
    return acc, {k for k in rej if k not in acc}, {
        'axis': [short_parent_id(a), short_parent_id(b)],
        'axis_mode': 'interior_average',
        'alpha': round(alpha, 4),
        'axis_disagreements': len(axis_keys),
        'moved': moved[:24],
        'moves': len(moved),
    }


def exterior_status(side: Status, other: Status, stats: PriorStats, key: Key, rng: random.Random) -> Status:
    # Exterior side of a categorical A--B axis coordinate.  If the protected side
    # is known, keep/reinforce it.  If the protected side is blank and the other
    # side is known, usually stay blank; rarely step to the opposite known class.
    if side[0] != 'B':
        return side
    if rng.random() < 0.80:
        return ('B', None)
    if other[0] == 'A':
        return ('R', None)
    if other[0] == 'R':
        return ('A', stats.default_out(key))
    return side


def orient_axis_by_lifetime(a: dict, b: dict) -> Tuple[Optional[dict], Optional[dict], str]:
    """Return (low_lifetime_parent, high_lifetime_parent, relation).

    UP/DOWN are lifetime directions.  If lifetimes are equal there is no up/down;
    ADOPT_EQUAL must choose an exterior side explicitly.
    """
    la, lb = lifetime(a), lifetime(b)
    if la < lb:
        return a, b, 'A_LOW_B_HIGH'
    if la > lb:
        return b, a, 'B_LOW_A_HIGH'
    return None, None, 'EQUAL_LIFETIME'


def adopt_candidate(rng: random.Random, a: dict, b: dict, stats: PriorStats, direction: str) -> Tuple[Dict[Key, str], Set[Key], dict]:
    """Exterior walk on the A--B axis.

    direction=UP means go beyond the higher-lifetime parent.
    direction=DOWN means go beyond the lower-lifetime parent.
    direction=EQUAL means lifetimes are tied; choose either exterior side, but
    record which side was chosen.
    """
    low, high, relation = orient_axis_by_lifetime(a, b)
    la, lb = lifetime(a), lifetime(b)
    if direction == 'UP':
        if high is None:
            # Equal lifetimes have no up direction; fall back to equal exterior.
            side = rng.choice([a, b])
            other = b if side is a else a
            actual_direction = 'EQUAL'
        else:
            side, other = high, low
            actual_direction = 'UP'
    elif direction == 'DOWN':
        if low is None:
            side = rng.choice([a, b])
            other = b if side is a else a
            actual_direction = 'EQUAL'
        else:
            side, other = low, high
            actual_direction = 'DOWN'
    elif direction == 'EQUAL':
        side = rng.choice([a, b])
        other = b if side is a else a
        actual_direction = 'EQUAL'
    else:
        raise ValueError(direction)

    acc = dict(side['_acc'])
    rej = set(side['_rej'])
    keys = sorted(set(a['_acc']) | set(a['_rej']) | set(b['_acc']) | set(b['_rej']))
    frac = rng.uniform(0.18, 0.70)
    axis_keys = []
    moved = []
    for k in keys:
        sa = status_of(a['_acc'], a['_rej'], k)
        sb = status_of(b['_acc'], b['_rej'], k)
        if status_key(sa) == status_key(sb):
            continue
        axis_keys.append(k)
        ss = status_of(side['_acc'], side['_rej'], k)
        so = status_of(other['_acc'], other['_rej'], k)
        p = min(0.98, frac * min(2.0, stats.key_weight(k) / 3.8))
        if rng.random() < p:
            before = status_of(acc, rej, k)
            st = exterior_status(ss, so, stats, k, rng)
            put_status(acc, rej, k, st, stats.default_out(k))
            moved.append({'key': list(k), 'from': compact_status(before), 'to': compact_status(status_of(acc, rej, k))})
    return acc, {k for k in rej if k not in acc}, {
        'axis': [short_parent_id(a), short_parent_id(b)],
        'axis_mode': 'exterior_lifetime_' + actual_direction.lower(),
        'requested_direction': direction,
        'actual_direction': actual_direction,
        'lifetime_a': la,
        'lifetime_b': lb,
        'lifetime_relation': relation,
        'exterior_parent': short_parent_id(side),
        'opposite_parent': short_parent_id(other),
        'exterior_parent_lifetime': lifetime(side),
        'opposite_parent_lifetime': lifetime(other),
        'exterior_fraction': round(frac, 4),
        'axis_disagreements': len(axis_keys),
        'moved': moved[:24],
        'moves': len(moved),
    }




def terminal_state_digest(state: dict) -> str:
    """Stable digest of the terminal phenotype, independent of rule-table hash."""
    rows = []
    for (q, r), st in sorted(state.items()):
        rows.append(f"{q},{r}:{st}")
    return hashlib.sha256('\n'.join(rows).encode()).hexdigest()[:16]

def trial_status(ev: dict) -> str:
    if ev['terminal_births'] == 0 and ev['unknown'] == 0:
        return 'CLOSED_CHILL'
    if ev['terminal_births'] == 0:
        return 'STALLED_UNKNOWN'
    return 'OPEN_OR_CONFLICT'


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--records', nargs='+', required=True)
    ap.add_argument('--signposts')
    ap.add_argument('--outdir', required=True)
    ap.add_argument('--seed', type=int, default=2026061709)
    ap.add_argument('--keep-min', type=int, default=800)
    ap.add_argument('--mutations', type=int, default=300)
    ap.add_argument('--mates', type=int, default=300)
    ap.add_argument('--adopts', type=int, default=None, help='backward-compatible total adopts, split evenly into adopt-up/adopt-down if adopt-specific counts are absent')
    ap.add_argument('--adopt-ups', type=int, default=None)
    ap.add_argument('--adopt-downs', type=int, default=None)
    ap.add_argument('--adopt-equals', type=int, default=0, help='equal-lifetime exterior walks; each trial chooses either side')
    ap.add_argument('--max-found', type=int, default=50,
                    help='target count for reports; does not stop the schedule unless --stop-after-max-found is set')
    ap.add_argument('--stop-after-max-found', action='store_true',
                    help='allow early stop after --max-found, but only after the per-operator minimum is met')
    ap.add_argument('--min-trials-before-stop', type=int, default=0,
                    help='with --stop-after-max-found, run at least this many trials in every operator block before stopping that block')
    ap.add_argument('--max-edits', type=int, default=8)
    ap.add_argument('--max-replay-steps', type=int, default=70, help='bound replay during search; 852 certificate closes at step 60')
    ap.add_argument('--max-cells', type=int, default=2000, help='abort search replay when an open candidate exceeds this many cells')
    ap.add_argument('--progress-every', type=int, default=50)
    ap.add_argument('--allow-known-state', action='store_true', help='save candidates even when their terminal state matches a known seed or earlier hit')
    ap.add_argument('--found-mode', choices=['brief', 'full', 'none'], default='brief', help='how much to print for each found candidate')
    args = ap.parse_args()

    rng = random.Random(args.seed)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'candidates').mkdir(exist_ok=True)

    recs = load_records(args.records)
    seed_hashes = {r['_digest'] for r in recs}
    parents = [r for r in recs if r['_eval']['terminal_births'] == 0 and r['_eval']['unknown'] == 0]
    parents = sorted(parents, key=lambda r: (-r['_eval']['cells'], short_parent_id(r)))
    signposts = load_signposts(args.signposts)
    stats = PriorStats(parents, signposts)
    unequal_pair_pool = build_lifetime_pair_pool(parents, 'UNEQUAL')
    equal_pair_pool = build_lifetime_pair_pool(parents, 'EQUAL')

    emit('SEARCH', f'records={len(recs)} closed_parents={len(parents)}')
    emit('SEARCH', f'seed={args.seed} keep_min={args.keep_min}')
    emit('SEARCH', f'prior_keys={len(stats.universe)} signposts={len(signposts)}')
    emit('SEARCH', f'adopt_pairs_updown={len(unequal_pair_pool)}')
    emit('SEARCH', f'adopt_pairs_equal={len(equal_pair_pool)}')
    adopt_ups = args.adopt_ups
    adopt_downs = args.adopt_downs
    if adopt_ups is None or adopt_downs is None:
        total_adopts = args.adopts if args.adopts is not None else 300
        if adopt_ups is None:
            adopt_ups = total_adopts // 2
        if adopt_downs is None:
            adopt_downs = total_adopts - adopt_ups
    emit('SEARCH', 'operators:')
    emit('SEARCH', f'MUTATE={args.mutations} MATE={args.mates}')
    emit('SEARCH', f'ADOPT_UP={adopt_ups} ADOPT_DOWN={adopt_downs}')
    emit('SEARCH', f'ADOPT_EQUAL={args.adopt_equals}')
    emit('SEARCH', 'geometry:')
    emit('SEARCH', 'MATE is interior averaging on the parent axis')
    emit('SEARCH', 'ADOPT_UP moves up the lifetime differential')
    emit('SEARCH', 'ADOPT_DOWN moves down the lifetime differential')
    emit('SEARCH', 'ADOPT_EQUAL handles equal-lifetime pairs')

    seen = set(seed_hashes)
    tried_hashes = set(seed_hashes)
    seed_state_hashes = {terminal_state_digest(r['_eval']['state']) for r in recs if r['_eval']['terminal_births'] == 0 and r['_eval']['unknown'] == 0}
    seen_state_hashes = set(seed_state_hashes)
    replay_cache = {}
    duplicate_rule_skips = collections.Counter()
    duplicate_state_skips = collections.Counter()
    trials: List[dict] = []
    found: List[dict] = []
    operator_counts = collections.Counter()
    operator_found = collections.defaultdict(collections.Counter)
    best = {'cells': 0, 'operator': None, 'hash': None, 'status': None}
    best_closed = {'cells': 0, 'operator': None, 'hash': None, 'state_hash': None}

    def store_trial(op: str, acc: Dict[Key, str], rej: Set[Key], parents_ids: List[str], meta: dict, index: int) -> None:
        nonlocal best, best_closed
        rej = {k for k in rej if k not in acc}
        h = digest(acc, rej)
        operator_counts[op] += 1
        if h in tried_hashes:
            duplicate_rule_skips[op] += 1
            if args.progress_every and index % args.progress_every == 0:
                emit('PROGRESS', f'{op} t={index} duplicate_rule={h}')
                emit('PROGRESS', f'best={best["cells"]} best_op={best["operator"]}')
                emit('PROGRESS', f'closed={best_closed["cells"]} found={len(found)}')
            return
        tried_hashes.add(h)
        if h in replay_cache:
            ev = replay_cache[h]
        else:
            ev = bounded_replay(acc, rej, max_steps=args.max_replay_steps, max_cells=args.max_cells)
            replay_cache[h] = ev
        status = trial_status(ev)
        state_hash = terminal_state_digest(ev['state'])
        is_new_state = state_hash not in seen_state_hashes
        row = {
            'operator': op,
            'trial_index': index,
            'hash': h,
            'state_hash': state_hash,
            'parents': parents_ids,
            'cells': ev['cells'],
            'status': status,
            'terminal_births': ev['terminal_births'],
            'terminal_unknown_frontier': ev['unknown'],
            'terminal_step': ev['terminal_step'],
            'accept': len(acc),
            'reject': len(rej),
            'used_accept': ev['used_accept'],
            'used_reject': ev['used_reject'],
            'is_new': h not in seen,
            'is_new_terminal_state': is_new_state,
            'meta': meta,
        }
        trials.append(row)
        if ev['cells'] > best.get('cells', -1):
            best = {'cells': ev['cells'], 'operator': op, 'hash': h, 'state_hash': state_hash, 'status': status}
        if h not in seen and status == 'CLOSED_CHILL' and ev['cells'] >= args.keep_min:
            if (not args.allow_known_state) and (not is_new_state):
                duplicate_state_skips[op] += 1
            else:
                seen.add(h)
                seen_state_hashes.add(state_hash)
                cand = materialize(acc, rej, ev, op, parents_ids, args.seed)
                cand['state_hash'] = state_hash
                cand['is_new_terminal_state'] = is_new_state
                cand['search_meta'] = meta
                found.append(cand)
                if ev['cells'] > best_closed.get('cells', -1):
                    best_closed = {'cells': ev['cells'], 'operator': op, 'hash': h, 'state_hash': state_hash}
                operator_found[op][str(ev['cells'])] += 1
                fname = f"candidate_{len(found):04d}_{op}_{ev['cells']:05d}_{h}.json"
                (outdir / 'candidates' / fname).write_text(json.dumps(cand, indent=2, sort_keys=True) + '\n')
                if args.found_mode != 'none':
                    emit('FOUND', f'#{len(found):03d} {op} cells={ev["cells"]} step={ev["terminal_step"]}')
                    emit('FOUND', f'hash={h} state={state_hash}')
                    if args.found_mode == 'full':
                        emit('FOUND', f'parents={",".join(parents_ids)}')
                        emit('FOUND', f'file=candidates/{fname}')
        if args.progress_every and index % args.progress_every == 0:
            emit('PROGRESS', f'{op} t={index} cells={ev["cells"]} status={status}')
            emit('PROGRESS', f'unknown={ev["unknown"]} births={ev["terminal_births"]}')
            emit('PROGRESS', f'state_new={is_new_state} found={len(found)}')
            emit('PROGRESS', f'best={best["cells"]} best_op={best["operator"]}')
            emit('PROGRESS', f'best_closed={best_closed["cells"]}')

    def run_block(op: str, count: int) -> None:
        emit('METHOD', f'{op} start trials={count}')
        for i in range(1, count + 1):
            if (args.stop_after_max_found
                    and len(found) >= args.max_found
                    and i > args.min_trials_before_stop):
                emit('METHOD', f'{op} stop: reached target={args.max_found}')
                emit('METHOD', f'{op} min_trials={args.min_trials_before_stop}')
                break
            if op == 'MUTATE':
                p = choose_parent(rng, parents)
                acc, rej, meta = mutate_candidate(rng, p, stats, args.max_edits)
                parents_ids = [short_parent_id(p)]
            elif op == 'MATE':
                a, b = choose_pair(rng, parents)
                acc, rej, meta = mate_candidate(rng, a, b, stats, args.max_edits)
                parents_ids = [short_parent_id(a), short_parent_id(b)]
            elif op == 'ADOPT_UP':
                a, b = choose_pair_from_pool(rng, unequal_pair_pool, parents)
                acc, rej, meta = adopt_candidate(rng, a, b, stats, 'UP')
                parents_ids = meta.get('axis', [short_parent_id(a), short_parent_id(b)])
            elif op == 'ADOPT_DOWN':
                a, b = choose_pair_from_pool(rng, unequal_pair_pool, parents)
                acc, rej, meta = adopt_candidate(rng, a, b, stats, 'DOWN')
                parents_ids = meta.get('axis', [short_parent_id(a), short_parent_id(b)])
            elif op == 'ADOPT_EQUAL':
                a, b = choose_pair_from_pool(rng, equal_pair_pool, parents)
                acc, rej, meta = adopt_candidate(rng, a, b, stats, 'EQUAL')
                parents_ids = meta.get('axis', [short_parent_id(a), short_parent_id(b)])
            else:
                raise ValueError(op)
            store_trial(op, acc, rej, parents_ids, meta, i)
        emit('METHOD', f'{op} done trials={operator_counts[op]}')
        emit('METHOD', f'{op} found={sum(operator_found[op].values())}')

    for op, n in [('MUTATE', args.mutations), ('MATE', args.mates), ('ADOPT_UP', adopt_ups), ('ADOPT_DOWN', adopt_downs), ('ADOPT_EQUAL', args.adopt_equals)]:
        run_block(op, n)

    found_by_cells = collections.Counter(str(r['cells']) for r in found)
    best_by_operator = {}
    for op in ('MUTATE', 'MATE', 'ADOPT_UP', 'ADOPT_DOWN', 'ADOPT_EQUAL'):
        op_trials = [x for x in trials if x['operator'] == op]
        if op_trials:
            b = max(op_trials, key=lambda x: (x['cells'], -x['terminal_unknown_frontier']))
            best_by_operator[op] = {
                'cells': b['cells'],
                'status': b['status'],
                'hash': b['hash'],
                'unknown': b['terminal_unknown_frontier'],
                'births': b['terminal_births'],
            }
    summary = {
        'ok': len(found) > 0,
        'purpose': 'mutate / mate / lifetime-oriented adopt-up / adopt-down / adopt-equal DH12 policy search for more same-family closed-chill records',
        'seed': args.seed,
        'loaded_records': len(recs),
        'valid_parent_records': len(parents),
        'keep_min': args.keep_min,
        'max_replay_steps': args.max_replay_steps,
        'max_cells': args.max_cells,
        'prior_universe_keys': len(stats.universe),
        'signpost_genes': len(signposts),
        'adopt_pairs_updown': len(unequal_pair_pool),
        'adopt_pairs_equal': len(equal_pair_pool),
        'operator_trials': dict(operator_counts),
        'trials': len(trials),
        'target_found': args.max_found,
        'stop_after_max_found': bool(args.stop_after_max_found),
        'min_trials_before_stop': args.min_trials_before_stop,
        'all_operator_blocks_entered': True,
        'new_closed_chill_ge_keep_min': len(found),
        'new_distinct_terminal_states_ge_keep_min': sum(1 for r in found if r.get('is_new_terminal_state')),
        'known_terminal_state_candidates': sum(1 for r in found if not r.get('is_new_terminal_state')),
        'known_seed_terminal_states': len(seed_state_hashes),
        'duplicate_rule_skips': dict(duplicate_rule_skips),
        'duplicate_terminal_state_skips': dict(duplicate_state_skips),
        'replay_cache_entries': len(replay_cache),
        'unique_rule_hashes_tried': len(tried_hashes),
        'found_by_cells': dict(found_by_cells),
        'found_by_operator_cells': {op: dict(counter) for op, counter in operator_found.items()},
        'best_new_cells': max([r['cells'] for r in found], default=0),
        'best_trial_seen_even_if_open': best,
        'best_closed_chill_candidate': best_closed,
        'best_by_operator': best_by_operator,
        'candidate_dir': str(outdir / 'candidates'),
        'found_index': [
            {
                'file': f"candidates/candidate_{i+1:04d}_{r['operator']}_{r['cells']:05d}_{r['rule_hash']}.json",
                'hash': r['rule_hash'],
                'state_hash': r.get('state_hash'),
                'is_new_terminal_state': r.get('is_new_terminal_state'),
                'cells': r['cells'],
                'step': r['depth'],
                'operator': r['operator'],
                'parents': r['parents'],
                'used_accept': r['used_accept'],
                'used_reject': r['used_reject'],
                'accept': r['accept'],
                'reject': r['reject'],
            }
            for i, r in enumerate(found)
        ],
        'top_trials': sorted(trials, key=lambda x: (x['cells'], -x['terminal_unknown_frontier']), reverse=True)[:40],
    }
    (outdir / 'policy_search_summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    (outdir / 'policy_search_trials.jsonl').write_text('\n'.join(json.dumps(x, sort_keys=True) for x in trials) + ('\n' if trials else ''))

    emit('SUMMARY', f'ok={summary["ok"]} trials={summary["trials"]}')
    emit('SUMMARY', f'target={summary["target_found"]}')
    emit('SUMMARY', f'found={summary["new_closed_chill_ge_keep_min"]}')
    emit('SUMMARY', f'best_new_cells={summary["best_new_cells"]}')
    emit('SUMMARY', f'found_by_cells={dict(found_by_cells)}')
    emit('SUMMARY', f'operator_trials={dict(operator_counts)}')
    emit('SUMMARY', f'found_by_operator_cells={summary["found_by_operator_cells"]}')
    emit('SUMMARY', f'summary_json={outdir / "policy_search_summary.json"}')
    emit('SUMMARY', f'candidates_dir={outdir / "candidates"}')
    return 0 if summary['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
