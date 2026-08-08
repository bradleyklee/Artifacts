#!/usr/bin/env python3
"""Reconstruct the dense Q2 quartic order-6 operator from modular period data.

This is deliberately resumable. Each accepted prime contributes a normalized
null vector for the (order, degree)=(6,31) ODE ansatz. The vectors are combined
by CRT and rational reconstruction is attempted after every accepted prime.
Every prime is independently checked on held-out series equations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from fractions import Fraction
from math import gcd, isqrt
from pathlib import Path

import numpy as np
import sympy as sp

R = 6
D = 31
NCOLS = (R + 1) * (D + 1)


def load_modules(src: Path):
    sys.path.insert(0, str(src))
    from general_quartic_series_mod import series  # type: ignore
    from modular_ode_screen_numpy import matrix  # type: ignore
    from reconstruct_operator_modular import null_vector_mod  # type: ignore
    return series, matrix, null_vector_mod


def crt_pair(a: int, m: int, b: int, p: int) -> int:
    return a + m * (((b - a) % p) * pow(m % p, -1, p) % p)


def ratrec(a: int, m: int) -> Fraction | None:
    """Classical rational reconstruction with |num|, den <= sqrt(m/2)."""
    a %= m
    if a == 0:
        return Fraction(0)
    bound = isqrt(m // 2)
    r0, r1 = m, a
    s0, s1 = 0, 1
    while abs(r1) > bound:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
    if s1 == 0:
        return None
    num, den = r1, s1
    if den < 0:
        num, den = -num, -den
    g = gcd(abs(num), den)
    num //= g
    den //= g
    if abs(num) > bound or den > bound or (a * den - num) % m:
        return None
    return Fraction(num, den)


def falling(n: int, j: int, p: int) -> int:
    z = 1
    for k in range(j):
        z = z * (n - k) % p
    return z


def verify_mod(seq: list[int], vec: list[int], p: int, start: int = 0) -> tuple[bool, int | None, int | None]:
    for n in range(start, len(seq) - R):
        z = 0
        t = 0
        for j in range(R + 1):
            for e in range(D + 1):
                c = vec[t] % p
                t += 1
                k = n - e + j
                if c and n >= e and k >= j and 0 <= k < len(seq):
                    z = (z + c * falling(k, j, p) * seq[k]) % p
        if z:
            return False, n, z
    return True, None, None


def prime_stream(start: int):
    p = start + 1
    while True:
        p = int(sp.prevprime(p))
        if p > 1100 and p % 4 == 1 and p not in (2, 3, 5):
            yield p


def read_checkpoint(path: Path) -> dict:
    if not path.exists():
        return {
            "format": 1,
            "order": R,
            "degree": D,
            "normalization_column": NCOLS - 1,
            "primes": [],
            "modulus": "1",
            "residues": None,
            "records": [],
        }
    d = json.loads(path.read_text())
    if d["order"] != R or d["degree"] != D:
        raise ValueError("checkpoint ansatz mismatch")
    return d


def atomic_write(path: Path, data: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    tmp.replace(path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, type=Path)
    ap.add_argument("--src", required=True, type=Path)
    ap.add_argument("--checkpoint", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--target-primes", type=int, default=30)
    ap.add_argument("--terms", type=int, default=340)
    ap.add_argument("--train", type=int, default=260)
    ap.add_argument("--prime-start", type=int, default=65521)
    ap.add_argument("--series-cache", type=Path)
    ns = ap.parse_args()

    if ns.train <= NCOLS + R:
        raise ValueError("training length leaves too little overdetermination")
    if ns.terms <= ns.train:
        raise ValueError("held-out terms required")

    series_fn, matrix_fn, null_vector_mod = load_modules(ns.src)
    model = json.loads(ns.model.read_text())
    spec = model["monomials"]
    state = read_checkpoint(ns.checkpoint)
    primes_done = set(int(x) for x in state["primes"])
    modulus = int(state["modulus"])
    residues = state["residues"]
    if residues is not None:
        residues = [int(x) for x in residues]
    free_expected = int(state["normalization_column"])

    cache_dir = ns.series_cache
    if cache_dir:
        cache_dir.mkdir(parents=True, exist_ok=True)

    stream = prime_stream(ns.prime_start)
    while len(state["primes"]) < ns.target_primes:
        p = next(stream)
        if p in primes_done:
            continue
        t0 = time.time()
        cache_path = cache_dir / f"q2_series_mod_{p}_{ns.terms}.json" if cache_dir else None
        if cache_path and cache_path.exists():
            seq = [int(x) for x in json.loads(cache_path.read_text())["terms"]]
            series_seconds = 0.0
            series_source = "cache"
        else:
            ts = time.time()
            seq = [int(x) for x in series_fn(spec, ns.terms, p)]
            series_seconds = time.time() - ts
            series_source = "computed"
            if cache_path:
                cache_path.write_text(json.dumps({
                    "example_id": model["example_id"], "prime": p,
                    "terms": seq, "seconds": series_seconds,
                }, indent=2) + "\n")

        tm = time.time()
        A = matrix_fn(seq, R, D, p, ns.train)
        vec, free = null_vector_mod(A, p)
        null_seconds = time.time() - tm
        if free != free_expected:
            print(json.dumps({"prime": p, "status": "SKIP_FREE_COLUMN", "free": free}), flush=True)
            continue
        ok = verify_mod(seq, vec, p, start=ns.train - R)
        if not ok[0]:
            raise RuntimeError(("heldout failure", p, ok))

        if residues is None:
            residues = [int(x) for x in vec]
            modulus = p
        else:
            residues = [crt_pair(a, modulus, int(b), p) for a, b in zip(residues, vec)]
            modulus *= p
        primes_done.add(p)
        state["primes"].append(p)
        state["modulus"] = str(modulus)
        state["residues"] = [str(x) for x in residues]

        reconstructed = [ratrec(x, modulus) for x in residues]
        solved_count = sum(x is not None for x in reconstructed)
        max_num_digits = max((len(str(abs(x.numerator))) for x in reconstructed if x is not None), default=0)
        max_den_digits = max((len(str(x.denominator)) for x in reconstructed if x is not None), default=0)
        rec = {
            "prime_index": len(state["primes"]),
            "prime": p,
            "series_source": series_source,
            "series_seconds": series_seconds,
            "nullspace_seconds": null_seconds,
            "total_seconds": time.time() - t0,
            "free_column": free,
            "heldout_equations": ns.terms - ns.train,
            "heldout_pass": True,
            "modulus_digits": len(str(modulus)),
            "reconstructed_coefficients": solved_count,
            "coefficient_count": NCOLS,
            "max_reconstructed_numerator_digits": max_num_digits,
            "max_reconstructed_denominator_digits": max_den_digits,
        }
        state["records"].append(rec)
        atomic_write(ns.checkpoint, state)
        print(json.dumps(rec), flush=True)

        if solved_count == NCOLS:
            coeffs = [str(x) for x in reconstructed]
            digest = hashlib.sha256(("\n".join(coeffs) + "\n").encode()).hexdigest()
            out = {
                "example_id": model["example_id"],
                "status": "EXACT_OPERATOR_RECONSTRUCTED_FROM_MODULAR_SERIES",
                "order": R,
                "degree": D,
                "coefficient_layout": "j-major, alpha exponent e=0..31",
                "normalization": {"column": free_expected, "value": "1"},
                "coefficients_flat": coeffs,
                "coefficient_sha256": digest,
                "primes": state["primes"],
                "modulus": str(modulus),
                "training_terms": ns.train,
                "heldout_terms_per_prime": ns.terms - ns.train,
                "records": state["records"],
            }
            atomic_write(ns.output, out)
            print("EXACT_OPERATOR_RECONSTRUCTED", digest, flush=True)
            return

    print("TARGET_REACHED_WITHOUT_FULL_RECONSTRUCTION", len(state["primes"]), flush=True)


if __name__ == "__main__":
    main()
