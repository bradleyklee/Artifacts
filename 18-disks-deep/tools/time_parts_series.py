#!/usr/bin/env python3
"""Derive complete exact-clock bit telemetry and a display-only plot.

The ledger remains authoritative: this script never changes event selection.
For each T=a+b√2+c√3+d√6 it records numerator and denominator bit lengths of
all four reduced rational coefficients.  The physical-time column is a
256-decimal-digit display approximation only, used solely as a plotting axis.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 256
SQRT2 = Decimal(2).sqrt()
SQRT3 = Decimal(3).sqrt()
SQRT6 = Decimal(6).sqrt()

PARTS = ("a", "b", "c", "d")


def rat_parts(text: str) -> tuple[int, int, int, int, Decimal]:
    if "/" in text:
        n_text, d_text = text.split("/", 1)
        n, d = int(n_text), int(d_text)
    else:
        n, d = int(text), 1
    return n, d, abs(n).bit_length(), d.bit_length(), Decimal(n) / Decimal(d)


def lcm(a: int, b: int) -> int:
    return abs(a // math.gcd(a, b) * b)


def load_rows(paths: list[Path]):
    last_step = -1
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                row = json.loads(line)
                step = int(row["step"])
                if step <= last_step:
                    raise ValueError(f"non-increasing absolute step {step} after {last_step}: {path}")
                last_step = step
                yield row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ledgers", type=Path, nargs="+")
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--png", type=Path)
    args = ap.parse_args()

    rows: list[dict[str, object]] = []
    running_max = 0
    for record in load_rows(args.ledgers):
        exact_t = record["exact_T"]
        vals: dict[str, Decimal] = {}
        rats: dict[str, tuple[int, int]] = {}
        out: dict[str, object] = {"step": record["step"], "event_class": record["event_class"]}
        common_den = 1
        for part in PARTS:
            n, d, nb, db, val = rat_parts(exact_t[part])
            rats[part] = (n, d)
            common_den = lcm(common_den, d)
            out[f"T_{part}_numerator_bits"] = nb
            out[f"T_{part}_denominator_bits"] = db
            vals[part] = val
        # Canonical homogeneous field coordinates: one positive common
        # denominator plus four integer numerators.  This is a second,
        # representation-level complexity observable alongside individually
        # reduced coefficients, not a replacement for exact_T.
        out["T_common_denominator_bits"] = common_den.bit_length()
        for part in PARTS:
            n, d = rats[part]
            out[f"T_common_{part}_numerator_bits"] = abs(n * (common_den // d)).bit_length()
        out["T_common_max_bits"] = max(
            int(out["T_common_denominator_bits"]),
            *(int(out[f"T_common_{p}_numerator_bits"]) for p in PARTS),
        )
        out["T_common_sum_bits"] = int(out["T_common_denominator_bits"]) + sum(
            int(out[f"T_common_{p}_numerator_bits"]) for p in PARTS
        )
        out["T_max_component_bits"] = max(
            int(out[f"T_{p}_{which}_bits"]) for p in PARTS for which in ("numerator", "denominator")
        )
        out["T_sum_component_bits"] = sum(
            int(out[f"T_{p}_{which}_bits"]) for p in PARTS for which in ("numerator", "denominator")
        )
        running_max = max(running_max, int(out["T_max_component_bits"]))
        out["running_T_max_component_bits"] = running_max
        t_display = vals["a"] + vals["b"] * SQRT2 + vals["c"] * SQRT3 + vals["d"] * SQRT6
        out["physical_time_display"] = format(t_display, ".40g")
        rows.append(out)

    if not rows:
        raise SystemExit("empty ledger list")
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    if args.png:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        x = [float(r["physical_time_display"]) for r in rows]
        fig, ax = plt.subplots(figsize=(10, 5.5))
        for part in PARTS:
            nums = [int(r[f"T_{part}_numerator_bits"]) for r in rows]
            # A zero field coefficient is written canonically as 0/1.  Omit
            # it from the display rather than pretending its fixed denominator
            # carries dynamics (D12 has b=d=0 throughout).
            if max(nums) == 0:
                continue
            ax.plot(x, nums, label=f"{part} numerator")
            ax.plot(x, [int(r[f"T_{part}_denominator_bits"]) for r in rows], label=f"{part} denominator", linestyle="--")
        ax.plot(x, [int(r["running_T_max_component_bits"]) for r in rows], label="running maximum", linewidth=2)
        ax.set_xlabel("physical collision time T (display approximation)")
        ax.set_ylabel("reduced rational coefficient bit length")
        ax.set_title("Exact collision-clock component complexity")
        ax.legend(ncol=3, fontsize=8)
        ax.grid(True)
        args.png.parent.mkdir(parents=True, exist_ok=True)
        fig.tight_layout()
        fig.savefig(args.png, dpi=180)
        plt.close(fig)

    print(json.dumps({"rows": len(rows), "first_step": rows[0]["step"], "last_step": rows[-1]["step"], "final_running_bits": rows[-1]["running_T_max_component_bits"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
