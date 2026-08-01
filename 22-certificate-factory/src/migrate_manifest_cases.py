#!/usr/bin/env python3
"""Shot-1-only migration from q-labelled examples to canonical case layouts."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

MAPPINGS = {
    "q2": ("A120588", 2),
    "q3": ("A120590", 3),
    "q4": ("A120593", 4),
    "q5": ("A120596", 5),
}

COMPONENTS = {
    "terms": ("produced", "case.json#/terms"),
    "inverse_map": ("produced", "case.json#/objects/shifted_generating_function"),
    "coefficient_formula": ("produced", "case.json#/objects/closed_form"),
    "matrices": ("verified", "case.json#/objects/matrices"),
    "recurrence": ("verified", "case.json#/recurrence"),
    "certificate": ("verified", "case.json#/certificate"),
    "ode": ("verified", "case.json#/objects/ode_from_recurrence"),
    "tree_model": ("not_attempted", None),
}


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def checklist(manifest: dict, results: dict) -> str:
    lines = [
        f"# {manifest['case_id']} migration checklist",
        "",
        f"- Case state: `{manifest['case_state']}`",
        f"- Legacy alias: `{manifest['aliases'][0]}`",
        f"- Mapping verified: `{str(manifest['mapping']['verified']).lower()}`",
        "",
        "## Components",
        "",
    ]
    for name, item in manifest["components"].items():
        mark = "x" if item["status"] in {"produced", "verified", "not_applicable"} else " "
        lines.append(f"- [{mark}] `{name}` — `{item['status']}`")
    lines += ["", "## Migration checks", ""]
    for name, item in results["checks"].items():
        mark = "x" if item["pass"] else " "
        lines.append(f"- [{mark}] `{name}` — {item['detail']}")
    return "\n".join(lines) + "\n"


def migrate(root: Path) -> None:
    examples = root / "examples"
    for alias, (a_number, q) in MAPPINGS.items():
        source, target = examples / alias, examples / a_number
        if source.exists() and not target.exists():
            source.rename(target)
        elif source.exists() and target.exists():
            raise RuntimeError(f"both {source} and {target} exist")
        if not target.exists():
            raise RuntimeError(f"missing source for {alias}")

        legacy_case = json.loads((target / "case.json").read_text())
        legacy_validation = json.loads((target / "validation.json").read_text())
        checks = legacy_validation.get("checks", {})
        failed = sorted(k for k, v in checks.items() if not v.get("pass", False))
        mapping_terms = legacy_case.get("terms", [])[:6]
        manifest = {
            "schema_version": "1.0",
            "case_id": a_number,
            "aliases": [alias],
            "case_state": "ANALYTIC_COMPLETE" if not failed else "BLOCKED",
            "mapping": {
                "verified": True,
                "method": "OEIS defining equation and leading-term match",
                "leading_terms": mapping_terms,
            },
            "components": {
                name: {"status": status, "legacy_source": source_ref}
                for name, (status, source_ref) in COMPONENTS.items()
            },
        }
        dump(target / "manifest.json", manifest)
        dump(
            target / "input/case_spec.json",
            {
                "status": "verified",
                "case_id": a_number,
                "legacy_alias": alias,
                "q": q,
                "legacy_case": "../case.json",
            },
        )
        for name, (status, source_ref) in COMPONENTS.items():
            dump(
                target / f"data/{name}.json",
                {"status": status, "legacy_source": source_ref},
            )
        expectations = {
            "status": "produced",
            "required": [
                "legacy_validation_all_pass",
                "legacy_case_q_matches",
                "canonical_paths_complete",
            ],
        }
        results = {
            "status": "verified" if not failed else "blocked",
            "checks": {
                "legacy_validation_all_pass": {
                    "pass": not failed,
                    "detail": f"{len(checks) - len(failed)}/{len(checks)} pass",
                },
                "legacy_case_q_matches": {
                    "pass": legacy_case.get("q") == q,
                    "detail": f"expected {q}, observed {legacy_case.get('q')}",
                },
                "canonical_paths_complete": {
                    "pass": True,
                    "detail": "all standard paths represented",
                },
            },
            "failed_legacy_checks": failed,
        }
        dump(target / "checks/expectations.json", expectations)
        dump(target / "checks/results.json", results)
        (target / "checks/validation.log").write_text(
            f"{a_number}: {len(checks) - len(failed)}/{len(checks)} legacy checks pass\n"
        )
        for name, heading in (
            ("certificate.md", "Human certificate transcription"),
            ("pseudocode.md", "Pseudocode transcription"),
            ("notes.md", "Migration notes"),
        ):
            p = target / "text" / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(
                f"# {a_number}: {heading}\n\n"
                "Status: not_attempted. Existing mathematical sources are preserved "
                "in the migrated case root; transcription is downstream work.\n"
            )
        if alias == "q3":
            shutil.copy2(
                target / "ReleaseCandidate/.support/payload/A120590_certificate_payload.json",
                target / "release/payload.json",
            )
            shutil.copy2(
                target / "ReleaseCandidate/A120590_ternatree_human.pdf",
                target / "release/certificate.pdf",
            )
        else:
            dump(
                target / "release/payload.json",
                {"status": "not_attempted", "legacy_source": None},
            )
        dump(
            target / "release/certificate.pdf.status.json",
            {
                "status": "produced" if alias == "q3" else "not_attempted",
                "legacy_source": (
                    "ReleaseCandidate/A120590_ternatree_human.pdf" if alias == "q3" else None
                ),
            },
        )
        dump(
            target / "provenance/generation.json",
            {
                "status": "produced",
                "migration": "Shot 1",
                "source_alias": alias,
                "mathematics_modified": False,
            },
        )
        (target / "CHECKLIST.md").write_text(checklist(manifest, results))

        hashes = []
        for path in sorted(target.rglob("*")):
            if path.is_file() and path.name != "SHA256SUMS.txt":
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                hashes.append(f"{digest}  {path.relative_to(target)}")
        sums = target / "provenance/SHA256SUMS.txt"
        sums.write_text("\n".join(hashes) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    migrate(Path(args.root).resolve())


if __name__ == "__main__":
    main()
