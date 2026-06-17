#!/usr/bin/env python3
# Golden Hex Tree minimal working example.
# Prints a_t=(N_t-1)/6 or its first differences from the REPHEX rules.

from collections import defaultdict
import sys

DIRECTIONS = [(-1,0), (0,-1), (1,-1), (1,0), (0,1), (-1,1)]

def add(a,b): return (a[0]+b[0], a[1]+b[1])
def d(i): return DIRECTIONS[i % 6]
def m(i): return i % 6

def phi_token(t):
    s,i = t[0], m(t[1])
    if s == 'D': return [('D',i), ('K',i)]
    if s in 'KH': return [('D',i), ('K',i), ('H',i)]
    if s == 'a': return [('D',i-2), ('a',i), ('H',i)]
    if s == 'b': return [('D',i-1), ('b',i), ('H',i)]
    if s in 'gh': return [(s,i), ('H',i)]
    raise ValueError(s)

def phi_word(w):
    out = []
    for t in w:
        out += [(s,m(i)) for s,i in phi_token(t)]
    return tuple(out)

def child(root, kind, ori, off=(), cap=0):
    return (kind, m(ori), root + tuple((s,m(i)) for s,i in off), cap)

def inflate_tile(tile):
    kind,i,w,cap = tile
    i, root = m(i), phi_word(w)

    if kind == 'F':
        return [('F',0,root,0)] + [child(root,'B',j,(('g',j),)) for j in range(6)]

    if kind == 'D':
        return [
            child(root,'D',i),
            child(root,'D',i,(('D',i),('K',i))),
            child(root,'B',i,(('D',i),('K',i),('D',i),('K',i))),
            child(root,'G',i+2,(('D',i),('a',i+2))),
            child(root,'G',i+1,(('D',i),('b',i+1))),
            child(root,'B',i+2,(('D',i),('K',i),('D',i),('a',i+2))),
            child(root,'B',i+1,(('D',i),('K',i),('D',i),('b',i+1))),
            child(root,'B',i-1,(('g',i-1),)),
            child(root,'B',i-2,(('h',i-2),)),
            child(root,'G',i-1,(('D',i),('K',i),('g',i-1))),
            child(root,'G',i-2,(('D',i),('K',i),('h',i-2))),
        ]

    # B is a through-branch carrier; G is a leaf.  The axial child is a cap
    # precisely when it comes from a G parent or from an existing cap.
    axis_cap = int(kind == 'G' or cap)
    return [
        child(root,'D',i),
        child(root,'B',i,(('D',i),('K',i)),axis_cap),
        child(root,'G',i+2,(('D',i),('a',i+2))),
        child(root,'G',i+1,(('D',i),('b',i+1))),
        child(root,'G',i-1,(('g',i-1),)),
        child(root,'G',i-2,(('h',i-2),)),
    ]

def inflate(patch):
    seen = {}
    for tile in patch:
        for t in inflate_tile(tile):
            key = t[:3]
            if key in seen and seen[key][3] != t[3]:
                raise RuntimeError('cap conflict')
            seen.setdefault(key, t)
    return sorted(seen.values())

def cell(word):
    q = r = 0
    for _,i in word:
        q,r = add((q,r), d(i))
    return (q,r)

def on_cells(level):
    patch = [('F',0,(),0)]
    for _ in range(level):
        patch = inflate(patch)

    on = set()
    for kind,i,w,cap in patch:
        c = cell(w)
        if kind == 'F':
            on.add(c)
        elif kind == 'D':
            on.add(c); on.add(add(c,d(i)))
        elif kind == 'B' and not cap:
            on.add(c)
    return on

def arrival_times(on):
    time = {(0,0): 0}
    front = defaultdict(set)

    for h,v in enumerate(DIRECTIONS):
        nb = add((0,0), v)
        if nb in on:
            front[1].add((nb,h))
            time.setdefault(nb, 1)

    seen = set(front[1])
    t = 1
    while front[t]:
        nxt = set()
        for c,h in front[t]:
            targets = [(add(c,d(h)), h)]
            for s in (-1,1):
                h1,h2 = m(h+s), m(h+2*s)
                c1,c2 = add(c,d(h1)), add(c,d(h2))
                if c1 in on and c2 in on:
                    targets += [(c1,h1), (c2,h2)]

            for c2,h2 in targets:
                if c2 in on and (c2,h2) not in seen:
                    seen.add((c2,h2))
                    nxt.add((c2,h2))
                    time.setdefault(c2, t+1)
        t += 1
        front[t] = nxt

    if set(time) != on:
        raise RuntimeError('not all ON cells were reached')
    return time

def sequence(level):
    times = arrival_times(on_cells(level))
    births = [0] * (max(times.values()) + 1)
    for t in times.values():
        births[t] += 1
    total, a = 0, []
    for b in births:
        total += b
        a.append((total - 1) // 6)
    return a

def main():
    command = sys.argv[1] if len(sys.argv) > 1 else 'sequence'
    level = int(sys.argv[2]) if len(sys.argv) > 2 else 6

    a = sequence(level)
    if command == 'sequence':
        print(', '.join(map(str,a)))
    elif command == 'differences':
        diffs = ['—'] + [str(a[i]-a[i-1]) for i in range(1,len(a))]
        print(', '.join(diffs))
    else:
        raise SystemExit('usage: golden_hex.py [sequence|differences] [level]')

if __name__ == '__main__':
    main()
