#!/usr/bin/env python3
"""Geometry and source extraction for the straight-path Spectre baseline.

This module reads only the minimal Figure 4.2/Figure 5.1 TeX excerpts bundled
with this artifact. It does not import the paper or any precomputed rule table.
"""
from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source_excerpt"
NAMES = ["Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma", "Phi", "Psi"]
SYMBOL = {"Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ", "Pi": "Π", "Sigma": "Σ", "Phi": "Φ", "Psi": "Ψ"}
TEX_SYMBOL = {"Gamma": r"\Gamma", "Delta": r"\Delta", "Theta": r"\Theta", "Lambda": r"\Lambda", "Xi": r"\Xi", "Pi": r"\Pi", "Sigma": r"\Sigma", "Phi": r"\Phi", "Psi": r"\Psi"}
EDGE_SYMBOL = {"alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε", "zeta": "ζ", "eta": "η", "theta": "θ"}
EDGE_TEX = {"alpha": r"\alpha", "beta": r"\beta", "gamma": r"\gamma", "delta": r"\delta", "epsilon": r"\varepsilon", "zeta": r"\zeta", "eta": r"\eta", "theta": r"\theta"}
DIRECTIONS = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
SQRT3 = math.sqrt(3.0)
Mark = tuple[str, str]
State = tuple[str, int]

@dataclass(frozen=True)
class Record:
    parent: str
    n: int
    m: int
    entry_super: Mark
    entry_mark: Mark
    entry_len: int
    word: tuple[State, ...]
    exit_n: int
    exit_m: int
    exit_super: Mark
    exit_mark: Mark
    exit_len: int

    def state_tex(self) -> str:
        return rf"{TEX_SYMBOL[self.parent]}_{{{self.n},{self.m}}}"

    def word_tex(self) -> str:
        return r"\;".join(rf"{TEX_SYMBOL[t]}_{{{d}}}" for t, d in self.word)

    def state_plain(self) -> str:
        return f"{self.parent}_{self.n},{self.m}"


def plus(cell: tuple[int, int], d: int) -> tuple[int, int]:
    q, r = cell
    a, b = DIRECTIONS[d]
    return q + a, r + b


def vertex_coord(cell: tuple[int, int]) -> tuple[float, float]:
    i, j = cell
    return round(SQRT3 / 2 * i, 6), round(0.5 * i + j, 6)


def hex_center(cell: tuple[int, int]) -> tuple[float, float]:
    q, r = cell
    return SQRT3 * 2 * q + SQRT3 * r + SQRT3, 3 * r + 1


def rotate(point: tuple[float, float], turns: int) -> tuple[float, float]:
    angle = turns * math.pi / 3
    x, y = point
    return x * math.cos(angle) - y * math.sin(angle), x * math.sin(angle) + y * math.cos(angle)


def point_key(point: tuple[float, float]) -> tuple[float, float]:
    return round(point[0], 6), round(point[1], 6)


_BASE_EDGE = [(-SQRT3, 1), (-SQRT3, -1)]


def edge_points(cell: tuple[int, int], effective_edge: int) -> tuple[tuple[float, float], tuple[float, float]]:
    cx, cy = hex_center(cell)
    return tuple(point_key((cx + x, cy + y)) for x, y in (rotate(p, effective_edge) for p in _BASE_EDGE))  # type: ignore[return-value]


def mark_text(mark: Mark) -> str:
    edge, sign = mark
    return EDGE_SYMBOL[edge] + ("" if sign == "1" else sign)


def mark_tex(mark: Mark) -> str:
    edge, sign = mark
    base = EDGE_TEX[edge]
    return base if sign == "1" else rf"{base}^{{{sign}}}"


def mark_ascii(mark: Mark) -> str:
    edge, sign = mark
    return edge if sign == "1" else edge + sign


def state_tex(state: State) -> str:
    tile, d = state
    return rf"{TEX_SYMBOL[tile]}_{{{d}}}"


def state_ascii(state: State) -> str:
    tile, d = state
    return f"{tile}_{d}"


def opposite(mark: Mark) -> Mark:
    edge, sign = mark
    if sign == "1":
        return mark
    return edge, "+" if sign == "-" else "-"


def matches(left: Mark, right: Mark) -> bool:
    return opposite(left) == right


def parse_source() -> tuple[dict[str, tuple[Mark, ...]], dict[str, tuple[list[tuple[str, int, tuple[int, int]]], list[tuple[int, int]], list[Mark]]]]:
    macros = (SOURCE / "figure_4_2_edge_tile_macros.tex").read_text(encoding="utf-8")
    figure = (SOURCE / "figure_5_1_supertiles.tex").read_text(encoding="utf-8")
    cycles: dict[str, tuple[Mark, ...]] = {}
    for name in NAMES:
        match = re.search(r"\\newcommand\{\\hex" + name + r"\}\[3\]\{%(.*?)\n\}", macros, re.S)
        if not match:
            raise ValueError(f"Missing tile macro for {name}")
        values: list[Mark | None] = [None] * 6
        for call, angle in re.findall(r"\\edge([a-z]+)\{#1\}\{(\d+)\}", match.group(1)):
            edge, sign = call, "1"
            for suffix, candidate_sign in (("plus", "+"), ("minus", "-")):
                if call.endswith(suffix):
                    edge, sign = call[:-len(suffix)], candidate_sign
                    break
            values[int(angle) // 60] = edge, sign
        if any(v is None for v in values):
            raise ValueError(f"Incomplete edge cycle for {name}: {values}")
        cycles[name] = tuple(values)  # type: ignore[arg-type]

    starts = list(re.finditer(r"\\subfloat\[Supertile \$\\([A-Za-z]+)\$\]\{%", figure))
    blocks = {}
    for index, match in enumerate(starts):
        parent = match.group(1)
        end = starts[index + 1].start() if index + 1 < len(starts) else figure.find(r"\end{center}", match.end())
        body = figure[match.end():end]
        children = [(tile, int(angle) // 60 % 6, (int(q), int(r))) for tile, angle, q, r in re.findall(r"\\hex([A-Za-z]+)\{(-?\d+)\}\{(-?\d+)\}\{(-?\d+)\}", body)]
        boundary_vertices = [(int(a), int(b)) for a, b in re.findall(r"\\markpt\{(-?\d+)\}\{(-?\d+)\}", body)]
        labels: list[Mark] = []
        for text in re.findall(r"\\vctxt\{[^}]+\}\{[^}]+\}\{\$([^$]+)\$\}", body):
            m = re.search(r"\\([a-z]+)(?:\^\{?([+-])\}?)?", text)
            if not m:
                raise ValueError(f"Cannot parse macro-edge label {text!r}")
            labels.append((m.group(1), m.group(2) or "1"))
        if not (children and len(boundary_vertices) == 6 and len(labels) == 6):
            raise ValueError(f"Incomplete Figure 5.1 block {parent}")
        blocks[parent] = children, boundary_vertices, labels
    if set(blocks) != set(NAMES):
        raise ValueError(f"Figure 5.1 blocks mismatch: {sorted(blocks)}")
    return cycles, blocks


def boundary_arcs(parent: str, cycles, blocks):
    children, marks, labels = blocks[parent]
    cells = {position: (tile, rotation) for tile, rotation, position in children}
    exterior = []
    for position, (tile, rotation) in cells.items():
        for local_edge in range(6):
            effective = (local_edge + rotation) % 6
            outside_direction = (effective - 3) % 6
            if plus(position, outside_direction) not in cells:
                a, b = edge_points(position, effective)
                exterior.append({"a": a, "b": b, "cell": position, "tile": tile, "rotation": rotation,
                                 "local": local_edge, "effective": effective, "mark": cycles[tile][local_edge]})
    adjacency: dict[tuple[float, float], list[int]] = {}
    for i, edge in enumerate(exterior):
        adjacency.setdefault(edge["a"], []).append(i)
        adjacency.setdefault(edge["b"], []).append(i)
    start = vertex_coord(marks[0])
    candidates = []
    for first in adjacency[start]:
        sequence, vertices = [], [start]
        current, edge_index = start, first
        while True:
            sequence.append(edge_index)
            edge = exterior[edge_index]
            nxt = edge["b"] if edge["a"] == current else edge["a"]
            vertices.append(nxt)
            if nxt == start:
                break
            options = [x for x in adjacency[nxt] if x != edge_index]
            current, edge_index = nxt, options[0]
        candidates.append((sequence, vertices))
    marker_points = [vertex_coord(mark) for mark in marks]
    chosen = None
    for sequence, vertices in candidates:
        try:
            indices = [vertices.index(point) for point in marker_points]
        except ValueError:
            continue
        if indices == sorted(indices):
            chosen = sequence, indices
            break
    if chosen is None:
        raise ValueError(f"Cannot orient supertile boundary {parent}")
    sequence, indices = chosen
    arcs = []
    for i, label in enumerate(labels):
        begin = indices[i]
        end = indices[i + 1] if i + 1 < len(indices) else len(sequence)
        arcs.append((label, [exterior[x] for x in sequence[begin:end]]))
    return cells, arcs


def straight_records(parent: str, cycles, blocks) -> list[Record]:
    cells, arcs = boundary_arcs(parent, cycles, blocks)
    exterior = {}
    for n, (super_edge, edges) in enumerate(arcs):
        for m, edge in enumerate(edges, start=1):
            exterior[(edge["cell"], edge["effective"])] = n, m, super_edge, edge, len(edges)
    output = []
    for n, (entry_super, edges) in enumerate(arcs):
        for m, entry_edge in enumerate(edges, start=1):
            cell, travel = entry_edge["cell"], entry_edge["effective"]
            seen, word = {cell}, []
            while True:
                tile, rotation = cells[cell]
                word.append((tile, (rotation - travel) % 6))
                nxt = plus(cell, travel)
                if nxt in cells:
                    if nxt in seen:
                        raise ValueError("Unexpected cycle in straight path")
                    seen.add(nxt)
                    cell = nxt
                    continue
                exit_record = exterior.get((cell, (travel + 3) % 6))
                if exit_record:
                    exit_n, exit_m, exit_super, exit_edge, exit_len = exit_record
                    if exit_n == (n + 3) % 6:
                        output.append(Record(parent, n, m, entry_super, entry_edge["mark"], len(edges),
                                             tuple(word), exit_n, exit_m, exit_super, exit_edge["mark"], exit_len))
                break
    return output


def record_join(left: Record, right: Record) -> bool:
    return (matches(left.exit_super, right.entry_super)
            and matches(left.exit_mark, right.entry_mark)
            and left.exit_len == right.entry_len
            and right.m == left.exit_len - left.exit_m + 1)


def extract_all() -> tuple[dict[str, tuple[Mark, ...]], dict[str, object], dict[str, list[Record]]]:
    cycles, blocks = parse_source()
    catalogue = {tile: straight_records(tile, cycles, blocks) for tile in NAMES}
    return cycles, blocks, catalogue


def write_source_data(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    cycles, blocks, catalogue = extract_all()
    with (output_dir / "figure_4_2_edge_dictionary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["tile", "edge_index", "edge", "sign"])
        for tile in NAMES:
            for index, (edge, sign) in enumerate(cycles[tile]):
                writer.writerow([tile, index, edge, sign])
    with (output_dir / "figure_5_1_supertile_placements.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["parent", "child_order", "child", "rotation", "q", "r"])
        for parent in NAMES:
            children, _, _ = blocks[parent]
            for order, (child, rotation, (q, r)) in enumerate(children):
                writer.writerow([parent, order, child, rotation, q, r])
    with (output_dir / "figure_5_1_macro_edges.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["parent", "n", "edge", "sign"])
        for parent in NAMES:
            _, _, labels = blocks[parent]
            for n, (edge, sign) in enumerate(labels):
                writer.writerow([parent, n, edge, sign])
    with (output_dir / "straight_path_records.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["parent", "n", "m", "entry_super", "entry", "entry_len", "word_json", "exit_n", "exit_m", "exit_super", "exit", "exit_len"])
        for parent in NAMES:
            for record in catalogue[parent]:
                writer.writerow([record.parent, record.n, record.m, mark_ascii(record.entry_super), mark_ascii(record.entry_mark), record.entry_len,
                                 json.dumps(record.word, separators=(",", ":")), record.exit_n, record.exit_m,
                                 mark_ascii(record.exit_super), mark_ascii(record.exit_mark), record.exit_len])
    counts = {tile: len(catalogue[tile]) for tile in NAMES}
    (output_dir / "extraction_summary.json").write_text(json.dumps({"records_per_supertile": counts, "total_straight_records": sum(counts.values())}, indent=2) + "\n", encoding="utf-8")


def parse_mark_ascii(text: str) -> Mark:
    if text[-1:] in {"+", "-"}:
        return text[:-1], text[-1]
    return text, "1"


def read_records(csv_path: Path) -> list[Record]:
    output = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            output.append(Record(row["parent"], int(row["n"]), int(row["m"]), parse_mark_ascii(row["entry_super"]), parse_mark_ascii(row["entry"]), int(row["entry_len"]),
                                 tuple((str(t), int(d)) for t, d in json.loads(row["word_json"])), int(row["exit_n"]), int(row["exit_m"]),
                                 parse_mark_ascii(row["exit_super"]), parse_mark_ascii(row["exit"]), int(row["exit_len"])))
    return output
