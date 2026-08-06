from pathlib import Path
import runpy

ROOT = Path(__file__).parent

runpy.run_path(str(ROOT / "period_certificate" / "verify_scalar_certificate.py"))
runpy.run_path(str(ROOT / "laurent" / "derive_and_verify_laurent.py"))
runpy.run_path(str(ROOT / "figures" / "make_figures.py"))

print("All certificates verified and all figures regenerated.")
