#!/usr/bin/env python3
from functools import cache
from math import gcd

M_BLOCKS = (4, 6, 8, 10)
MAX_N = 100


@cache
def mu(d):
    sign = 1
    p = 2
    while p * p <= d:
        if d % p == 0:
            d //= p
            if d % p == 0:
                return 0
            sign = -sign
        p += 1
    return -sign if d > 1 else sign


def divisors(d):
    return [q for q in range(1, d + 1) if d % q == 0]


# McLarnan 1981, p. 285: C_Nv.
def cycles(m, k, reflection):
    seen = [False] * m
    out = []
    for start in range(m):
        if seen[start]:
            continue
        cycle = []
        i = start
        while not seen[i]:
            seen[i] = True
            cycle.append(i)
            i = (k - i) % m if reflection else (i + k) % m
        out.append(cycle)
    return out


# McLarnan 1981, p. 285: registry mod 3.
def fixed(m, n, k, reflection):
    dp = [[0, 0, 0] for _ in range(n + 1)]
    dp[0][0] = 1
    for cycle in cycles(m, k, reflection):
        length = len(cycle)
        even_slots = sum(i % 2 for i in cycle)
        nxt = [[0, 0, 0] for _ in range(n + 1)]
        for total in range(n + 1):
            for residue, count in enumerate(dp[total]):
                for value in range((n - total) // length + 1):
                    nxt[total + length * value][
                        (residue + even_slots * value) % 3
                    ] += count
        dp = nxt
    return dp[n][(-n) % 3]


# Burnside average.
@cache
def f_prime(m, n):
    total = 0
    for k in range(m):
        total += fixed(m, n, k, False)
        total += fixed(m, n, k, True)
    assert total % (2 * m) == 0
    return total // (2 * m)


# McLarnan 1981, p. 286: exact layer number.
@cache
def f(m, n):
    return sum(
        mu(d) * f_prime(m // d, n // d)
        for d in divisors(gcd(m // 2, n))
    )


def a(m, n):
    return f(m, n)


if __name__ == '__main__':
    for m in M_BLOCKS:
        print(f'm={m}; n=1..{MAX_N}: ' +
              ','.join(str(a(m, n)) for n in range(1, MAX_N + 1)))
