#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import fitz
ATTACHMENTS=['MANIFEST.sha256','README_AUTONOMOUS_REVIEW.txt','certificate_payload.json','certificate_source.tex','quantized_levels_for_figure.csv','verification_output.txt','verification_results.json','continued_eisenstein_root_check.json','continued_eisenstein_root_check.csv','solution_basis_audit.json','solution_basis_audit.csv','claim_index.json','verify_certificate.py','verify_continued_eisenstein_root.py','generate_figure.py','generate_quantized_levels.py','quantization_spec.json','SOURCE_BUNDLE_STANDARD.md']
def main():
    ap=argparse.ArgumentParser();ap.add_argument('input_pdf',type=Path);ap.add_argument('output_pdf',type=Path);ap.add_argument('--payload-dir',type=Path,default=Path('payload'));args=ap.parse_args()
    missing=[n for n in ATTACHMENTS if not (args.payload_dir/n).is_file()]
    if missing:raise SystemExit('missing payload files: '+', '.join(missing))
    args.output_pdf.parent.mkdir(parents=True,exist_ok=True)
    doc=fitz.open(args.input_pdf)
    for n in ATTACHMENTS:
        path=args.payload_dir/n
        doc.embfile_add(n,path.read_bytes(),filename=n,ufilename=n,desc='Triangle Rectangle autonomous referee payload')
    doc.save(args.output_pdf,garbage=4,deflate=True,clean=True);doc.close()
if __name__=='__main__':main()
