#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from plane_scan import tacnode

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = ROOT / "examples" / "data" / "tacnode_quartic_result.json"


def main() -> None:
    holomorphic = tacnode.verify(tacnode.HOLOMORPHIC_EXAMPLE)
    meromorphic = tacnode.verify(tacnode.MEROMORPHIC_EXAMPLE)
    payload = {
        "search": "one-fixed-tacnode harmonic quartic stratum",
        "status": "verified_new_plane_presentation_no_new_fiber_configuration",
        "quartic_genus_one_taxonomy": {
            "2+2": "two ordinary double points; implemented structured family gives 8 configurations",
            "2+1+1": "the double point must acquire delta 2; the A3 tacnode conditions are solved here",
            "3+1": "a multiplicity-three point has delta at least 3 and does not give a generic genus-one quartic",
            "4": "a multiplicity-four point has delta at least 6 and does not give a generic genus-one quartic",
        },
        "tacnode_parameterization": (
            "p^2+q^2+2s*p^2*q+v*p*q^2+w*q^3+s^2*p^2*q^2+s*v*p*q^3+c*q^4"
        ),
        "examples": {"T0_holomorphic": holomorphic, "T1_meromorphic": meromorphic},
        "conclusion": (
            "For A=v^2-4c nonzero, c4 and c6 have degrees 1 and 1 while Delta has degree 3; "
            "the fiber at infinity is III*. Generic finite roots are three I1 fibers. "
            "This stratum therefore adds plane models but not a new four-fiber configuration."
        ),
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n")
    print("wrote", OUTPUT)
    print(holomorphic["fibers"], holomorphic["delta"])
    print("time forms", holomorphic["time_form_type"], meromorphic["time_form_type"])


if __name__ == "__main__":
    main()
