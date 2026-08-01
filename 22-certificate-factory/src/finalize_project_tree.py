#!/usr/bin/env python3
"""Canonicalize referenced data and stage superseded project history."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = Path("/tmp/certificate_factory_final_cleanup_2026-07-31")


def pointer_get(document, pointer):
    value = document
    for token in pointer.strip("/").split("/"):
        if token:
            value = value[token.replace("~1", "/").replace("~0", "~")]
    return value


def materialize(relative_file):
    target = ROOT / relative_file
    wrapper = json.loads(target.read_text())
    reference = wrapper["canonical_source"]
    source_name, pointer = reference.split("#", 1)
    source = ROOT / source_name if source_name.startswith("runs/") else target.parents[1] / source_name
    value = pointer_get(json.loads(source.read_text()), pointer)
    if isinstance(value, dict):
        value = dict(value)
        value.setdefault("status", "verified")
        value["canonicalized_from"] = reference
    target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def stage(path, entries):
    if not path.exists() and not path.is_symlink():
        return
    relative = path.relative_to(ROOT)
    destination = STAGE / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    size = path.stat().st_size if path.is_file() else sum(p.stat().st_size for p in path.rglob("*") if p.is_file())
    if path.is_file() and not path.is_symlink():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
    else:
        digest = None
    shutil.move(str(path), str(destination))
    entries.append({"path": str(relative), "bytes": size, "sha256": digest})


def main():
    if STAGE.exists():
        raise SystemExit(f"recovery stage already exists: {STAGE}")

    references = [
        "examples/A120588/data/ode.json",
        "examples/A120590/data/ode.json",
        "examples/A120592/data/certificate.json",
        "examples/A120592/data/matrices.json",
        "examples/A120592/data/ode.json",
        "examples/A120592/data/recurrence.json",
        "examples/A120593/data/ode.json",
        "examples/A120596/data/ode.json",
        "examples/A120600/data/certificate.json",
        "examples/A120600/data/matrices.json",
        "examples/A120600/data/ode.json",
        "examples/A120600/data/recurrence.json",
        "examples/A244594/data/certificate.json",
        "examples/A244594/data/matrices.json",
        "examples/A244594/data/ode.json",
        "examples/A244594/data/recurrence.json",
        "examples/A244627/data/certificate.json",
        "examples/A244627/data/matrices.json",
        "examples/A244627/data/ode.json",
        "examples/A244627/data/recurrence.json",
        "examples/A244856/data/matrices.json",
    ]
    for item in references:
        materialize(item)

    entries = []
    # Promote the final physical certificate names and remove compatibility aliases.
    for release in sorted(ROOT.glob("examples/A*/release")):
        canonical_pdf = release / "certificate.pdf"
        canonical_tex = release / "certificate.tex"
        physical_pdf = release / "certificate_WITH_RHO_AND_INLINE_MULTIPLICITIES.pdf"
        physical_tex = release / "certificate_WITH_RHO_AND_INLINE_MULTIPLICITIES.tex"
        if canonical_pdf.is_symlink():
            canonical_pdf.unlink()
        if canonical_tex.is_symlink():
            canonical_tex.unlink()
        physical_pdf.rename(canonical_pdf)
        physical_tex.rename(canonical_tex)
        for alias in release.glob("certificate_WITH_*"):
            stage(alias, entries)
        for extra in list(release.glob("*.gz")) + [release / "certificate.pdf.status.json", release / "certificate.building.pdf"]:
            stage(extra, entries)

    final_aggregate = ROOT / "release/ALL_23_CERTIFICATES.pdf"
    (ROOT / "release/ALL_23_CERTIFICATES_RHO_INLINE_v10.pdf").rename(final_aggregate)

    targets = [
        ROOT / "release/ALL_23_CERTIFICATES_RHO_INLINE_v9.pdf",
        ROOT / "release/HANNA_23_CALCULUS_CERTIFICATES.tex",
        ROOT / "CALCULUS_DIGEST_23_CASES.md",
        ROOT / "TRANSFER_2026-07-30.md",
        ROOT / "failures",
        ROOT / "runs",
        ROOT / "src/__pycache__",
        ROOT / "reports/PRUNING_LEDGER_2026-07-31.json",
        ROOT / "reports/PRUNING_LEDGER_2026-07-31.md",
        ROOT / "work/external_archive_inventory.json",
        ROOT / "work/NEW_WORK_WINDOW_PROMPT.txt",
    ]
    targets += list(ROOT.glob("work/SHOT*_2026-07-*.md"))
    targets += list(ROOT.glob("examples/A*/case.json"))
    targets += list(ROOT.glob("examples/A*/validation.json"))
    targets += list(ROOT.glob("examples/A120590/*.tsv"))
    targets += list(ROOT.glob("examples/A120590/*.txt"))
    targets += list(ROOT.glob("ALL_23_*.pdf"))
    targets += [p for p in (ROOT / "release").glob("*.pdf") if p.name != "ALL_23_CERTIFICATES.pdf"]
    targets += [p for p in (ROOT / "reports").iterdir() if p.name not in {
        "REVISION_QUALITY_AUDIT.json", "REVISION_QUALITY_AUDIT.md", "oeis_style_audit.json", "forensics"
    }]

    q3 = ROOT / "examples/q3/ReleaseCandidate"
    keep_support = {
        q3 / ".support/source/ternatree_one_page_crank_academic.txt",
        q3 / ".support/graphs/ternatree_pseudocode_mysteries.pdf",
        q3 / ".support/graphs/ternatree_sympy_resolutions.pdf",
    }
    targets += [p for p in (q3 / ".support").rglob("*") if p.is_file() and p not in keep_support]
    targets += [q3 / "ternatree_pseudocode_mysteries.png", q3 / "ternatree_sympy_resolutions.png", q3 / "ternatree_poetry_digest.pdf"]

    for target in sorted(set(targets), key=lambda p: (len(p.parts), str(p)), reverse=True):
        stage(target, entries)
    for directory in sorted((q3 / ".support").rglob("*"), reverse=True):
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()

    result = {
        "status": "canonicalized",
        "materialized_data_records": len(references),
        "staged_paths": len(entries),
        "staged_bytes": sum(x["bytes"] for x in entries),
        "recovery_stage": str(STAGE),
        "entries": entries,
    }
    report = ROOT / "reports/FINAL_TREE_CLEANUP.json"
    report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "materialized_data_records", "staged_paths", "staged_bytes", "recovery_stage")}))


if __name__ == "__main__":
    main()
