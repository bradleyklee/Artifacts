# Square-Hexagon

        Stable case ID: `P0002`  
        Status: `exact_certificate`

        Closed order-four plane-curve certificate with finite-support closure, reduced primitive, and a human certificate.

        ## Representations

        - `C01`: Cartesian plane coordinates

        ## Replay

        From the repository root:

        ```bash
        python3 examples/plane/P0002_square_hexagon/scripts/reproduce.py
        ```

        Filed replay commands:

        - `python3 exact/verify_merged_certificate.py`
- `python3 exact/verify_reduced_primitive.py`
- `python3 exact/derive_deductive_certificate.py`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `backends/plane_curves/square_hexagon_current`
