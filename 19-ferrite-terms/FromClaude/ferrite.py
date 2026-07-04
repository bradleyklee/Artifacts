import math
from math import comb
from functools import lru_cache

def divisors(n):
    return [d for d in range(1, n+1) if n % d == 0]

@lru_cache(maxsize=None)
def mobius(n):
    if n == 1:
        return 1
    result = 1
    nn = n
    p = 2
    while p*p <= nn:
        if nn % p == 0:
            nn //= p
            if nn % p == 0:
                return 0
            result = -result
        p += 1
    if nn > 1:
        result = -result
    return result

def group_elements(N):
    """Return all 2N permutations of C_Nv acting on labels 1..N as dicts {i: pi(i)}."""
    elems = []
    for k in range(N):
        perm = {}
        for i in range(1, N+1):
            perm[i] = ((i-1+k) % N) + 1
        elems.append(perm)
    for k in range(N):
        perm = {}
        for i in range(1, N+1):
            perm[i] = ((k - (i-1)) % N) + 1
        elems.append(perm)
    return elems

def cycles_of(perm, N):
    seen = set()
    cycles = []
    for start in range(1, N+1):
        if start in seen:
            continue
        cyc = []
        j = start
        while j not in seen:
            seen.add(j)
            cyc.append(j)
            j = perm[j]
        cycles.append(cyc)
    return cycles

def fix_count(cycles, S):
    """Number of assignments v_c>=0 per cycle with sum(L_c*v_c)=S and evensum = r0 (mod3)
       where r0 = (-S) mod 3, evensum = sum(e_c*v_c)."""
    r0 = (-S) % 3
    dp = [[0]*3 for _ in range(S+1)]
    dp[0][0] = 1
    for cyc in cycles:
        L = len(cyc)
        e = sum(1 for pos in cyc if pos % 2 == 0)
        new_dp = [[0]*3 for _ in range(S+1)]
        for s in range(S+1):
            for r in range(3):
                c = dp[s][r]
                if c == 0:
                    continue
                v = 0
                while s + L*v <= S:
                    rr = (r + e*v) % 3
                    new_dp[s+L*v][rr] += c
                    v += 1
        dp = new_dp
    return dp[S][r0]

_fp_cache = {}
def F_prime(N, S):
    """Burnside count: C_Nv orbits of (v_1..v_N), sum=S, satisfying registry -> layer-number DIVIDES 5N+6S."""
    if S < 0:
        return 0
    key = (N,S)
    if key in _fp_cache:
        return _fp_cache[key]
    elems = group_elements(N)
    total = 0
    for perm in elems:
        cycs = cycles_of(perm, N)
        total += fix_count(cycs, S)
    assert total % (2*N) == 0, f"Non-integer average at N={N},S={S}: {total}/{2*N}"
    val = total // (2*N)
    _fp_cache[key] = val
    return val

def F(N, S):
    """Mobius inversion over d | gcd(N/2, S): F(N,S) = sum mu(d) F'(N/d, S/d)"""
    half = N // 2
    total = 0
    for d in divisors(half):
        if S % d == 0:
            total += mobius(d) * F_prime(N//d, S//d)
    return total

if __name__ == "__main__":
    table7 = {
1:(0,0,0,0,0),2:(1,1,2,2,3),3:(1,2,3,4,5),4:(1,2,6,10,18),5:(1,3,9,19,38),
6:(2,6,19,44,100),7:(1,6,24,76,198),8:(2,9,46,150,445),9:(2,13,62,251,829),
10:(2,15,96,432,1605),11:(2,18,132,686,2851),12:(3,25,194,1094,5014),
13:(2,27,249,1646,8361),14:(3,34,354,2498,13843),15:(3,42,452,3608,21907),
16:(3,47,600,5206,34362),17:(3,54,762,7301,52327),18:(4,67,986,10160,78571),
19:(3,72,1212,13814,115434),20:(4,84,1544,18718,167695)
    }
    Ns = [2,4,6,8,10]
    all_ok = True
    for S in range(1,21):
        computed = tuple(F(N,S) for N in Ns)
        expected = table7[S]
        ok = computed == expected
        if not ok:
            all_ok = False
        print(S, computed, expected, "OK" if ok else "MISMATCH")
    print("ALL OK" if all_ok else "SOME MISMATCHES")
