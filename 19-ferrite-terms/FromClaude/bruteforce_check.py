import itertools
from ferrite import group_elements, F, F_prime

def compositions(N, S):
    """All tuples of N nonneg ints summing to S (stars and bars, explicit)."""
    if N == 1:
        yield (S,)
        return
    for first in range(S+1):
        for rest in compositions(N-1, S-first):
            yield (first,) + rest

def brute_F_prime(N, S):
    """Directly enumerate all tuples, group into orbits under C_Nv, filter registry, count orbits."""
    elems = group_elements(N)
    seen = set()
    orbit_count = 0
    all_tuples = list(compositions(N, S))
    tupset = set(all_tuples)
    for t in all_tuples:
        if t in seen:
            continue
        # registry check: 3 | (S + sum of even-position (1-indexed) entries)
        evensum = sum(t[i-1] for i in range(1, N+1) if i % 2 == 0)
        if (S + evensum) % 3 != 0:
            seen.add(t)  # mark visited but not counted; still need to mark whole orbit
            continue
        # compute orbit
        orbit = set()
        for perm in elems:
            # perm: position i (1-indexed) -> perm[i]; new tuple: new[perm[i]-1] = t[i-1]
            new = [0]*N
            for i in range(1, N+1):
                new[perm[i]-1] = t[i-1]
            orbit.add(tuple(new))
        seen |= orbit
        orbit_count += 1
    return orbit_count

if __name__ == "__main__":
    print("Brute-force F'(N,S) [orbit count with registry, period dividing N] vs Burnside formula:")
    mismatches = 0
    for N in [2,4,6]:
        for S in range(0, 13):
            bf = brute_F_prime(N, S)
            formula = F_prime(N, S)
            status = "OK" if bf == formula else "MISMATCH"
            if bf != formula:
                mismatches += 1
            print(f"N={N} S={S}: brute={bf} formula={formula} {status}")
    print("ALL MATCH" if mismatches == 0 else f"{mismatches} MISMATCHES")
