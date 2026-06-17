#!/usr/bin/env python3
"""Print/write a compact card of the 48 used accept rules.

Input may be the PDF-derived visible payload or the reduced certificate.  The
card intentionally comes from visible-reconstructed data when used by Makefile.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def load_rules(obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    rules = obj.get("accept_rules") or obj.get("accept")
    if not isinstance(rules, list):
        raise SystemExit("input JSON does not contain a list named accept_rules")
    out = []
    for i, r in enumerate(rules, 1):
        key = r.get("canonical_neighbor_key") or r.get("key") or r.get("context")
        if isinstance(key, list):
            key = "|".join(str(x) for x in key)
        output = r.get("output") or r.get("out") or r.get("state")
        matrix_index = r.get("matrix_index", r.get("index", i))
        used = r.get("used_in_growth", True)
        out.append({"i": i, "matrix_index": matrix_index, "key": str(key), "output": str(output), "used": bool(used)})
    out.sort(key=lambda x: (int(x["matrix_index"]) if str(x["matrix_index"]).lstrip('-').isdigit() else 10**9, x["key"]))
    return out


def make_text(rules: List[Dict[str, Any]]) -> str:
    lines = []
    lines.append("DH12 Apex 852 — card of 48 used ACCEPT rules")
    lines.append("source: PDF-visible reconstruction payload, not embedded certificate")
    lines.append("format: R##  M###  six-neighbor canonical context  -> output")
    lines.append("-" * 88)
    for n, r in enumerate(rules, 1):
        lines.append(f"R{n:02d}  M{int(r['matrix_index']):03d}  {r['key']:<41} -> {r['output']}")
    lines.append("-" * 88)
    lines.append(f"total used accept rules: {len(rules)}")
    return "\n".join(lines) + "\n"


def make_md(rules: List[Dict[str, Any]]) -> str:
    lines = []
    lines.append("# DH12 Apex 852 — card of 48 used ACCEPT rules")
    lines.append("")
    lines.append("Source: PDF-visible reconstruction payload, not embedded certificate.")
    lines.append("")
    lines.append("| Rule | Matrix | Canonical six-neighbor context | Output |")
    lines.append("|---:|---:|---|---|")
    for n, r in enumerate(rules, 1):
        key = str(r["key"]).replace("|", "\\|")
        lines.append(f"| R{n:02d} | M{int(r['matrix_index']):03d} | `{key}` | `{r['output']}` |")
    lines.append("")
    lines.append(f"Total used accept rules: **{len(rules)}**")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("json_path")
    ap.add_argument("--out-txt")
    ap.add_argument("--out-md")
    args = ap.parse_args()
    obj = json.loads(Path(args.json_path).read_text())
    rules = load_rules(obj)
    if len(rules) != 48:
        raise SystemExit(f"expected 48 used accept rules, found {len(rules)}")
    text = make_text(rules)
    if args.out_txt:
        Path(args.out_txt).write_text(text)
    if args.out_md:
        Path(args.out_md).write_text(make_md(rules))
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
