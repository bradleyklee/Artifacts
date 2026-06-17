#!/usr/bin/env python3
"""No-dependency visible/vector scraper for the Apex 852 SVG art source.

This is the dependency-free companion to the PDF scraper.  It does not read the
PDF embedded certificate or the SVG <metadata> payload.  It reconstructs the
same rule payload from visible SVG shapes and visible text:
  - H/D cell polygons and port-dot/line geometry,
  - 15 P7 seven-patch thumbnails,
  - the 18x30 accept/reject/pad matrix,
  - the visible printed accept list,
  - the complete 852-cell main panel.
"""
from __future__ import annotations
import argparse, json, math, re, statistics, sys, xml.etree.ElementTree as ET
from collections import Counter, deque
from pathlib import Path

GREEN = "#7ebe6f"
YELLOW = "#e2c95f"
M_ACCEPT = "#2b4fc4"
M_REJECT = "#c53aa5"
BLACK = "#000000"
PORT_BLACK = "#080808"

DIR_VECS_SCREEN = [
    (1.0, 0.0),
    (0.5, -math.sqrt(3) / 2),
    (-0.5, -math.sqrt(3) / 2),
    (-1.0, 0.0),
    (-0.5, math.sqrt(3) / 2),
    (0.5, math.sqrt(3) / 2),
]
DIRS_AXIAL = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def fnum(v, default=0.0) -> float:
    if v is None or v == "":
        return float(default)
    v = str(v).strip().replace("px", "")
    return float(v)


def parse_translate(attr: str | None) -> tuple[float, float]:
    if not attr:
        return (0.0, 0.0)
    dx = dy = 0.0
    for m in re.finditer(r"translate\(([^)]*)\)", attr):
        nums = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", m.group(1))]
        if nums:
            dx += nums[0]
            dy += nums[1] if len(nums) > 1 else 0.0
    return dx, dy


def hex_color(v: str | None) -> str | None:
    if v is None:
        return None
    v = v.strip()
    return v.lower() if v.startswith("#") else v


def dir_idx_from_vector(dx, dy):
    n = math.hypot(dx, dy)
    if n == 0:
        raise ValueError("zero vector")
    dx, dy = dx / n, dy / n
    return max(range(6), key=lambda i: dx * DIR_VECS_SCREEN[i][0] + dy * DIR_VECS_SCREEN[i][1])


def physical_state_from_ports(typ, port_dirs):
    S = set(port_dirs)
    if typ == "H":
        if len(S) != 1:
            raise ValueError(f"H cell has {len(S)} port directions: {sorted(S)}")
        return f"H.{next(iter(S))}"
    if typ == "D":
        if len(S) != 4:
            raise ValueError(f"D cell has {len(S)} port directions: {sorted(S)}")
        for i in range(6):
            if S == {(i + j) % 6 for j in range(4)}:
                return f"D.{i}"
        raise ValueError(f"D cell port directions not four-consecutive: {sorted(S)}")
    raise ValueError(f"unknown type {typ}")


def rotate_state(st, k):
    if st == "*":
        return "*"
    typ, idx = st.split(".")
    return f"{typ}.{(int(idx) + k) % 6}"


def inverse_rotate_state(st, k):
    if st == "*":
        return "*"
    typ, idx = st.split(".")
    return f"{typ}.{(int(idx) - k) % 6}"


def rotate_key(raw_key, k):
    out = ["*"] * 6
    for p, st in enumerate(raw_key):
        out[(p + k) % 6] = rotate_state(st, k)
    return tuple(out)


def canonicalize(raw_key):
    candidates = [rotate_key(tuple(raw_key), k) for k in range(6)]
    best = min(candidates)
    return best, candidates.index(best)


def component_clusters(items, threshold):
    used = [False] * len(items)
    comps = []
    for a in range(len(items)):
        if used[a]:
            continue
        stack = [a]
        used[a] = True
        comp = []
        while stack:
            idx = stack.pop()
            comp.append(items[idx])
            _, cx, cy, *_ = items[idx]
            for j, other in enumerate(items):
                if used[j]:
                    continue
                _, ox, oy, *_ = other
                if math.hypot(cx - ox, cy - oy) < threshold:
                    used[j] = True
                    stack.append(j)
        comps.append(comp)
    return comps


class VisibleSVGScraper:
    def __init__(self, svg_path: str | Path):
        self.svg_path = Path(svg_path)
        self.shapes = []
        self.text = []
        root = ET.fromstring(self.svg_path.read_text(encoding="utf-8"))
        self._walk(root, 0.0, 0.0, 1.0, 1.0, in_metadata=False)
        self.text = "\n".join(self.text)
        self.port_dots = self._extract_port_dots()
        self.center_lines = self._extract_center_lines()

    def _pt(self, x, y, ox, oy, sx, sy):
        return (ox + sx * x, oy + sy * y)

    def _walk(self, elem, ox, oy, sx, sy, in_metadata=False):
        tag = local(elem.tag)
        if tag == "metadata":
            return
        tx, ty = parse_translate(elem.attrib.get("transform"))
        ox += sx * tx
        oy += sy * ty
        if tag == "svg" and "viewBox" in elem.attrib:
            x = fnum(elem.attrib.get("x"), 0)
            y = fnum(elem.attrib.get("y"), 0)
            w = fnum(elem.attrib.get("width"), 0)
            h = fnum(elem.attrib.get("height"), 0)
            nums = [float(v) for v in elem.attrib["viewBox"].replace(",", " ").split()]
            if len(nums) == 4 and w and h:
                vx, vy, vw, vh = nums
                ox = ox + sx * x - sx * (w / vw) * vx
                oy = oy + sy * y - sy * (h / vh) * vy
                sx = sx * (w / vw)
                sy = sy * (h / vh)
        elif tag == "g":
            pass
        elif tag == "polygon":
            pts = []
            for token in elem.attrib.get("points", "").strip().split():
                if not token:
                    continue
                a, b = token.split(",")
                pts.append(self._pt(float(a), float(b), ox, oy, sx, sy))
            if pts:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                self.shapes.append({
                    "kind": "polygon",
                    "fill": hex_color(elem.attrib.get("fill")),
                    "stroke": hex_color(elem.attrib.get("stroke")),
                    "points": pts,
                    "x0": min(xs), "y0": min(ys),
                    "x1": max(xs), "y1": max(ys),
                })
        elif tag == "rect":
            x = fnum(elem.attrib.get("x"), 0)
            y = fnum(elem.attrib.get("y"), 0)
            w = fnum(elem.attrib.get("width"), 0)
            h = fnum(elem.attrib.get("height"), 0)
            x0, y0 = self._pt(x, y, ox, oy, sx, sy)
            x1, y1 = self._pt(x + w, y + h, ox, oy, sx, sy)
            self.shapes.append({
                "kind": "rect",
                "fill": hex_color(elem.attrib.get("fill")),
                "stroke": hex_color(elem.attrib.get("stroke")),
                "x0": min(x0, x1), "y0": min(y0, y1),
                "x1": max(x0, x1), "y1": max(y0, y1),
            })
        elif tag == "circle":
            cx, cy = self._pt(fnum(elem.attrib.get("cx")), fnum(elem.attrib.get("cy")), ox, oy, sx, sy)
            r = fnum(elem.attrib.get("r")) * (abs(sx) + abs(sy)) / 2
            self.shapes.append({
                "kind": "circle",
                "fill": hex_color(elem.attrib.get("fill")),
                "stroke": hex_color(elem.attrib.get("stroke")),
                "cx": cx, "cy": cy, "r": r,
                "x0": cx - r, "y0": cy - r,
                "x1": cx + r, "y1": cy + r,
            })
        elif tag == "line":
            x0, y0 = self._pt(fnum(elem.attrib.get("x1")), fnum(elem.attrib.get("y1")), ox, oy, sx, sy)
            x1, y1 = self._pt(fnum(elem.attrib.get("x2")), fnum(elem.attrib.get("y2")), ox, oy, sx, sy)
            self.shapes.append({
                "kind": "line",
                "fill": hex_color(elem.attrib.get("fill")),
                "stroke": hex_color(elem.attrib.get("stroke")),
                "x0": x0, "y0": y0,
                "x1": x1, "y1": y1,
            })
        elif tag == "text":
            # Visible text only; metadata is never walked.
            t = "".join(elem.itertext()).strip()
            if t:
                self.text.append(t)
        for child in list(elem):
            self._walk(child, ox, oy, sx, sy, in_metadata=in_metadata)

    def _extract_port_dots(self):
        out = []
        for i, s in enumerate(self.shapes):
            if s["kind"] == "circle" and s.get("fill") == PORT_BLACK:
                out.append({"draw_index": i, "cx": s["cx"], "cy": s["cy"], "r": s["r"]})
        return out

    def _extract_center_lines(self):
        out = []
        for i, s in enumerate(self.shapes):
            if s["kind"] == "line" and s.get("stroke") == PORT_BLACK:
                out.append({"draw_index": i, "x0": s["x0"], "y0": s["y0"], "x1": s["x1"], "y1": s["y1"]})
        return out

    def port_dirs_for_cell(self, cx, cy, cell_h):
        dirs = []
        for dot in self.port_dots:
            dx = dot["cx"] - cx
            dy = dot["cy"] - cy
            if math.hypot(dx, dy) < 0.44 * cell_h:
                dirs.append(dir_idx_from_vector(dx, dy))
        center_tol = 0.035 * cell_h
        for ln in self.center_lines:
            d0 = math.hypot(ln["x0"] - cx, ln["y0"] - cy)
            d1 = math.hypot(ln["x1"] - cx, ln["y1"] - cy)
            if d0 < center_tol:
                dirs.append(dir_idx_from_vector(ln["x1"] - ln["x0"], ln["y1"] - ln["y0"]))
            elif d1 < center_tol:
                dirs.append(dir_idx_from_vector(ln["x0"] - ln["x1"], ln["y0"] - ln["y1"]))
        return tuple(sorted(set(dirs)))

    def hd_cells_in_box(self, x0, y0, x1, y1):
        cells = []
        for idx, s in enumerate(self.shapes):
            if s["kind"] != "polygon" or s.get("fill") not in (GREEN, YELLOW):
                continue
            cx = (s["x0"] + s["x1"]) / 2
            cy = (s["y0"] + s["y1"]) / 2
            if not (x0 <= cx <= x1 and y0 <= cy <= y1):
                continue
            h = s["y1"] - s["y0"]
            typ = "H" if s["fill"] == GREEN else "D"
            ports = self.port_dirs_for_cell(cx, cy, h)
            state = physical_state_from_ports(typ, ports)
            cells.append({
                "draw_index": idx,
                "cx": cx, "cy": cy,
                "w": s["x1"] - s["x0"], "h": h,
                "type": typ,
                "ports": list(ports),
                "state": state,
            })
        return cells

    def extract_p7_templates(self):
        cells = self.hd_cells_in_box(245, 500, 455, 705)
        comps = component_clusters([(c["draw_index"], c["cx"], c["cy"], c) for c in cells], 15)
        comps = sorted(comps, key=lambda comp: (
            sum(x[2] for x in comp) / len(comp),
            sum(x[1] for x in comp) / len(comp),
        ))
        if len(comps) != 15 or any(len(c) != 7 for c in comps):
            raise RuntimeError(f"P7 extraction expected 15 comps of 7, got {[len(c) for c in comps]}")
        templates = []
        for rep_index, comp in enumerate(comps):
            cx = sum(x[1] for x in comp) / len(comp)
            cy = sum(x[2] for x in comp) / len(comp)
            center_item = min(comp, key=lambda x: math.hypot(x[1] - cx, x[2] - cy))
            center = center_item[3]
            slots = [None] * 6
            for item in comp:
                if item is center_item:
                    continue
                cell = item[3]
                slot = dir_idx_from_vector(cell["cx"] - center["cx"], cell["cy"] - center["cy"])
                if slots[slot] is not None:
                    raise RuntimeError(f"duplicate P7 slot {slot} in rep {rep_index}")
                slots[slot] = cell["state"]
            if any(s is None for s in slots):
                raise RuntimeError(f"missing P7 slot in rep {rep_index}: {slots}")
            templates.append({"rep_index": rep_index, "center": center["state"], "slots": slots})
        return templates

    def extract_matrix_statuses(self):
        status_by_idx = {i: "blank" for i in range(540)}
        candidates = []
        for draw_idx, s in enumerate(self.shapes):
            if s["kind"] != "rect" or s.get("fill") not in (M_ACCEPT, M_REJECT, BLACK):
                continue
            if not (55 <= s["x0"] <= 195 and 480 <= s["y0"] <= 690):
                continue
            w = s["x1"] - s["x0"]
            h = s["y1"] - s["y0"]
            if not (3.5 <= w <= 5.5 and 3.5 <= h <= 5.5):
                continue
            candidates.append((draw_idx, s["fill"], s))
        if not candidates:
            raise RuntimeError("no matrix square candidates")
        x0 = min(r["x0"] for _, _, r in candidates)
        y0 = min(r["y0"] for _, _, r in candidates)
        xs = sorted(set(round(r["x0"], 3) for _, _, r in candidates))
        ys = sorted(set(round(r["y0"], 3) for _, _, r in candidates))
        xdiffs = [xs[i + 1] - xs[i] for i in range(len(xs) - 1) if xs[i + 1] - xs[i] < 8]
        ydiffs = [ys[i + 1] - ys[i] for i in range(len(ys) - 1) if ys[i + 1] - ys[i] < 8]
        step_x = statistics.median(xdiffs)
        step_y = statistics.median(ydiffs)
        for _, col, r in candidates:
            c = round((r["x0"] - x0) / step_x)
            rr = round((r["y0"] - y0) / step_y)
            if not (0 <= c < 18 and 0 <= rr < 30):
                raise RuntimeError(f"matrix square outside 18x30: row={rr} col={c}")
            idx = rr * 18 + c
            status = "accept" if col == M_ACCEPT else "reject" if col == M_REJECT else "pad"
            status_by_idx[idx] = status
        counts = Counter(status_by_idx.values())
        # In the SVG source the four pad cells are intentionally not colored; mark
        # them by position after the 536 real canonical contexts.
        for idx in range(536, 540):
            if status_by_idx[idx] == "blank":
                status_by_idx[idx] = "pad"
        counts = Counter(status_by_idx.values())
        if counts["accept"] != 48 or counts["reject"] != 41 or counts["pad"] != 4:
            raise RuntimeError(f"matrix counts bad: {counts}")
        return status_by_idx, {"x0": x0, "y0": y0, "step_x": step_x, "step_y": step_y, "counts": dict(counts)}

    def extract_accept_text_types(self):
        pairs = re.findall(r"\b(\d{3})\s*(?:->|→)\s*([HD])\b", self.text)
        if len(pairs) != 48:
            raise RuntimeError(f"expected 48 printed accept entries, got {len(pairs)}")
        return {int(i): t for i, t in pairs}

    def extract_blocked_center(self):
        candidates = []
        for draw_idx, s in enumerate(self.shapes):
            if s["kind"] != "polygon" or s.get("fill") != BLACK:
                continue
            cx = (s["x0"] + s["x1"]) / 2
            cy = (s["y0"] + s["y1"]) / 2
            w = s["x1"] - s["x0"]
            h = s["y1"] - s["y0"]
            if 90 <= cx <= 380 and 150 <= cy <= 450 and 5.5 <= w <= 12.0 and 6.5 <= h <= 13.0:
                candidates.append((draw_idx, cx, cy, w, h))
        if len(candidates) != 1:
            raise RuntimeError(f"expected 1 blocked-center black hex, got {candidates}")
        _, cx, cy, w, h = candidates[0]
        return cx, cy, w, h

    def extract_main_state(self):
        all_cells = self.hd_cells_in_box(90, 150, 385, 450)
        comps = component_clusters([(i, c["cx"], c["cy"], c) for i, c in enumerate(all_cells)], 15)
        comps = sorted(comps, key=len, reverse=True)
        if len(comps) < 1 or len(comps[0]) != 852:
            raise RuntimeError(f"main state largest component expected 852, got {[len(c) for c in comps]}")
        cells = [item[3] for item in comps[0]]
        x_origin, y_origin, _, _ = self.extract_blocked_center()
        yvals = sorted(c["cy"] for c in cells)
        yclusters = []
        for y in yvals:
            if not yclusters or abs(y - yclusters[-1][-1]) > 1:
                yclusters.append([y])
            else:
                yclusters[-1].append(y)
        row_y = [statistics.mean(yc) for yc in yclusters]
        dy = statistics.median([row_y[i + 1] - row_y[i] for i in range(len(row_y) - 1)])
        dxs = []
        for ry in row_y:
            xs = sorted(c["cx"] for c in cells if abs(c["cy"] - ry) < 0.5)
            dxs.extend([xs[i + 1] - xs[i] for i in range(len(xs) - 1) if xs[i + 1] - xs[i] < 9])
        dx = statistics.median(dxs)
        state = {}
        max_err = 0.0
        for c in cells:
            r = round((c["cy"] - y_origin) / dy)
            q = round((c["cx"] - x_origin) / dx - r / 2)
            xp = x_origin + dx * (q + r / 2)
            yp = y_origin + dy * r
            err = math.hypot(c["cx"] - xp, c["cy"] - yp)
            max_err = max(max_err, err)
            if (q, r) in state:
                raise RuntimeError(f"duplicate main-state coordinate {(q, r)}")
            state[(q, r)] = c["state"]
        if (0, 0) in state:
            raise RuntimeError("blocked center coordinate unexpectedly occupied")
        if max_err > 0.02:
            raise RuntimeError(f"grid assignment max_err too large: {max_err}")
        axiom = {d: state.get(d) for d in DIRS_AXIAL}
        if any(v is None for v in axiom.values()):
            raise RuntimeError(f"missing visible seed neighbor around blocked center: {axiom}")
        return state, {
            "component_sizes": [len(c) for c in comps],
            "origin_svg_xy": [x_origin, y_origin],
            "dx": dx, "dy": dy,
            "max_grid_error": max_err,
            "axiom_from_visible_main": {f"{q},{r}": v for (q, r), v in axiom.items()},
            "counts": dict(Counter(state.values())),
        }


def build_matrix_from_p7(templates):
    rows = []
    seen = set()
    for rep in templates:
        slots = rep["slots"]
        rep_index = rep["rep_index"]
        for mask in range(64):
            raw = tuple(slots[b] if (mask >> b) & 1 else "*" for b in range(6))
            canonical_key, k = canonicalize(raw)
            if canonical_key in seen:
                continue
            seen.add(canonical_key)
            center_output = rotate_state(rep["center"], k)
            rows.append({
                "matrix_index": len(rows),
                "outer_index": rep_index * 64 + mask,
                "rep_index": rep_index,
                "mask": mask,
                "mask_bits_b0_to_b5": "".join("1" if (mask >> b) & 1 else "0" for b in range(6)),
                "raw_slots": raw,
                "canonical_rotation_k": k,
                "canonical_neighbor_key": canonical_key,
                "candidate_output_from_visible_p7_center": center_output,
                "candidate_output_type": center_output.split(".")[0],
            })
    return rows


def frontier(state, blocked={(0, 0)}):
    out = set()
    for q, r in state:
        for dq, dr in DIRS_AXIAL:
            c = (q + dq, r + dr)
            if c not in state and c not in blocked:
                out.add(c)
    return out


def key_matches_full_rotated(canonical_key, rotated_full_key):
    return all(a == "*" or a == b for a, b in zip(canonical_key, rotated_full_key))


def replay(accept_rules, reject_rules, axiom, max_steps=10000):
    state = dict(axiom)
    blocked = {(0, 0)}
    history = []
    unknown = []
    for t in range(max_steps):
        births = {}
        reject_count = 0
        unknown = []
        for q, r in sorted(frontier(state, blocked)):
            raw = tuple(state.get((q + dq, r + dr), "*") for dq, dr in DIRS_AXIAL)
            key, k = canonicalize(raw)
            if key in accept_rules:
                births[(q, r)] = inverse_rotate_state(accept_rules[key], k)
            elif key in reject_rules:
                reject_count += 1
            else:
                unknown.append({"cell": [q, r], "raw_key": list(raw), "canonical_key": list(key), "rotation_k": k})
        history.append({"t": t, "births": len(births), "placed": len(state) + len(births), "rejected_frontier": reject_count, "unknown_frontier": len(unknown)})
        if not births:
            return state, history, unknown
        for c, v in births.items():
            if c in state and state[c] != v:
                raise RuntimeError(f"birth conflict at {c}: {state[c]} vs {v}")
        state.update(births)
    raise RuntimeError(f"replay did not terminate within {max_steps} steps")


def compare_states(a, b):
    A, B = set(a), set(b)
    missing = sorted([[q, r, b[(q, r)]] for q, r in B - A])
    extra = sorted([[q, r, a[(q, r)]] for q, r in A - B])
    wrong = sorted([[q, r, a[(q, r)], b[(q, r)]] for q, r in (A & B) if a[(q, r)] != b[(q, r)]])
    return {"exact": a == b, "missing_count": len(missing), "extra_count": len(extra), "wrong_count": len(wrong), "missing_sample": missing[:10], "extra_sample": extra[:10], "wrong_sample": wrong[:10]}


def state_rows(state):
    return [[q, r, state[(q, r)]] for q, r in sorted(state)]


def key_index_maps(matrix_rows, status_by_index, accept_text_types):
    accept_types = {}
    reject_set = set()
    key_to_index = {}
    for row in matrix_rows:
        idx = row["matrix_index"]
        key = row["canonical_neighbor_key"]
        key_to_index[key] = idx
        status = status_by_index[idx]
        if status == "accept":
            typ = accept_text_types.get(idx)
            if typ is None:
                raise RuntimeError(f"matrix index {idx} is accept but absent from printed accept list")
            accept_types[key] = typ
        elif status == "reject":
            reject_set.add(key)
    return accept_types, reject_set, key_to_index


def transform_coord(q, r, k=0, sense=1):
    def f(d):
        return (k + sense * d) % 6
    v0 = DIRS_AXIAL[f(0)]
    v5 = DIRS_AXIAL[f(5)]
    return (q * v0[0] + r * v5[0], q * v0[1] + r * v5[1])


def transform_state_label(st, k=0, sense=1):
    typ, raw_i = st.split(".")
    i = int(raw_i)
    def f(d):
        return (k + sense * d) % 6
    if typ == "H":
        return f"H.{f(i)}"
    S = {f((i + j) % 6) for j in range(4)}
    return physical_state_from_ports("D", tuple(sorted(S)))


def apply_main_transform(state, k=0, sense=1, transform_labels=False):
    out = {}
    for (q, r), st in state.items():
        c = transform_coord(q, r, k, sense)
        out[c] = transform_state_label(st, k, sense) if transform_labels else st
    if len(out) != len(state):
        raise RuntimeError("main transform collapsed coordinates")
    return out


def forced_replay_extract_outputs(matrix_rows, status_by_index, accept_text_types, target_state, max_steps=10000):
    accept_types, reject_set, key_to_index = key_index_maps(matrix_rows, status_by_index, accept_text_types)
    axiom = {d: target_state.get(d) for d in DIRS_AXIAL}
    if any(v is None for v in axiom.values()):
        return {"ok": False, "reason": "missing_axiom_neighbor", "axiom": {f"{q},{r}": v for (q, r), v in axiom.items()}}
    state = dict(axiom)
    blocked = {(0, 0)}
    outputs = {}
    history = []
    for t in range(max_steps):
        births = {}
        reject_count = 0
        unknown = []
        conflicts = []
        for q, r in sorted(frontier(state, blocked)):
            raw = tuple(state.get((q + dq, r + dr), "*") for dq, dr in DIRS_AXIAL)
            key, rot = canonicalize(raw)
            if key in accept_types:
                idx = key_to_index[key]
                if (q, r) not in target_state:
                    conflicts.append({"kind": "accept_outside_target", "cell": [q, r], "matrix_index": idx, "canonical_key": list(key), "rotation_k": rot})
                    continue
                target = target_state[(q, r)]
                if not target.startswith(accept_types[key] + "."):
                    conflicts.append({"kind": "printed_output_type_mismatch", "cell": [q, r], "target": target, "printed_type": accept_types[key], "matrix_index": idx, "canonical_key": list(key), "rotation_k": rot})
                    continue
                canonical_output = rotate_state(target, rot)
                old = outputs.get(key)
                if old is not None and old != canonical_output:
                    conflicts.append({"kind": "rule_output_conflict", "cell": [q, r], "old_output": old, "new_output": canonical_output, "target": target, "matrix_index": idx, "canonical_key": list(key), "rotation_k": rot})
                    continue
                outputs[key] = canonical_output
                births[(q, r)] = target
            elif key in reject_set:
                reject_count += 1
            else:
                unknown.append({"cell": [q, r], "raw_key": list(raw), "canonical_key": list(key), "rotation_k": rot})
        history.append({"t": t, "births": len(births), "placed": len(state) + len(births), "rejected_frontier": reject_count, "unknown_frontier": len(unknown), "conflicts": len(conflicts)})
        if conflicts:
            return {"ok": False, "reason": "conflict", "history": history, "conflict_sample": conflicts[:10], "outputs_assigned": len(outputs), "state_cells": len(state)}
        if not births:
            cmp = compare_states(state, target_state)
            ok = cmp["exact"] and len(unknown) == 0
            return {"ok": ok, "reason": "terminal", "history": history, "unknown_terminal": len(unknown), "unknown_sample": unknown[:10], "compare_to_target": cmp, "outputs_assigned": len(outputs), "accept_count": len(accept_types), "state_cells": len(state), "outputs_by_key": outputs, "axiom": axiom}
        state.update(births)
    return {"ok": False, "reason": "max_steps", "history": history, "outputs_assigned": len(outputs), "state_cells": len(state)}


def find_working_main_transform(raw_state, matrix_rows, status_by_index, accept_text_types):
    attempts = []
    for transform_labels in (False, True):
        for sense in (1, -1):
            for k in range(6):
                target = apply_main_transform(raw_state, k=k, sense=sense, transform_labels=transform_labels)
                result = forced_replay_extract_outputs(matrix_rows, status_by_index, accept_text_types, target)
                summary = {"k": k, "sense": sense, "transform_labels": transform_labels, "ok": result.get("ok", False), "reason": result.get("reason"), "state_cells": result.get("state_cells"), "outputs_assigned": result.get("outputs_assigned"), "last_history_row": (result.get("history") or [None])[-1], "conflict_sample": result.get("conflict_sample", [])[:2], "unknown_terminal": result.get("unknown_terminal"), "compare_to_target": result.get("compare_to_target")}
                attempts.append(summary)
                if result.get("ok"):
                    return target, result, summary, attempts
    return None, None, None, attempts


def payload_rules_from_forced_outputs(matrix_rows, status_by_index, accept_text_types, outputs_by_key):
    accept = []
    reject = []
    for row in matrix_rows:
        idx = row["matrix_index"]
        status = status_by_index[idx]
        key = row["canonical_neighbor_key"]
        key_s = "|".join(key)
        if status == "accept":
            out = outputs_by_key.get(key, row.get("candidate_output_from_visible_p7_center"))
            printed_type = accept_text_types.get(idx)
            if printed_type != out.split(".")[0]:
                raise RuntimeError(f"accept output type mismatch at {idx}: printed {printed_type}, forced replay gives {out}")
            accept.append({"matrix_index": idx, "canonical_neighbor_key": key_s, "output": out, "output_type": out.split(".")[0]})
        elif status == "reject":
            reject.append({"matrix_index": idx, "canonical_neighbor_key": key_s})
    return accept, reject


def maybe_audit_payload(visible_payload, payload_path):
    ref = json.loads(Path(payload_path).read_text())
    ref_accept = {r["matrix_index"]: (r["canonical_neighbor_key"], r["output"], r["output_type"]) for r in ref["accept_rules"]}
    ref_reject = {r["matrix_index"]: r["canonical_neighbor_key"] for r in ref["reject_rules"]}
    vis_accept = {r["matrix_index"]: (r["canonical_neighbor_key"], r["output"], r["output_type"]) for r in visible_payload["accept_rules"]}
    vis_reject = {r["matrix_index"]: r["canonical_neighbor_key"] for r in visible_payload["reject_rules"]}
    accept_wrong = sorted([idx for idx in set(ref_accept) | set(vis_accept) if ref_accept.get(idx) != vis_accept.get(idx)])
    reject_wrong = sorted([idx for idx in set(ref_reject) | set(vis_reject) if ref_reject.get(idx) != vis_reject.get(idx)])
    return {"accept_exact": not accept_wrong, "reject_exact": not reject_wrong, "accept_wrong_count": len(accept_wrong), "reject_wrong_count": len(reject_wrong), "accept_wrong_sample": [{"index": i, "visible": vis_accept.get(i), "reference": ref_accept.get(i)} for i in accept_wrong[:10]], "reject_wrong_sample": [{"index": i, "visible": vis_reject.get(i), "reference": ref_reject.get(i)} for i in reject_wrong[:10]]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("svg")
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-state", required=True)
    ap.add_argument("--out-report", required=True)
    ap.add_argument("--audit-payload-json")
    args = ap.parse_args()

    scraper = VisibleSVGScraper(args.svg)
    p7_templates = scraper.extract_p7_templates()
    matrix_rows = build_matrix_from_p7(p7_templates)
    status_by_index, matrix_geom = scraper.extract_matrix_statuses()
    accept_text_types = scraper.extract_accept_text_types()
    raw_visible_state, state_geom = scraper.extract_main_state()

    if len(matrix_rows) != 536:
        raise RuntimeError(f"visible P7s x masks unique matrix expected 536, got {len(matrix_rows)}")
    if sorted(i for i, s in status_by_index.items() if s == "accept") != sorted(accept_text_types):
        raise RuntimeError("visible matrix accept cells do not match printed accept list")

    target_state, forced, chosen_transform, transform_attempts = find_working_main_transform(raw_visible_state, matrix_rows, status_by_index, accept_text_types)
    if not forced or not forced.get("ok"):
        report = {"ok": False, "svg": str(args.svg), "embedded_json_used": False, "failure": "no visible-main transform produced closed 852 replay", "transform_attempts": transform_attempts, "p7_templates": p7_templates, "matrix_geometry": matrix_geom, "matrix_counts": dict(Counter(status_by_index.values())), "main_state_geometry": state_geom, "visible_state_cells": len(raw_visible_state)}
        Path(args.out_report).write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        raise SystemExit(1)

    accept_rules, reject_rules = payload_rules_from_forced_outputs(matrix_rows, status_by_index, accept_text_types, forced["outputs_by_key"])
    accept_map = {tuple(r["canonical_neighbor_key"].split("|")): r["output"] for r in accept_rules}
    reject_set = {tuple(r["canonical_neighbor_key"].split("|")) for r in reject_rules}
    axiom = forced["axiom"]
    replay_state, history, unknown = replay(accept_map, reject_set, axiom)
    replay_cmp = compare_states(replay_state, target_state)

    payload = {
        "artifact": "visible_svg_rederived_payload_v88_plus_no_embedded_json_used",
        "source_svg": str(args.svg),
        "reconstruction_source": "visible/vector SVG shapes only: P7 diagrams, 18x30 matrix, printed accept list, main-frame pattern",
        "canonicalization": "six-neighbor keys modulo C6 rotation; center excluded from rule key",
        "display_convention": "visible port-dot convention: H.i has one port in direction i; D.i has ports i,i+1,i+2,i+3 modulo 6",
        "main_panel_transform_used_for_growth_check": chosen_transform,
        "p7_template_count": len(p7_templates),
        "mask_count": 64,
        "outer_product_count": 64 * len(p7_templates),
        "dictionary": {"accept_records_stored": len(accept_rules), "reject_records_stored": len(reject_rules), "canonical_accept_reject_overlap": len(set(accept_map) & reject_set)},
        "matrix": {"unique_canonical_neighbor_contexts": len(matrix_rows), "accept": len(accept_rules), "reject": len(reject_rules), "blank": Counter(status_by_index.values())["blank"], "pad_to_540": Counter(status_by_index.values())["pad"]},
        "seed_axiom_from_transformed_visible_main": {f"{q},{r}": v for (q, r), v in sorted(axiom.items())},
        "accept_rules": accept_rules,
        "reject_rules": reject_rules,
    }

    report = {
        "ok": True,
        "svg": str(args.svg),
        "embedded_json_used": False,
        "p7_templates": p7_templates,
        "matrix_geometry": matrix_geom,
        "matrix_counts": dict(Counter(status_by_index.values())),
        "matrix_unique_contexts": len(matrix_rows),
        "accept_text_count": len(accept_text_types),
        "main_state_geometry_raw_scrape": state_geom,
        "main_panel_transform_used_for_growth_check": chosen_transform,
        "transform_attempts_summary": transform_attempts,
        "raw_visible_state_cells": len(raw_visible_state),
        "target_state_cells_after_transform": len(target_state),
        "target_state_counts_after_transform": dict(Counter(target_state.values())),
        "rederived_rule_counts": {"accept": len(accept_rules), "reject": len(reject_rules)},
        "forced_output_derivation": {"outputs_assigned": forced["outputs_assigned"], "accept_count": forced["accept_count"], "history_len": len(forced["history"]), "last_history_row": forced["history"][-1], "unknown_terminal": forced["unknown_terminal"], "compare_to_target": forced["compare_to_target"]},
        "independent_replay_from_rederived_payload": {"final_cells": len(replay_state), "history_len": len(history), "last_history_row": history[-1], "unknown_terminal": len(unknown), "compare_to_transformed_visible_main": replay_cmp},
        "first_history_rows": history[:5],
        "last_history_rows": history[-5:],
        "output_source": "forced replay into complete visible main-frame pattern; each accepted birth fixes canonical output orientation from the target cell and rotation k",
    }
    if args.audit_payload_json:
        report["audit_against_payload_json_not_used_for_derivation"] = maybe_audit_payload(payload, args.audit_payload_json)

    Path(args.out_json).write_text(json.dumps(payload, indent=2) + "\n")
    Path(args.out_state).write_text(json.dumps(state_rows(target_state), indent=2) + "\n")
    Path(args.out_report).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
