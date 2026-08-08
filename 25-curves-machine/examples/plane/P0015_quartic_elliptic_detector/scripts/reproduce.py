#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve()
REPO = HERE.parents[4]
cmd = [sys.executable, str(REPO / "code/tools/run_case.py"), "P0015"] + sys.argv[1:]
raise SystemExit(subprocess.call(cmd, cwd=REPO))
