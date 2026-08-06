from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parent

runpy.run_path(str(ROOT / "verify_scalar_certificate.py"))
runpy.run_path(str(ROOT / "derive_and_verify_laurent.py"))
runpy.run_path(str(ROOT / "make_figures.py"))

print("All public A303790 certificates verified and paper figures regenerated.")
