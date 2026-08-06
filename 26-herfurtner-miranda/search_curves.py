#!/usr/bin/env python3
"""Public wrapper for the exact curve search and catalogue printer."""
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parent
runpy.run_path(str(ROOT / "code" / "run_model_search.py"), run_name="__main__")
