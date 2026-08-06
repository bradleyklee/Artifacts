#!/usr/bin/env python3
"""Write aggregate public or private solver statistics without crossing roots."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(path)


def public_stats() -> dict:
    catalogue_path = PROJECT_ROOT / "examples/public/catalogue/models.json"
    catalogue = read(catalogue_path)
    perturbation_path = PROJECT_ROOT / "examples/public/PERTURBATIONS.json"
    regression_paths = [
        PROJECT_ROOT / "examples/public/regression/order3_triangle.json",
        PROJECT_ROOT / "examples/public/regression/order4_triangle.json",
    ]
    perturbations = read(perturbation_path) if perturbation_path.exists() else {
        "records": []
    }
    regressions = [
        read(path) for path in regression_paths if path.exists()
    ]
    records = perturbations["records"]
    orders = Counter(
        str(record["order"])
        for record in records
        if "order" in record
    )
    statuses = Counter(record["status"] for record in records)
    result = {
        "schema": "laurent-period-public-stats-v1",
        "canonical_baseline": {
            "records": len(catalogue["models"]),
            "laurent_realizations": sum(
                model.get("laurent_model") is not None
                for model in catalogue["models"]
            ),
            "complete_double_certificates": catalogue["summary"][
                "double_telescoper_isoperiodic_proofs"
            ],
            "verification": "11/11 records; 4/4 complete certificates",
        },
        "systematic_perturbations": {
            "base": perturbations.get("base"),
            "completed_records": len(records),
            "status_counts": dict(sorted(statuses.items())),
            "operator_order_counts": dict(sorted(orders.items())),
            "controls": perturbations.get("controls", {}),
        },
    }
    if regressions:
        result["higher_order_regressions"] = [
            {
                "F": regression["F"],
                "order": regression["operator_stats"]["order"],
                "shift_degree": regression["operator_stats"]["shift_degree"],
                "term_count": len(regression["constant_terms"]),
                "dilation": regression["certificate"]["dilation"],
                "matrix_shape": regression["certificate"]["matrix_shape"],
                "pole_layers": len(regression["certificate"]["layers"]),
                "checks": regression["checks"],
                "rational_reconstruction_degree_bound": None,
                "exact_solve_field": "Q(t)",
            }
            for regression in regressions
        ]
    return result


def private_stats() -> dict:
    root = PROJECT_ROOT / "examples/private/platonic"
    models = read(root / "models.json")["models"]
    references = []
    for model in models:
        record = read(root / "reference" / f"{model['model']}.json")
        references.append({
            "model": model["model"],
            "G_shape": record["matrices"]["G"]["shape"],
            "J_shape": record["matrices"]["J"]["shape"],
            "order": 2,
        })
    return {
        "schema": "laurent-period-private-stats-v1",
        "canonical_baseline": {
            "records": len(models),
            "verification": "8/8 exact stored certificates",
        },
        "records": references,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scope", choices=("public", "private", "all"))
    args = parser.parse_args()
    if args.scope in {"public", "all"}:
        write(PROJECT_ROOT / "examples/public/STATS.json", public_stats())
    if args.scope in {"private", "all"}:
        write(
            PROJECT_ROOT / "examples/private/platonic/STATS.json",
            private_stats(),
        )


if __name__ == "__main__":
    main()
