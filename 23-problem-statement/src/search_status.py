#!/usr/bin/env python3
"""Summarize raw checkpoints and the deduplicated current search state."""
from __future__ import annotations

import collections
import json
from pathlib import Path

WIDTH = 80
RESOLVED = {"optimal", "infeasible"}


def say(text: str) -> None:
    text = " ".join(str(text).split())
    print(text if len(text) <= WIDTH else text[: WIDTH - 3] + "...")


search = Path("search")
files = sorted(search.glob("*.jsonl")) if search.exists() else []
raw = collections.Counter()
best: dict[int, str] = {}
raw_total = 0
for path in files:
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        count += 1
        raw_total += 1
        try:
            record = json.loads(line)
            class_id = int(record["class_id"])
            status = str(record.get("status", "unknown"))
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            raw["invalid"] += 1
            continue
        raw[status] += 1
        old = best.get(class_id)
        if old in RESOLVED:
            continue
        if status in RESOLVED or old is None:
            best[class_id] = status
        elif old == "unknown" and status == "timeout":
            best[class_id] = status
    say(f"[file] {path.name} records={count}")

current = collections.Counter(best.values())
say(f"[raw] files={len(files)} records={raw_total}")
say(f"[current] unique={len(best)}")
for status in ("optimal", "infeasible", "timeout", "unknown"):
    if current[status]:
        say(f"[current] {status}={current[status]}")
if not files:
    say("[current] no checkpoint files")
