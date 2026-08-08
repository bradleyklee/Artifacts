# Platonic Plane-Sphere Bridge Corpus

        Stable case ID: `B0001`  
        Status: `mixed_exact_numeric`

        Exact and numerical maps connecting octahedral/icosahedral sphere quotients, even quartics, and Triangle-Rectangle models.

        ## Representations

        - `C01`: Sphere-side models
- `C02`: Elliptic quotient models
- `C03`: Plane-curve models

        ## Replay

        From the repository root:

        ```bash
        python3 examples/bridges/B0001_platonic_plane_sphere_bridges/scripts/reproduce.py
        ```

        Filed replay commands:

        - `python3 code/tools/verify_filed_case.py B0001`
- `python3 code/verify_icosahedral_branchpoint_tschirnhaus_map_v1.py`
- `python3 code/verify_icosahedral_quotient_to_even_quartic_exact_proof_v1.py`
- `for f in code/verify_*.py; do python3 "$f"; done`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `backends/sphere_curves/platonic_bridge`
