#!/usr/bin/env python3
import argparse
from functools import lru_cache
from math import gcd


# McLarnan 1981, pp. 285–286

def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


@lru_cache(maxsize=None)
def mobius(n):
    if n == 1:
        return 1
    sign, p, m = 1, 2, n
    while p * p <= m:
        if m % p == 0:
            m //= p
            if m % p == 0:
                return 0
            sign = -sign
        p += 1
    return -sign if m > 1 else sign


# C_Nv on v_1,...,v_N

def cycles(N, k, reflection):
    perm = [(k - i) % N if reflection else (i + k) % N for i in range(N)]
    seen, out = set(), []
    for start in range(N):
        if start in seen:
            continue
        cycle, i = [], start
        while i not in seen:
            seen.add(i)
            cycle.append(i)
            i = perm[i]
        out.append(cycle)
    return out


# fixed tuples; registry mod 3

def fixed_count(cycles_, S):
    dp = [[0, 0, 0] for _ in range(S + 1)]
    dp[0][0] = 1
    for cycle in cycles_:
        length = len(cycle)
        even_slots = sum(i % 2 == 1 for i in cycle)  # paper positions 2,4,...
        nxt = [[0, 0, 0] for _ in range(S + 1)]
        for total in range(S + 1):
            for residue, count in enumerate(dp[total]):
                for value in range((S - total) // length + 1):
                    nxt[total + length * value][(residue + even_slots * value) % 3] += count
        dp = nxt
    return dp[S][(-S) % 3]


@lru_cache(maxsize=None)
def Fprime(N, S):
    if N <= 0 or N % 2 or S < 0:
        raise ValueError("N must be positive and even; S must be nonnegative")
    total = sum(fixed_count(cycles(N, k, reflection), S)
                for reflection in (False, True) for k in range(N))
    assert total % (2 * N) == 0
    return total // (2 * N)


# exact layer number

def F(N, S):
    return sum(mobius(d) * Fprime(N // d, S // d)
               for d in divisors(gcd(N // 2, S)))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", nargs="+", type=int, default=[4, 6, 8, 10])
    p.add_argument("--start-s", type=int, default=21)
    p.add_argument("--end-s", type=int, default=60)
    a = p.parse_args()
    if a.start_s < 1 or a.end_s < a.start_s:
        raise ValueError("require 1 <= start-s <= end-s")
    for N in a.n:
        values = ",".join(str(F(N, S)) for S in range(a.start_s, a.end_s + 1))
        print(f"N={N}; S={a.start_s}..{a.end_s}: {values}")


if __name__ == "__main__":
    main()
