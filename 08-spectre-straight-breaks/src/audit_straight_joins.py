#!/usr/bin/env python3
"""Audit closure of the positioned straight-only Spectre path catalogue.

Reads data/straight_path_records.csv as data; it does not reparse the TeX excerpts.
"""
from __future__ import annotations
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from spectre_straight import ROOT, Record, State, NAMES, read_records, record_join, state_tex, TEX_SYMBOL, mark_tex

DATA = ROOT / "data"


def tex_record(record: Record) -> str:
    return record.state_tex()


def tex_states(states: list[State] | tuple[State, ...]) -> str:
    return r"\;".join(state_tex(state) for state in states)


def grouped_words(left: Record, right: Record) -> str:
    return rf"\bigl({tex_states(left.word)}\bigr)\;\bigl({tex_states(right.word)}\bigr)"


def candidates(records_by_key, state: State) -> list[Record]:
    return records_by_key[state]


def position_solutions(states: list[State], records_by_key, limit: int = 2) -> list[list[Record]]:
    solutions: list[list[Record]] = []
    def walk(index: int, chosen: list[Record]) -> None:
        if len(solutions) >= limit:
            return
        if index == len(states):
            solutions.append(chosen.copy())
            return
        for record in candidates(records_by_key, states[index]):
            if not chosen or record_join(chosen[-1], record):
                walk(index + 1, chosen + [record])
    walk(0, [])
    return solutions


def maximal_prefix(states: list[State], records_by_key) -> tuple[int, list[list[Record]]]:
    active: list[list[Record]] = [[]]
    for index, state in enumerate(states):
        next_active = []
        for chosen in active:
            for record in candidates(records_by_key, state):
                if not chosen or record_join(chosen[-1], record):
                    next_active.append(chosen + [record])
        if not next_active:
            return index, active
        active = next_active
    return len(states), active


def marked_post(left: Record, prefix: list[Record], failure: int, states: list[State]) -> str:
    cut = len(left.word)
    tokens = []
    for i, state in enumerate(states):
        if i < len(prefix):
            tokens.append(tex_record(prefix[i]))
        elif i == failure:
            tokens.append(r"\underline{" + state_tex(state) + "}")
        else:
            tokens.append(state_tex(state))
    return rf"\bigl({' '.join(tokens[:cut])}\bigr)\;\bigl({' '.join(tokens[cut:])}\bigr)"


def required_after(prefix: list[Record]) -> str:
    if not prefix:
        return "initial positioned state unavailable"
    previous = prefix[-1]
    required_m = previous.exit_len - previous.exit_m + 1
    return rf"need\;({mark_tex((previous.exit_super[0], '+' if previous.exit_super[1] == '-' else '-' if previous.exit_super[1] == '+' else '1'))},\,{required_m}:{mark_tex((previous.exit_mark[0], '+' if previous.exit_mark[1] == '-' else '-' if previous.exit_mark[1] == '+' else '1'))})"


def run() -> None:
    records = read_records(DATA / "straight_path_records.csv")
    records_by_key: dict[State, list[Record]] = defaultdict(list)
    for record in records:
        records_by_key[(record.parent, record.n)].append(record)
    joins = [(left, right) for left in records for right in records if record_join(left, right)]
    rows = []
    break_counts: Counter[str] = Counter()
    location_counts: Counter[str] = Counter()
    for left, right in joins:
        states = list(left.word) + list(right.word)
        solutions = position_solutions(states, records_by_key)
        if solutions:
            status = "live-unique" if len(solutions) == 1 else "live-multiple"
            positioned = r"\;".join(record.state_tex() for record in solutions[0])
            break_symbol = location = reason = ""
            immediate = False
        else:
            status = "break"
            failure, prefixes = maximal_prefix(states, records_by_key)
            prefix = prefixes[0]
            break_symbol = state_tex(states[failure])
            if failure < len(left.word):
                location = "left word"
            elif failure == len(left.word):
                location = "image join"
            else:
                location = "right word"
            immediate = location == "image join"
            break_counts[break_symbol] += 1
            location_counts[location] += 1
            available = r",\;".join(record.state_tex() for record in records_by_key[states[failure]]) or r"\text{none}"
            reason = required_after(prefix) + rf";\;\mathrm{{avail}}\;{available}"
            positioned = marked_post(left, prefix, failure, states)
        rows.append({
            "pre": rf"{left.state_tex()}\mid {right.state_tex()}",
            "post": grouped_words(left, right),
            "broken": positioned,
            "br": break_symbol,
            "local": location,
            "immediate": str(immediate),
            "reason": reason,
            "status": status,
        })
    rows.sort(key=lambda row: (not (row["immediate"] == "True"), row["br"], row["pre"]))
    with (DATA / "straight_local_join_audit.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[(row["local"], row["br"], row["post"], row["reason"])].append(row)
    with (DATA / "straight_local_join_groups.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["location", "break", "post", "reason", "count", "example_1", "example_2"])
        for key, members in sorted(groups.items(), key=lambda item: (item[0][0], item[0][1], -len(item[1]), item[0][2])):
            writer.writerow([*key, len(members), members[0]["pre"], members[1]["pre"] if len(members) > 1 else ""])
    summary = {
        "straight_path_records": len(records),
        "valid_positioned_joins": len(joins),
        "breaking_inflated_joins": sum(1 for row in rows if row["status"] == "break"),
        "nonbreaking_inflated_joins": sum(1 for row in rows if row["status"].startswith("live")),
        "immediate_breaks": location_counts["image join"],
        "break_locations": dict(location_counts),
        "break_symbols": dict(break_counts.most_common()),
        "pathology_groups": len(groups),
    }
    (DATA / "straight_local_join_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["straight_path_records"] != 76 or summary["valid_positioned_joins"] != 288 or summary["nonbreaking_inflated_joins"] != 0 or summary["immediate_breaks"] != 25:
        raise SystemExit("audit invariant failed")

if __name__ == "__main__":
    run()
