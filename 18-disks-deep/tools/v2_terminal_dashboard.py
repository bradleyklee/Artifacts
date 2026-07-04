#!/usr/bin/env python3
"""80-column foreground dashboard for the sealed-block Artifact 18 campaign.

Read-only: consumes writer_status.json and report_status.json.  It never writes
physics data, checkpoints, blocks, or reporter outputs.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CSI = "\x1b["
RESET = CSI + "0m"
BOLD = CSI + "1m"
DIM = CSI + "2m"
GREEN = CSI + "32m"
YELLOW = CSI + "33m"
RED = CSI + "31m"
CYAN = CSI + "36m"

WIDTH = 80


def safe_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return {}


def parse_utc(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def age(value: object) -> str:
    stamp = parse_utc(value)
    if stamp is None:
        return "--"
    seconds = max(0, int((datetime.now(timezone.utc) - stamp).total_seconds()))
    if seconds < 60:
        return f"{seconds:2d}s"
    if seconds < 3600:
        return f"{seconds // 60:d}m{seconds % 60:02d}s"
    return f"{seconds // 3600:d}h{(seconds % 3600) // 60:02d}m"


def duration(seconds: float) -> str:
    seconds = max(0.0, seconds)
    if seconds < 60:
        return f"{seconds:4.1f}s"
    if seconds < 3600:
        return f"{int(seconds // 60):d}m{int(seconds % 60):02d}s"
    return f"{int(seconds // 3600):d}h{int((seconds % 3600) // 60):02d}m"


def n(value: object, width: int = 0) -> str:
    try:
        text = f"{int(value):,}"
    except (TypeError, ValueError):
        text = "--"
    return f"{text:>{width}}" if width else text


def f(value: object, precision: int = 3) -> str:
    try:
        return f"{float(value):+.{precision}f}"
    except (TypeError, ValueError):
        return "--"


def fit(text: str, width: int = WIDTH) -> str:
    return text[:width].ljust(width)


class Dashboard:
    def __init__(self, root: Path, children: dict[str, Any], target: int) -> None:
        self.root = root
        self.children = children
        self.target = target
        self.started = time.monotonic()
        self.active = False
        self.spinner = 0
        self.color = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

    def style(self, text: str, code: str) -> str:
        return f"{code}{text}{RESET}" if self.color else text

    def start(self) -> None:
        if sys.stdout.isatty() and not self.active:
            sys.stdout.write(CSI + "?1049h" + CSI + "?25l")
            sys.stdout.flush()
            self.active = True

    def close(self) -> None:
        if self.active:
            sys.stdout.write(CSI + "?25h" + CSI + "?1049l")
            sys.stdout.flush()
            self.active = False

    def _state_label(self, state: str) -> str:
        labels = {
            'running': 'RUNNING',
            'sealed': 'SEALED',
            'idle': 'IDLE',
            'target_reached': 'TARGET DONE',
            'stopped_nonregular_or_error': 'STOP/ERROR',
            'seal_check_failed': 'CHECK FAIL',
            'starting': 'STARTING',
            'done': 'DONE',
        }
        return labels.get(state, state[:13].upper())

    def lane(self, lane: str) -> list[str]:
        writer = safe_json(self.root / "campaign" / "live" / lane / "writer_status.json")
        report = safe_json(self.root / "campaign" / "live" / lane / "report_status.json")
        proc = self.children.get(lane)
        rc = None if proc is None else proc.poll()
        state = str(writer.get("state", "starting"))
        if rc is not None:
            state = "done" if rc == 0 else f"exit {rc}"
        if state in {"running", "sealed", "idle"}:
            color = GREEN
        elif state in {"target_reached", "done", "stopping"}:
            color = YELLOW
        else:
            color = RED
        label = self.style(f"{lane:<3}", CYAN + BOLD)
        state_display = self.style(f"{self._state_label(state):<13}", color)
        accepted = report.get("accepted_collision", writer.get("accepted_collision", 0))
        blocks = report.get("blocks", 0)
        total = report.get("latest_total_bits")
        sl = report.get("slope_1000_bits_per_collision")
        rate = writer.get("events_per_second")
        start = writer.get("segment_start")
        end = writer.get("segment_end")
        if state == "running" and start is not None and end is not None:
            work = f"work {n(start)}->{n(end)}"
        else:
            work = f"last {n(accepted)}"
        line1 = f" {label} {state_display}  {work:<25} {n(accepted):>7}/{n(self.target):<7}"
        line2 = (
            f"     blocks {n(blocks):>3}  total {n(total):>7} bits  "
            f"slope(1000) {f(sl):>7}/evt  rate {f(rate,1):>6}/s"
        )
        writer_stamp = writer.get("updated_utc") or writer.get("started_utc")
        line3 = f"     writer {age(writer_stamp):>6} ago  report {age(report.get('updated_utc')):>6} ago"
        return [fit(line1), fit(line2), fit(line3)]

    def reporter_line(self) -> str:
        status = safe_json(self.root / "campaign" / "live" / "reporter_status.json")
        proc = self.children.get("reporter")
        rc = None if proc is None else proc.poll()
        if rc is None:
            state, color = "running", GREEN
        elif rc == 0:
            state, color = "done", YELLOW
        else:
            state, color = f"exit {rc}", RED
        text = (
            f" reporter {self.style(state, color)}  pid={getattr(proc, 'pid', '--')}  "
            f"update {age(status.get('updated_utc'))} ago  "
            "SVG: campaign/live/<lane>/"
        )
        return fit(text)

    def snapshot(self, stopping: bool = False) -> str:
        self.spinner = (self.spinner + 1) % 4
        spin = "|/-\\"[self.spinner]
        elapsed = duration(time.monotonic() - self.started)
        top_state = "STOP REQUESTED" if stopping else "LIVE"
        state_code = YELLOW + BOLD if stopping else GREEN + BOLD
        heading = (
            f" ARTIFACT 18 TWO-BODY  {spin}  "
            f"{self.style(top_state, state_code)}  3 writers + reporter  {elapsed}"
        )
        rule = self.style("=" * WIDTH, DIM)
        lines = [fit(heading), rule]
        for lane in ("d12", "24A", "24B"):
            lines.extend(self.lane(lane))
            lines.append(self.style("-" * WIDTH, DIM))
        lines.append(self.reporter_line())
        lines.append(rule)
        lines.append(fit("Blocks seal every 1,000 events. Ctrl-C finishes current block, then exits."))
        lines.append(fit("Accepted values are sealed blocks only; active work is not plotted yet."))
        return "\n".join(lines)

    def render(self, stopping: bool = False) -> None:
        if not sys.stdout.isatty():
            return
        sys.stdout.write(CSI + "H" + CSI + "J" + self.snapshot(stopping))
        sys.stdout.flush()

