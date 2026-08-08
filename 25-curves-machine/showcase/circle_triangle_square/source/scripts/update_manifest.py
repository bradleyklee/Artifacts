#!/usr/bin/env python3
"""Update recursive SHA-256 manifests for the embedded payload and project."""
from __future__ import annotations
import argparse, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PAYLOAD=ROOT/'payload'

def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_payload_manifest()->None:
    embedded=[
      'README_AUTONOMOUS_REVIEW.txt','certificate_payload.json','certificate_source.tex',
      'claim_index.json','generate_figure.py','generate_quantized_levels.py',
      'quantization_spec.json','SOURCE_BUNDLE_STANDARD.md','quantized_levels_for_figure.csv',
      'verification_output.txt','verification_results.json','verify_certificate.py'
    ]
    files=[PAYLOAD/name for name in embedded]
    missing=[p.name for p in files if not p.is_file()]
    if missing: raise SystemExit('missing embedded payload files: '+', '.join(missing))
    (PAYLOAD/'MANIFEST.sha256').write_text('\n'.join(f'{digest(p)}  {p.name}' for p in files)+'\n')
    print('wrote payload/MANIFEST.sha256')

def write_project_manifest()->None:
    excluded={'PROJECT_MANIFEST.sha256','certificate_source.aux','certificate_source.log','certificate_source.out','certificate_source.pdf'}
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name not in excluded)
    (ROOT/'PROJECT_MANIFEST.sha256').write_text('\n'.join(f'{digest(p)}  {p.relative_to(ROOT).as_posix()}' for p in files)+'\n')
    print('wrote PROJECT_MANIFEST.sha256')

def main()->None:
    ap=argparse.ArgumentParser(); g=ap.add_mutually_exclusive_group();
    g.add_argument('--payload-only',action='store_true');g.add_argument('--project-only',action='store_true');a=ap.parse_args()
    if a.project_only: write_project_manifest()
    elif a.payload_only: write_payload_manifest()
    else: write_payload_manifest();write_project_manifest()
if __name__=='__main__':main()
