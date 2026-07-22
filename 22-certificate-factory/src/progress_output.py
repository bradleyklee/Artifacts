#!/usr/bin/env python3
"""Shared 80-column progress formatter for generation and validation."""
from __future__ import annotations

import textwrap
import time

TOTAL_WIDTH = 80
TIMESTAMP_WIDTH = 10  # [HH:MM:SS]
STAGE_WIDTH = 22
SEPARATOR = " | "
PREFIX_WIDTH = TIMESTAMP_WIDTH + 1 + STAGE_WIDTH + len(SEPARATOR)
MESSAGE_WIDTH = TOTAL_WIDTH - PREFIX_WIDTH


def emit_progress(stage: str, message: object) -> None:
    """Print right-aligned stage labels and wrapped 80-column messages.

    Continuation lines begin in the same message column as the first line.
    Long unbroken algebraic expressions are split rather than overflowing.
    """
    stamp = f"[{time.strftime('%H:%M:%S')}]"
    stage_text = str(stage).strip()
    message_text = str(message)

    # Preserve explicit newlines while wrapping each logical paragraph.
    wrapped: list[str] = []
    for paragraph in message_text.splitlines() or [""]:
        lines = textwrap.wrap(
            paragraph,
            width=MESSAGE_WIDTH,
            break_long_words=True,
            break_on_hyphens=False,
            replace_whitespace=False,
            drop_whitespace=True,
        )
        wrapped.extend(lines or [""])

    first_prefix = f"{stamp} {stage_text:>{STAGE_WIDTH}}{SEPARATOR}"
    continuation_prefix = " " * PREFIX_WIDTH
    print(first_prefix + wrapped[0], flush=True)
    for line in wrapped[1:]:
        print(continuation_prefix + line, flush=True)
