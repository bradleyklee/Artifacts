#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
roots = [ROOT / 'code', ROOT / 'examples' / 'A303790']
count = 0
for base in roots:
    for path in sorted(base.rglob('*.py')):
        source = path.read_text(encoding='utf-8')
        compile(source, str(path), 'exec')
        count += 1
print(f'syntax check passed for {count} Python files')
