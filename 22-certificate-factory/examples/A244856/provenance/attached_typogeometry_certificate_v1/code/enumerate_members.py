#!/usr/bin/env python3
from functools import lru_cache
from itertools import product
import argparse

@lru_cache(None)
def members(n: int) -> tuple[str, ...]:
    if n < 0:
        return ()
    if n == 0:
        return ("0",)

    out: set[str] = set()

    # Terminal.
    if n == 1:
        out.add("1")

    # Costly unary growth.
    for child in members(n - 1):
        if child != "0":
            out.add("{" + child + "}")

    # Free ordered four-slot junction with at least two nonzero children.
    for sizes in product(range(n + 1), repeat=4):
        if sum(sizes) != n:
            continue
        if sum(size > 0 for size in sizes) < 2:
            continue
        choices = [("0",) if size == 0 else members(size) for size in sizes]
        for slots in product(*choices):
            out.add("{" + ",".join(slots) + "}")

    return tuple(sorted(out))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("N", nargs="?", type=int, default=4)
    args = parser.parse_args()
    if args.N > 5:
        raise SystemExit("Refusing N>5: literal member sets grow rapidly.")
    for n in range(args.N + 1):
        ws = members(n)
        print(f"n={n} count={len(ws)}")
        for i, word in enumerate(ws, 1):
            print(f"{i:5d}  {word}")
        print()

if __name__ == "__main__":
    main()
