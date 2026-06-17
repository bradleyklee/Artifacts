#!/usr/bin/env python3
"""Small stdlib PDF structure check for this release artifact.

This intentionally avoids third-party PDF libraries.  It is a shallow structure
check: page count, obvious image XObjects, URI links, and embedded-file markers.
The deep proof test is done from the visible SVG art source plus certificate
replay.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path


def count(pattern: bytes, data: bytes) -> int:
    return len(re.findall(pattern, data))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--out-json", required=True)
    args = ap.parse_args()
    p = Path(args.pdf)
    data = p.read_bytes()
    # Avoid counting /Type /Pages as a page object.
    pages = count(rb"/Type\s*/Page(?!s)\b", data)
    image_xobjects = count(rb"/Subtype\s*/Image\b", data)
    uri_links = count(rb"/URI\b", data)
    embedded_files = count(rb"/EmbeddedFile\b", data)
    ok = data.startswith(b"%PDF-") and pages == 1 and image_xobjects == 0
    out = {
        "ok": ok,
        "pdf": str(p),
        "pages": pages,
        "image_xobjects": image_xobjects,
        "uri_links": uri_links,
        "embedded_files": embedded_files,
        "method": "stdlib regex scan of PDF object bytes",
    }
    Path(args.out_json).write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
