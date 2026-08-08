#!/usr/bin/env python3
from __future__ import annotations
import json
import pathlib
import py_compile
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
REQUIRED = [
    "START_HERE.md",
    "01_PROJECT_DESCRIPTION.md",
    "02_PROGRESS_AND_STATUS.md",
    "03_THEORY_AND_ALGORITHM.md",
    "04_OPERATOR_MANUAL.md",
    "05_DATA_COVERAGE_AND_PERFORMANCE.md",
    "06_LESSONS_AND_OPEN_PROBLEMS.md",
    "07_ANNOTATED_FILE_TREE.md",
    "progress_meter.json",
    "data/benchmark/benchmark_statistics.json",
    "data/benchmark/benchmark_rows.csv",
    "data/bounds/generic_quartic_status.json",
    "algorithms/src/core/cartesian_cohomology_reduction.py",
    "algorithms/src/core/quartic_universal_bounds.py",
    "08_BRANCH_MERGE_SPHERE_CURVES.md",
    "BRANCH_MERGE_MANIFEST.md",
    "algorithms/pseudocode/ALG-007_SPHERE_CURVE_BRANCH.md",
    "algorithms/src/core/sphere_curve_conventions_check.py",
    "data/examples/sphere_curves/chapter4_operator_catalog.json",
    "algorithms/pseudocode/ALG-008_EVEN_SPHERE_QUARTIC_FACTORY.md",
    "algorithms/src/core/even_sphere_quartic_factory.py",
    "algorithms/src/core/even_sphere_period_data.py",
    "algorithms/scripts/replay_even_sphere_asymmetric.py",
    "data/examples/sphere_curves/asymmetric_1_2_5_exact_certificate.json",
    "data/examples/sphere_curves/even_quartic_catalog.json",
    "data/examples/sphere_curves/showcase_period_data.json",
    "algorithms/src/core/octahedral_invariant_reduction.py",
    "algorithms/scripts/replay_even_sphere_octahedral.py",
    "data/examples/sphere_curves/octahedral_exact_invariant_certificate.json",
    "data/examples/sphere_curves/octahedral_direct_degree7_certificate.json",
    "algorithms/pseudocode/ALG-009_DIHEDRAL_ODE_SPHERE.md",
    "algorithms/src/core/dihedral_ode_sphere.py",
    "algorithms/scripts/replay_dihedral_sphere_comparison.py",
    "data/examples/sphere_curves/dihedral_sphere_comparison.json",
    "reports/DIHEDRAL_SPHERE_IMPLEMENTATION_REPORT.md",
    "algorithms/pseudocode/ALG-010_EVEN_SPHERE_REFINEMENT_LOOP.md",
    "algorithms/scripts/run_even_sphere_refinement_loop.py",
    "data/examples/sphere_curves/even_sphere_refinement_stats.json",
    "reports/EVEN_SPHERE_REFINEMENT_REPORT.md",
    "algorithms/pseudocode/ALG-011_PHYSICS_GENERATING_SPHERE.md",
    "algorithms/src/core/physics_generating_sphere.py",
    "algorithms/scripts/replay_physics_generating_sphere.py",
    "data/examples/sphere_curves/physics_generating_function_stats.json",
    "algorithms/pseudocode/ALG-012_WATSON_PHYSICS_ADAPTER.md",
    "algorithms/src/core/watson_physics_adapter.py",
    "algorithms/scripts/replay_watson_physics_adapter.py",
    "data/examples/sphere_curves/watson_physics_adapter.json",
    "reports/PHYSICS_CONVENTION_SPHERE_REPORT.md",
    "reports/EVEN_SPHERE_RESEARCH_STATUS.md",
    "reports/OCTAHEDRAL_CERTIFICATE_COMPARISON.md",
    "algorithms/pseudocode/ALG-013_EVEN_SPHERE_COHOMOLOGY_BOUNDS.md",
    "algorithms/src/core/even_sphere_degree_bounds.py",
    "algorithms/src/core/hyperelliptic_period_reduction.py",
    "algorithms/src/core/reflection_invariant_sphere_reduction.py",
    "algorithms/scripts/replay_even_sphere_reflection.py",
    "data/bounds/even_sphere_degree_bounds.json",
    "data/examples/sphere_curves/reflection_xy_exact_certificate.json",
    "reports/EVEN_SPHERE_DEGREE_BOUND_REPORT.md",
    "algorithms/pseudocode/ALG-014_UNRESTRICTED_SPHERE_POLYNOMIAL_LOOP.md",
    "algorithms/scripts/replay_tetrahedral_sphere.py",
    "algorithms/scripts/replay_unrestricted_single_harmonic.py",
    "data/examples/sphere_curves/tetrahedral_exact_certificate.json",
    "data/examples/sphere_curves/unrestricted_single_harmonic_benchmark.json",
    "reports/UNRESTRICTED_SPHERE_POLYNOMIAL_STATUS.md",
    "algorithms/pseudocode/ALG-015_ICOSAHEDRAL_NORMALIZE_ELIMINATE_REDUCE.md",
    "algorithms/src/core/icosahedral_sphere.py",
    "algorithms/scripts/replay_icosahedral_sphere.py",
    "data/examples/sphere_curves/icosahedral_normalization_audit.json",
    "data/examples/sphere_curves/icosahedral_search.json",
    "reports/ICOSAHEDRAL_EXACT_CALCULATION.md",
    "algorithms/pseudocode/ALG-016_PERTURB_AND_RECORD.md",
    "algorithms/scripts/run_icosahedral_perturbation.py",
    "algorithms/scripts/screen_icosahedral_columns.py",
    "data/examples/sphere_curves/icosahedral_perturbation_z2.json",
    "data/examples/sphere_curves/icosahedral_perturbation_z2_columns.json",
    "data/examples/sphere_curves/icosahedral_perturbation_z.json",
    "reports/ICOSAHEDRAL_PERTURBATION_REPORT.md",
]

def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)

for rel in REQUIRED:
    if not (ROOT / rel).is_file():
        fail(f"missing {rel}")

json_count = 0
for path in ROOT.rglob("*.json"):
    try:
        with path.open("r", encoding="utf-8") as f:
            json.load(f)
    except Exception as exc:
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
    json_count += 1

py_count = 0
for path in (ROOT / "algorithms").rglob("*.py"):
    try:
        py_compile.compile(str(path), doraise=True)
    except Exception as exc:
        fail(f"Python compile error {path.relative_to(ROOT)}: {exc}")
    py_count += 1

stats = json.loads((ROOT / "data/benchmark/benchmark_statistics.json").read_text())
if stats.get("models_total") != 43:
    fail("benchmark model count is not 43")
if stats.get("mode_agreement_count") != 43:
    fail("benchmark mode agreement count is not 43")

print("TRANSFER_VERIFY_PASS")
print(f"root={ROOT}")
print(f"json_files={json_count}")
print(f"python_files_compiled={py_count}")
print("benchmark_models=43")
print("mode_agreement=43")
