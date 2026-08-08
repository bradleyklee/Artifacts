# Generic Asymmetric Q2 Quartic

        Stable case ID: `P0007`  
        Status: `exact_order6_certificate`

        Dense asymmetric squarefree quartic with exact order-six operator, 100-term verification, degree bounds, and a large primitive certificate.

        ## Representations

        - `C01`: Cartesian quartic coordinates

        ## Replay

        From the repository root:

        ```bash
        python3 examples/plane/P0007_q2_generic/scripts/reproduce.py
        ```

        Filed replay commands:

        - `python3 scripts/verify_q2_exact_operator.py data/q2_operator_exact.json data/q2_series_100.json --output /tmp/q2_verify.json`
- `python3 scripts/verify_q2_certificate_from_json.py --model data/q2_generic.json --src src --operator-verified data/q2_operator_exact_verified.json --certificate data/q2_primitive_certificate_shift.json`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `backends/plane_curves/search_analyze/q2_order6_engine`
