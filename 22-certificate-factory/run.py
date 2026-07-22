#!/usr/bin/env python3
from pathlib import Path
import runpy
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
runpy.run_path(str(ROOT / "src" / "relay_factory_v02.py"), run_name="__main__")
