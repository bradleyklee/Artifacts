#!/usr/bin/env python3
"""
Independent re-simulation engine for hard-octagon collision certificates.

This does NOT reuse any code from the repo's check_three.py / check_clock.py /
source/check_certificate.py. It re-derives, from the documented geometric
parameters only (cardinal support R=(1+sqrt2)/2, diagonal support D=1+sqrt2/2,
edge_length=1, square container x,y=+-H), the full event-detection physics:

  - For every unordered body pair and every one of the 8 face-normal
    directions, solve exactly (in Q(sqrt2)) for the time at which the
    separating-axis gap along that normal hits zero, then check strict
    tangential edge overlap (rejecting vertex-only / corner contacts).
  - For every body and every one of the 4 cardinal directions, solve exactly
    for the time its cardinal face reaches the container wall.
  - Take the global minimum positive time across ALL candidates; every
    candidate tying that minimum forms the batch.
  - Advance every body freely to that time (p = p0 + v*tau) and apply the
    documented collision law (specular cardinal wall reflection; equal-mass
    elastic normal-exchange for pairs; both-axis flip for simultaneous
    corner double-wall hits).

It then compares, row by row, against the certificate's own ledger: the
claimed event set, the claimed absolute time, and the claimed post-state.
"""
import json, sys
from fractions import Fraction as F
from pathlib import Path

# ---------- exact Q(sqrt2) arithmetic: value = a + b*sqrt(2), a,b in Q ----------

class QS:
    __slots__ = ("a", "b")
    def __init__(self, a, b=0):
        self.a = F(a); self.b = F(b)
    def __add__(self, o):
        o = o if isinstance(o, QS) else QS(o)
        return QS(self.a + o.a, self.b + o.b)
    def __sub__(self, o):
        o = o if isinstance(o, QS) else QS(o)
        return QS(self.a - o.a, self.b - o.b)
    def __neg__(self):
        return QS(-self.a, -self.b)
    def scale(self, r):  # multiply by a plain rational
        r = F(r)
        return QS(self.a * r, self.b * r)
    def div_rational(self, r):  # divide by a nonzero plain rational
        r = F(r)
        return QS(self.a / r, self.b / r)
    def is_zero(self):
        return self.a == 0 and self.b == 0
    def __eq__(self, o):
        return isinstance(o, QS) and self.a == o.a and self.b == o.b
    def sign(self):
        a, b = self.a, self.b
        if b == 0:
            return (a > 0) - (a < 0)
        if a == 0:
            return (b > 0) - (b < 0)
        sa = (a > 0) - (a < 0)
        sb = (b > 0) - (b < 0)
        if sa == sb:
            return sa
        diff = a*a - 2*b*b  # a^2 - 2b^2 ; never 0 since a,b not both 0 and sqrt2 irrational
        sdiff = (diff > 0) - (diff < 0)
        if a > 0:   # b<0 case (opposite signs, a>0)
            return sdiff
        else:       # a<0, b>0 case
            return -sdiff
    def __gt__(self, o):
        return (self - o).sign() > 0
    def __lt__(self, o):
        return (self - o).sign() < 0
    def __repr__(self):
        return f"({self.a}+{self.b}*sqrt2)"

def qs_from_json(d):
    return QS(F(d["a"]), F(d["b"]))

ZERO = QS(0, 0)
SQRT2 = QS(0, 1)
R = QS(F(1,2), F(1,2))        # cardinal support (1+sqrt2)/2
D = QS(1, F(1,2))             # diagonal support 1+sqrt2/2
TWO_R = QS(1, 1)               # 2R = 1+sqrt2
TWO_D = QS(2, 1)               # 2D = 2+sqrt2
EDGE_THRESH = QS(1, 0)         # cardinal tangential strict-overlap threshold = edge_length
DIAG_THRESH = QS(0, 1)         # diagonal tangential strict-overlap threshold = edge_length*sqrt2

DIRS = {
    "E": (1, 0), "N": (0, 1), "W": (-1, 0), "S": (0, -1),
    "NE": (1, 1), "NW": (-1, 1), "SW": (-1, -1), "SE": (1, -1),
}
CARDINAL = {"E", "N", "W", "S"}

def dotQS(nx, ny, vx, vy):  # nx,ny in {-1,0,1}; vx,vy are QS
    out = ZERO
    if nx == 1: out = out + vx
    elif nx == -1: out = out - vx
    if ny == 1: out = out + vy
    elif ny == -1: out = out - vy
    return out

def dotF(nx, ny, vx, vy):  # vx,vy are Fraction (velocities)
    out = F(0)
    if nx == 1: out += vx
    elif nx == -1: out -= vx
    if ny == 1: out += vy
    elif ny == -1: out -= vy
    return out

# ---------------- state ----------------

class Body:
    __slots__ = ("id", "x", "y", "vx", "vy")
    def __init__(self, id_, x, y, vx, vy):
        self.id = id_; self.x = x; self.y = y; self.vx = vx; self.vy = vy

def load_state_from_json(arr):
    bodies = {}
    for b in arr:
        x = qs_from_json(b["position"]["x"])
        y = qs_from_json(b["position"]["y"])
        vx = F(b["velocity"]["vx"]); vy = F(b["velocity"]["vy"])
        bodies[b["id"]] = Body(b["id"], x, y, vx, vy)
    return bodies

def advance(bodies, tau):
    """Return new dict of bodies advanced freely by tau (QS), velocities unchanged."""
    out = {}
    for bid, b in bodies.items():
        nx = b.x + (QS(0,0).scale(0))  # no-op, keep style consistent
        newx = b.x + QS(b.vx * tau.a, b.vx * tau.b)
        newy = b.y + QS(b.vy * tau.a, b.vy * tau.b)
        out[bid] = Body(bid, newx, newy, b.vx, b.vy)
    return out

def find_candidates(bodies, ids_sorted):
    """Enumerate all valid (kind, label, tau) candidates from the CURRENT state (tau measured from now)."""
    cands = []
    n = len(ids_sorted)
    # pair candidates
    for ii in range(n):
        for jj in range(ii+1, n):
            i, j = ids_sorted[ii], ids_sorted[jj]
            bi, bj = bodies[i], bodies[j]
            dpx = bj.x - bi.x; dpy = bj.y - bi.y
            dvx = bj.vx - bi.vx; dvy = bj.vy - bi.vy
            for label, (nx, ny) in DIRS.items():
                target = TWO_R if label in CARDINAL else TWO_D
                primary_now = dotQS(nx, ny, dpx, dpy)
                denom = dotF(nx, ny, dvx, dvy)
                if denom == 0:
                    continue
                tau = (target - primary_now).div_rational(denom)
                if tau.sign() <= 0:
                    continue
                # tangential coordinate at tau: perp = (-ny, nx)
                dpx_t = dpx + QS(dvx * tau.a, dvx * tau.b)
                dpy_t = dpy + QS(dvy * tau.a, dvy * tau.b)
                u = dotQS(-ny, nx, dpx_t, dpy_t)
                thresh = EDGE_THRESH if label in CARDINAL else DIAG_THRESH
                if not ((thresh - u).sign() > 0 and (thresh + u).sign() > 0):
                    continue  # vertex-only / no real tangential overlap -> reject
                cands.append(("pair", (i, j, label), tau))
    # wall candidates
    for i in ids_sorted:
        b = bodies[i]
        for label, (nx, ny) in DIRS.items():
            if label not in CARDINAL:
                continue
            primary_now = dotQS(nx, ny, b.x, b.y)
            denom = dotF(nx, ny, b.vx, b.vy)
            if denom == 0:
                continue
            target = H - R
            tau = (target - primary_now).div_rational(denom)
            if tau.sign() <= 0:
                continue
            cands.append(("wall", (i, label), tau))
    return cands

def min_tau(cands):
    best = None
    for c in cands:
        t = c[2]
        if best is None or t < best:
            best = t
    return best

def apply_batch(bodies, batch):
    """batch: list of ('pair',(i,j,label),tau) / ('wall',(i,label),tau), all same tau already applied via advance()."""
    new = {bid: Body(bid, b.x, b.y, b.vx, b.vy) for bid, b in bodies.items()}
    wall_hits = {}
    for kind, info, _ in batch:
        if kind == "wall":
            i, label = info
            wall_hits.setdefault(i, []).append(label)
    for i, labels in wall_hits.items():
        b = new[i]
        if len(labels) == 1:
            nx, ny = DIRS[labels[0]]
            if nx != 0:
                b.vx = -b.vx
            if ny != 0:
                b.vy = -b.vy
        elif len(labels) == 2:
            b.vx = -b.vx
            b.vy = -b.vy
        else:
            raise ValueError(f"body {i} hit {len(labels)} walls at once")
    for kind, info, _ in batch:
        if kind == "pair":
            i, j, label = info
            nx, ny = DIRS[label]
            bi, bj = new[i], new[j]
            dvx = bi.vx - bj.vx; dvy = bi.vy - bj.vy
            num = dotF(nx, ny, dvx, dvy)
            n2 = nx*nx + ny*ny
            k = F(num, n2)
            bi.vx -= k*nx; bi.vy -= k*ny
            bj.vx += k*nx; bj.vy += k*ny
    return new

H = None  # set per file

def run_file(path, label_print, max_rows=None):
    global H
    cert = json.loads(Path(path).read_text())
    H = qs_from_json(cert["instance"]["container_half_box"])
    ledger = cert["evolution"]["ledger"]
    bodies = load_state_from_json(cert["instance"]["initial_state"])
    ids_sorted = sorted(bodies.keys())
    t_abs = ZERO
    problems = []
    nrows = len(ledger)
    check_n = min(nrows, max_rows) if max_rows else nrows
    for row in ledger[:check_n]:
        idx = row["index"]
        claimed_time = qs_from_json(row["time"])
        claimed_events = set(row["events"])

        cands = find_candidates(bodies, ids_sorted)
        if not cands:
            problems.append(f"row {idx}: no candidates found at all")
            break
        tau = min_tau(cands)
        batch = [c for c in cands if (c[2] - tau).is_zero()]

        my_time = t_abs + tau
        if not (my_time - claimed_time).is_zero():
            problems.append(f"row {idx}: computed next-event time {my_time} != claimed {claimed_time}")

        my_events = set()
        for kind, info, _ in batch:
            if kind == "pair":
                i, j, lab = info
                my_events.add(f"pair:{i}:{j}:{lab}")
            else:
                i, lab = info
                my_events.add(f"wall:{i}:{lab}")
        if my_events != claimed_events:
            problems.append(f"row {idx}: computed event set {sorted(my_events)} != claimed {sorted(claimed_events)}")

        advanced = advance(bodies, tau)
        newstate = apply_batch(advanced, batch)

        # compare against claimed post
        claimed_post = load_state_from_json(row["post"])
        for bid in ids_sorted:
            mb, cb = newstate[bid], claimed_post[bid]
            if not (mb.x - cb.x).is_zero() or not (mb.y - cb.y).is_zero():
                problems.append(f"row {idx}: body {bid} computed position != claimed post position")
            if mb.vx != cb.vx or mb.vy != cb.vy:
                problems.append(f"row {idx}: body {bid} computed velocity != claimed post velocity")

        bodies = newstate
        t_abs = my_time
        if problems and len(problems) > 5:
            break
    return nrows, problems

if __name__ == "__main__":
    base = Path("/home/claude/work/extracted/15-octagon-collisions/data")
    target = sys.argv[1] if len(sys.argv) > 1 else None
    maxr = int(sys.argv[2]) if len(sys.argv) > 2 else None
    files = []
    if target:
        files = [Path(target)]
    else:
        files = sorted((base/"three-body"/"evolve").glob("*.json"))[:1]
    for f in files:
        nrows, problems = run_file(f, f.stem, maxr)
        print(f"{f}: checked {min(nrows, maxr) if maxr else nrows}/{nrows} rows, {len(problems)} problems")
        for p in problems[:10]:
            print("   ", p)
