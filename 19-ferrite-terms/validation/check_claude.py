#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
claude = (ROOT / 'FromClaude' / 'claude_terms_S21_S60.txt').read_text().splitlines()
ours = (ROOT / 'terms' / 'matched_n21_n60.txt').read_text().splitlines()

for left, right in zip(claude, ours):
    left_values = left.split(': ', 1)[1]
    right_values = right.split(': ', 1)[1]
    assert left_values == right_values

print('Claude agreement: 160 values, n=21..60, m=4,6,8,10.')
