#!/usr/bin/env python3
"""Print checksum-checked Artifact 18 quotient-word prefixes.

The displayed residue rows are read from the saved 10,000-term word files.
For d12 mod 3 and all mod-6 views, this tool additionally re-certifies the
complete retained 50,000-event lane, confirms that the saved word is its
10,000-term prefix, and renders a base-10 prefix of the corresponding finite
base-b fraction.  Decimal digits are printed only when the full retained
finite prefix forces them for every possible continuation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from export_words import CertificationError, certify_lane

# Python 3.11 protects against accidental giant integer-to-string conversions.
# These displays intentionally support thousands of precisely certified places.
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

ORDER = (
    ("d12", 6),
    ("d12", 3),
    ("24A", 12),
    ("24A", 6),
    ("24B", 12),
    ("24B", 6),
)
DECIMAL_VIEWS = frozenset({("d12", 3), ("d12", 6), ("24A", 6), ("24B", 6)})


class WordDisplayError(RuntimeError):
    """Raised when saved word files cannot be safely displayed."""


@dataclass(frozen=True)
class WordView:
    lane: str
    modulus: int
    filename: str
    values: tuple[int, ...]
    target_events: int


@dataclass(frozen=True)
class DecimalView:
    lane: str
    modulus: int
    residues: tuple[int, ...]
    saved_terms: int


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_views(root: Path, terms: int) -> list[WordView]:
    words_dir = root / "words"
    manifest_path = words_dir / "WORDS_MANIFEST.json"
    try:
        manifest: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WordDisplayError(f"cannot read {manifest_path}: {exc}") from exc

    try:
        records = {(str(view["lane"]), int(view["modulus"])): view for view in manifest["views"]}
    except (KeyError, TypeError, ValueError) as exc:
        raise WordDisplayError("malformed WORDS_MANIFEST.json") from exc

    missing = [f"{lane} mod {modulus}" for lane, modulus in ORDER if (lane, modulus) not in records]
    if missing:
        raise WordDisplayError(f"manifest missing required views: {', '.join(missing)}")

    views: list[WordView] = []
    for lane, modulus in ORDER:
        record = records[(lane, modulus)]
        try:
            filename = str(record["file"])
            expected_sha = str(record["sha256"])
            declared_terms = int(record["terms"])
            coverage = record["source_recorded_event_coverage"]
            target_events = int(coverage["last"])
            if int(coverage["count"]) != target_events:
                raise ValueError("coverage count/last mismatch")
        except (KeyError, TypeError, ValueError) as exc:
            raise WordDisplayError(f"malformed manifest record for {lane} mod {modulus}") from exc
        if declared_terms < terms:
            raise WordDisplayError(
                f"{filename} declares only {declared_terms} terms; requested {terms}"
            )
        path = words_dir / filename
        try:
            payload = path.read_bytes()
        except OSError as exc:
            raise WordDisplayError(f"cannot read {path}: {exc}") from exc
        if sha256_bytes(payload) != expected_sha:
            raise WordDisplayError(f"saved word checksum mismatch: {path}")
        try:
            text = payload.decode("utf-8")
            if not text.endswith("\n"):
                raise ValueError("missing final newline")
            values = tuple(int(part) for part in text[:-1].split(","))
        except (UnicodeDecodeError, ValueError) as exc:
            raise WordDisplayError(f"malformed comma-separated word: {path}") from exc
        if len(values) != declared_terms:
            raise WordDisplayError(
                f"{filename} has {len(values)} terms; manifest declares {declared_terms}"
            )
        if any(value < 0 or value >= modulus for value in values):
            raise WordDisplayError(f"{filename} has a residue outside 0..{modulus - 1}")
        views.append(WordView(
            lane=lane,
            modulus=modulus,
            filename=filename,
            values=values,
            target_events=target_events,
        ))
    return views


def base_word_as_decimal(values: tuple[int, ...], base: int, places: int) -> str:
    """Return a tail-certified decimal prefix for a finite base-``base`` word.

    A finite base-b word determines an interval [S/b^N, (S+1)/b^N).  Decimal
    digits are emitted only if that whole interval lies in a single 10^-places
    bucket, so no unknown continuation can alter a displayed digit.
    """
    if base < 2:
        raise WordDisplayError("fraction base must be at least 2")
    if places < 1:
        raise WordDisplayError("decimal place count must be positive")
    if not values:
        raise WordDisplayError("cannot render an empty residue word")
    if any(value < 0 or value >= base for value in values):
        raise WordDisplayError(f"base-{base} fraction requested for an out-of-range residue")

    numerator = 0
    for value in values:
        numerator = numerator * base + value
    denominator = base ** len(values)
    scale = 10 ** places
    lower = (numerator * scale) // denominator
    # The right endpoint is excluded.  This is the highest decimal bucket
    # reached by a continuation compatible with the finite stored word.
    upper = (((numerator + 1) * scale) - 1) // denominator
    if lower != upper:
        raise WordDisplayError(
            f"{places} decimal digits are not determined by the {len(values)} known base-{base} residues"
        )
    return "0." + f"{lower:0{places}d}" + "…"


def certify_decimal_views(root: Path, views: list[WordView]) -> dict[tuple[str, int], DecimalView]:
    """Recover full recorded streams and link every displayed decimal to its word."""
    by_key = {(view.lane, view.modulus): view for view in views}
    result: dict[tuple[str, int], DecimalView] = {}
    for lane in ("d12", "24A", "24B"):
        lane_views = [by_key[key] for key in DECIMAL_VIEWS if key[0] == lane]
        if not lane_views:
            continue
        targets = {view.target_events for view in lane_views}
        saved_lengths = {len(view.values) for view in lane_views}
        if len(targets) != 1 or len(saved_lengths) != 1:
            raise WordDisplayError(f"inconsistent saved-word metadata for {lane}")
        target_events = targets.pop()
        saved_terms = saved_lengths.pop()
        try:
            native, _steps, _record = certify_lane(root, lane, target_events, saved_terms)
        except CertificationError as exc:
            raise WordDisplayError(f"full-corpus certification failed for {lane}: {exc}") from exc
        for view in lane_views:
            full = tuple(label % view.modulus for label in native)
            if full[:saved_terms] != view.values:
                raise WordDisplayError(
                    f"saved {view.lane} mod {view.modulus} word is not the prefix of the complete retained stream"
                )
            # Force a two-horizon convergence check.  The saved 10,000-term
            # prefix and the complete retained stream must determine the same
            # 60-place decimal display before either is printed.
            result[(view.lane, view.modulus)] = DecimalView(
                lane=view.lane,
                modulus=view.modulus,
                residues=full,
                saved_terms=saved_terms,
            )
    return result


def decimal_line(decimal_view: DecimalView, places: int) -> str:
    saved = decimal_view.residues[:decimal_view.saved_terms]
    from_saved = base_word_as_decimal(saved, decimal_view.modulus, places)
    from_full = base_word_as_decimal(decimal_view.residues, decimal_view.modulus, places)
    if from_saved != from_full:
        raise WordDisplayError(
            f"base-{decimal_view.modulus} decimal display did not converge from saved prefix to full retained stream "
            f"for {decimal_view.lane}"
        )
    kind = "ternary" if decimal_view.modulus == 3 else f"base-{decimal_view.modulus}"
    return (
        f"  base-10 prefix from full retained {kind} stream "
        f"({len(decimal_view.residues)} residues; converged from saved {decimal_view.saved_terms}): {from_full}"
    )


def render_text(views: list[WordView], terms: int, decimal_places: int, decimals: dict[tuple[str, int], DecimalView]) -> str:
    lines = [f"Artifact 18 saved integer-word prefixes: first {terms} terms"]
    for view in views:
        prefix = view.values[:terms]
        lines.append(f"{view.lane} mod {view.modulus}: {','.join(str(value) for value in prefix)}")
        decimal_view = decimals.get((view.lane, view.modulus))
        if decimal_view is not None:
            lines.append(decimal_line(decimal_view, decimal_places))
    return "\n".join(lines)


def render_markdown(views: list[WordView], terms: int, decimal_places: int, decimals: dict[tuple[str, int], DecimalView]) -> str:
    lines = [
        "### First 50 terms" if terms == 50 else f"### First {terms} terms",
        "",
        f"Regenerate this checksum-checked display with `make words-print WORD_TERMS={terms}`.",
        "`make words-check` is the separate complete 50,000-event derivation check.",
        "",
        "```text",
        *render_text(views, terms, decimal_places, decimals).splitlines(),
        "```",
        "",
        "Each base-10 line is calculated from the complete retained lane, then compared",
        "with the corresponding saved 10,000-term prefix. Its 60 shown decimal places are",
        "tail-certified: no continuation after the retained data can alter any displayed digit.",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--terms", type=int, default=50)
    parser.add_argument(
        "--decimal-places",
        type=int,
        default=60,
        help="base-10 digits shown for certified base-3/base-6 conversions (default: 60)",
    )
    parser.add_argument("--markdown", action="store_true", help="emit a README-ready Markdown section")
    args = parser.parse_args()
    if args.terms < 1:
        raise SystemExit("--terms must be positive")
    if args.decimal_places < 1:
        raise SystemExit("--decimal-places must be positive")
    try:
        root = args.root.resolve()
        views = load_views(root, args.terms)
        decimals = certify_decimal_views(root, views)
        output = (
            render_markdown(views, args.terms, args.decimal_places, decimals)
            if args.markdown
            else render_text(views, args.terms, args.decimal_places, decimals)
        )
    except WordDisplayError as exc:
        raise SystemExit(f"FAIL words-print: {exc}") from exc
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
