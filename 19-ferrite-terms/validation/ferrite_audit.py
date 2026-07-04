#!/usr/bin/env python3
"""Exact enumerator for the McLarnan M_N Y_S ferrite count.

This file intentionally contains no OEIS data and no copied table values.
The code follows a finite mathematical specification:

  * N is positive and even;
  * v=(v_1,...,v_N) is a weak composition of S;
  * registry closure is sum(v_odd)-sum(v_even) == 0 (mod 3);
  * equivalent symbols form a D_N orbit;
  * exact physical layer number is selected by Mobius inversion over
    shorter *registry-closing* even-M cells.

Two separate Burnside implementations are supplied:
  A. generic permutations -> cycle decomposition -> exact DP;
  B. closed dihedral cycle signatures -> a different exact DP.

They agree in the built-in audit without reference data.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
from itertools import combinations
from math import gcd, isqrt
from typing import Iterable, Iterator, Sequence


# ---------- elementary arithmetic ----------

def _require_even_N(N: int) -> None:
    if N <= 0 or N % 2:
        raise ValueError("N must be a positive even integer")


def _require_inputs(N: int, S: int) -> None:
    _require_even_N(N)
    if S < 0:
        raise ValueError("S must be nonnegative")


def divisors(n: int) -> tuple[int, ...]:
    """Positive divisors, increasing."""
    if n <= 0:
        raise ValueError("divisors requires n > 0")
    low: list[int] = []
    high: list[int] = []
    for d in range(1, isqrt(n) + 1):
        if n % d == 0:
            low.append(d)
            if d * d != n:
                high.append(n // d)
    return tuple(low + high[::-1])


@lru_cache(maxsize=None)
def mobius(n: int) -> int:
    """Classical Moebius function mu(n), by exact trial factorization."""
    if n <= 0:
        raise ValueError("mobius requires n > 0")
    remaining = n
    number_of_prime_factors = 0
    p = 2
    while p * p <= remaining:
        if remaining % p == 0:
            remaining //= p
            if remaining % p == 0:
                return 0
            number_of_prime_factors += 1
            while remaining % p == 0:
                remaining //= p
        p = 3 if p == 2 else p + 2
    if remaining > 1:
        number_of_prime_factors += 1
    return -1 if number_of_prime_factors % 2 else 1


# ---------- literal objects and the registry law ----------

def weak_compositions(total: int, parts: int) -> Iterator[tuple[int, ...]]:
    """All ordered weak compositions of ``total`` into exactly ``parts`` parts."""
    if total < 0 or parts <= 0:
        return
    for bars in combinations(range(total + parts - 1), parts - 1):
        cuts = (-1,) + bars + (total + parts - 1,)
        yield tuple(cuts[j + 1] - cuts[j] - 1 for j in range(parts))


def registry_balance(v: Sequence[int]) -> int:
    """v_1-v_2+v_3-... in paper indexing."""
    return sum(v[0::2]) - sum(v[1::2])


def registry_valid(v: Sequence[int]) -> bool:
    return registry_balance(v) % 3 == 0


def hagg_displacement_literal(v: Sequence[int]) -> int:
    """Expand M=(1,1,3), Y=(1,1,1,3) literally and sum signed runs.

    Each Zhdanov run flips the sign phase.  For even N this phase closes
    after the full word.  The result is the Hagg displacement of the cyclic
    M Y^v1 M Y^v2 ... M Y^vN word.
    """
    if len(v) % 2:
        raise ValueError("the ferrite model requires even N")
    phase = 1
    displacement = 0
    for y_count in v:
        for run in (1, 1, 3):
            displacement += phase * run
            phase = -phase
        for _ in range(y_count):
            for run in (1, 1, 1, 3):
                displacement += phase * run
                phase = -phase
    if phase != 1:
        raise AssertionError("an even-M word did not restore its sign phase")
    return displacement


# ---------- D_N implementation A: literal permutations ----------

def _cycles_of(perm: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    seen = [False] * len(perm)
    answer: list[tuple[int, ...]] = []
    for start in range(len(perm)):
        if seen[start]:
            continue
        cycle: list[int] = []
        i = start
        while not seen[i]:
            seen[i] = True
            cycle.append(i)
            i = perm[i]
        answer.append(tuple(cycle))
    return tuple(answer)


@lru_cache(maxsize=None)
def dihedral_permutations(N: int) -> tuple[tuple[int, ...], ...]:
    """r_k(i)=i+k and s_k(i)=k-i, modulo N, in a fixed deterministic order."""
    _require_even_N(N)
    rotations = [tuple((i + k) % N for i in range(N)) for k in range(N)]
    reflections = [tuple((k - i) % N for i in range(N)) for k in range(N)]
    all_permutations = tuple(rotations + reflections)
    # N=2 is a nonfaithful action: the abstract group still has 2N elements,
    # so duplicate permutation images must remain in this Burnside list.
    return all_permutations


@lru_cache(maxsize=None)
def dihedral_cycles(N: int) -> tuple[tuple[tuple[int, ...], ...], ...]:
    return tuple(_cycles_of(perm) for perm in dihedral_permutations(N))


def apply_permutation(v: tuple[int, ...], perm: Sequence[int]) -> tuple[int, ...]:
    """Tuple action compatible with the fixed-point condition v_i=v_perm(i)."""
    return tuple(v[perm[i]] for i in range(len(v)))


def fixed_valid_from_cycles(S: int, cycles: Sequence[Sequence[int]]) -> int:
    """Exact count of registry-valid fixed tuples for one permutation.

    A cycle C receives one nonnegative value x.  It contributes |C|x to the
    total Y-count and (number of odd paper positions - number of even paper
    positions)*x to the registry balance.  This is a direct finite DP over
    total and balance modulo 3.
    """
    dp = [[0, 0, 0] for _ in range(S + 1)]
    dp[0][0] = 1
    for cycle in cycles:
        a = len(cycle)
        b = sum(1 if i % 2 == 0 else -1 for i in cycle) % 3
        next_dp = [[0, 0, 0] for _ in range(S + 1)]
        for total, row in enumerate(dp):
            for residue, count in enumerate(row):
                if not count:
                    continue
                for x in range((S - total) // a + 1):
                    next_dp[total + a * x][(residue + b * x) % 3] += count
        dp = next_dp
    return dp[S][0]


@lru_cache(maxsize=None)
def Fprime_generic(N: int, S: int) -> int:
    """Number of D_N-orbits with layer-number dividing 5N+6S (Burnside A)."""
    _require_inputs(N, S)
    fixed_sum = sum(fixed_valid_from_cycles(S, cycles) for cycles in dihedral_cycles(N))
    if fixed_sum % (2 * N):
        raise AssertionError("Burnside numerator is not divisible by |D_N|")
    return fixed_sum // (2 * N)


# ---------- D_N implementation B: direct dihedral cycle signatures ----------
# A signature entry (multiplicity, a, b) means that ``multiplicity`` cycle
# variables each contribute a*x to S and b*x to the signed balance.

def _clean_signature(entries: Iterable[tuple[int, int, int]]) -> tuple[tuple[int, int, int], ...]:
    return tuple((m, a, b % 3) for m, a, b in entries if m)


def rotation_signature(N: int, k: int) -> tuple[tuple[int, int, int], ...]:
    """Cycle signature of i -> i+k (mod N), derived without permutations."""
    _require_even_N(N)
    k %= N
    g = gcd(N, k)
    cycle_length = N // g
    if k % 2:
        # k odd implies the members of every cycle alternate parity.
        return ((g, cycle_length, 0),)
    # k even preserves parity.  The g cycles split equally by parity.
    return _clean_signature(((g // 2, cycle_length, cycle_length),
                             (g // 2, cycle_length, -cycle_length)))


def reflection_signature(N: int, k: int) -> tuple[tuple[int, int, int], ...]:
    """Cycle signature of i -> k-i (mod N), derived by reflection geometry."""
    _require_even_N(N)
    k %= N
    if k % 2:
        # No fixed positions; every transposition pairs one odd and one even slot.
        return ((N // 2, 2, 0),)
    if N % 4 == 2:
        # Two fixed points of opposite parity; remaining pairs preserve parity.
        pairs_per_parity = (N - 2) // 4
        return _clean_signature(((1, 1, 1), (1, 1, -1),
                                 (pairs_per_parity, 2, 2),
                                 (pairs_per_parity, 2, -2)))
    # N is divisible by four.  The two fixed points have the same parity.
    fixed_sign = 1 if (k // 2) % 2 == 0 else -1
    quarter = N // 4
    return _clean_signature(((2, 1, fixed_sign),
                             (quarter - 1, 2, 2 * fixed_sign),
                             (quarter, 2, -2 * fixed_sign)))


def fixed_valid_from_signature(S: int, signature: Sequence[tuple[int, int, int]]) -> int:
    """Independent exact coefficient computation from a cycle signature.

    This intentionally does not use permutations or cycle walks.  It computes
    the coefficient selected by the three residue classes of the formal
    generating function product over the signature variables.
    """
    coefficients = [[0, 0, 0] for _ in range(S + 1)]
    coefficients[0][0] = 1
    for multiplicity, a, b in signature:
        for _ in range(multiplicity):
            next_coefficients = [[0, 0, 0] for _ in range(S + 1)]
            for total, row in enumerate(coefficients):
                for residue, count in enumerate(row):
                    if count:
                        for x in range((S - total) // a + 1):
                            next_coefficients[total + a * x][(residue + b * x) % 3] += count
            coefficients = next_coefficients
    return coefficients[S][0]


@lru_cache(maxsize=None)
def Fprime_signature(N: int, S: int) -> int:
    """Same mathematical count as Fprime_generic, via signatures (Burnside B)."""
    _require_inputs(N, S)
    fixed_sum = 0
    for k in range(N):
        fixed_sum += fixed_valid_from_signature(S, rotation_signature(N, k))
    for k in range(N):
        fixed_sum += fixed_valid_from_signature(S, reflection_signature(N, k))
    if fixed_sum % (2 * N):
        raise AssertionError("signature Burnside numerator is not divisible by |D_N|")
    return fixed_sum // (2 * N)


# ---------- exact physical layer number ----------

def repetition_divisors(N: int, S: int) -> tuple[int, ...]:
    """Allowed multipliers d for a smaller cell with an even M-count.

    A d-fold repetition can reduce the physical layer number only if the base
    has N/d even M blocks and S/d Y blocks, hence d divides gcd(N/2,S).
    Whether the base actually reduces the layer number additionally depends on
    registry closure; that is encoded in Fprime(N/d,S/d).
    """
    _require_inputs(N, S)
    return divisors(gcd(N // 2, S))


@lru_cache(maxsize=None)
def F_generic(N: int, S: int) -> int:
    """Exact-layer-number count, using Moebius inversion over valid subcells."""
    _require_inputs(N, S)
    return sum(mobius(d) * Fprime_generic(N // d, S // d)
               for d in repetition_divisors(N, S))


@lru_cache(maxsize=None)
def F_signature(N: int, S: int) -> int:
    """Exact-layer-number count based wholly on the signature Burnside engine."""
    _require_inputs(N, S)
    return sum(mobius(d) * Fprime_signature(N // d, S // d)
               for d in repetition_divisors(N, S))


# ---------- literal checks for small finite domains ----------

def rotate(v: tuple[int, ...], k: int) -> tuple[int, ...]:
    k %= len(v)
    return v[k:] + v[:k]


def dihedral_canonical(v: tuple[int, ...]) -> tuple[int, ...]:
    reflected = v[::-1]
    return min(*(rotate(v, k) for k in range(len(v))),
               *(rotate(reflected, k) for k in range(len(v))))


def Fprime_literal(N: int, S: int) -> int:
    """Direct enumerate -> registry filter -> literal D_N quotient.  Test only."""
    _require_inputs(N, S)
    return len({dihedral_canonical(v)
                for v in weak_compositions(S, N)
                if registry_valid(v)})


def has_shorter_physical_cell(v: tuple[int, ...]) -> bool:
    """True iff v repeats a smaller even-M cell whose own registry closes.

    A repeated ferrite tuple need not have a shorter *physical* layer number:
    its shorter tuple may have registry displacement +/-1 modulo 3 and become
    registry-closing only after three copies.  This distinction is why a raw
    string-period test is not the correct primitivity criterion.
    """
    N, S = len(v), sum(v)
    for d in repetition_divisors(N, S):
        if d == 1:
            continue
        m = N // d
        base = v[:m]
        if v == base * d and registry_valid(base):
            return True
    return False


def F_literal_exact(N: int, S: int) -> int:
    """Direct exact physical-cell count; used only as a small-domain oracle."""
    representatives = {dihedral_canonical(v)
                       for v in weak_compositions(S, N)
                       if registry_valid(v)}
    return sum(not has_shorter_physical_cell(v) for v in representatives)


# ---------- audit ----------

def _compose(p: Sequence[int], q: Sequence[int]) -> tuple[int, ...]:
    """p after q."""
    return tuple(p[q[i]] for i in range(len(p)))


def audit(literal_max_N: int = 10, literal_max_S: int = 10,
          signature_max_N: int = 30, signature_max_S: int = 60) -> None:
    """Reference-free proof-to-code audit.  Raises on any failed assertion."""
    if literal_max_N % 2 or signature_max_N % 2:
        raise ValueError("audit N bounds must be even")

    # 1. Literal block expansion proves the compressed registry formula.
    for N in range(2, literal_max_N + 1, 2):
        for S in range(literal_max_S + 1):
            for v in weak_compositions(S, N):
                if hagg_displacement_literal(v) != 2 * registry_balance(v):
                    raise AssertionError(("literal Hagg formula", N, S, v))

    # 2. Verify D_N closure plus generic fixed points against literal fixed tuples.
    for N in range(2, literal_max_N + 1, 2):
        perms = dihedral_permutations(N)
        as_set = set(perms)
        if any(_compose(p, q) not in as_set for p in perms for q in perms):
            raise AssertionError(("D_N not closed", N))
        for S in range(literal_max_S + 1):
            all_tuples = tuple(weak_compositions(S, N))
            for perm, cycles in zip(perms, dihedral_cycles(N)):
                literal_fixed = sum(registry_valid(v) and apply_permutation(v, perm) == v
                                    for v in all_tuples)
                dp_fixed = fixed_valid_from_cycles(S, cycles)
                if literal_fixed != dp_fixed:
                    raise AssertionError(("individual fixed-point mismatch", N, S, perm,
                                          literal_fixed, dp_fixed))

    # 3. Direct orbit formation agrees with generic Burnside; direct physical
    #    primitivity agrees with Moebius inversion on a tractable grid.
    for N in range(2, literal_max_N + 1, 2):
        for S in range(1, literal_max_S + 1):
            if Fprime_literal(N, S) != Fprime_generic(N, S):
                raise AssertionError(("literal orbit/Burnside mismatch", N, S))
            if F_literal_exact(N, S) != F_generic(N, S):
                raise AssertionError(("literal exact/Moebius mismatch", N, S,
                                      F_literal_exact(N, S), F_generic(N, S)))

    # 4. Separate formula-level dihedral engine agrees far above direct-enumeration range.
    for N in range(2, signature_max_N + 1, 2):
        for S in range(signature_max_S + 1):
            a = Fprime_generic(N, S)
            b = Fprime_signature(N, S)
            if a != b:
                raise AssertionError(("generic/signature Fprime mismatch", N, S, a, b))
            a_exact = F_generic(N, S)
            b_exact = F_signature(N, S)
            if a_exact != b_exact or a_exact < 0:
                raise AssertionError(("generic/signature exact mismatch", N, S,
                                      a_exact, b_exact))

    # 5. Inversion recomposes Fprime exactly, independent of how F was obtained.
    for N in range(2, signature_max_N + 1, 2):
        for S in range(1, signature_max_S + 1):
            reconstruction = sum(F_generic(N // d, S // d)
                                 for d in repetition_divisors(N, S))
            if reconstruction != Fprime_generic(N, S):
                raise AssertionError(("Moebius reconstruction mismatch", N, S,
                                      reconstruction, Fprime_generic(N, S)))


def terms(N_values: Iterable[int], start_S: int, end_S: int,
          method: str = "generic") -> str:
    if start_S < 1 or end_S < start_S:
        raise ValueError("require 1 <= start_S <= end_S")
    engine = {"generic": F_generic, "signature": F_signature}[method]
    rows = []
    for N in N_values:
        _require_even_N(N)
        values = ",".join(str(engine(N, S)) for S in range(start_S, end_S + 1))
        rows.append(f"N={N}; S={start_S}..{end_S}: {values}")
    return "\n".join(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="exact M_N Y_S ferrite enumerator")
    parser.add_argument("--audit", action="store_true", help="run the reference-free audit")
    parser.add_argument("--start-s", type=int, default=1)
    parser.add_argument("--end-s", type=int, default=60)
    parser.add_argument("--n", nargs="+", type=int, default=[4, 6, 8, 10])
    parser.add_argument("--method", choices=["generic", "signature"], default="generic")
    parser.add_argument("--literal-max-n", type=int, default=10)
    parser.add_argument("--literal-max-s", type=int, default=10)
    parser.add_argument("--signature-max-n", type=int, default=30)
    parser.add_argument("--signature-max-s", type=int, default=60)
    args = parser.parse_args()
    if args.audit:
        audit(args.literal_max_n, args.literal_max_s,
              args.signature_max_n, args.signature_max_s)
        print("audit: PASS")
    print(terms(args.n, args.start_s, args.end_s, args.method))


if __name__ == "__main__":
    main()
