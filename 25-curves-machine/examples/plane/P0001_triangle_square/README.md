# Triangle-Square

        Stable case ID: `P0001`  
        Status: `exact_certificate`

        Baseline exact order-two plane-curve example retained as a cross-method regression case.

        ## Representations

        - `C01`: Cartesian plane coordinates

        ## Replay

        From the repository root:

        ```bash
        python3 examples/plane/P0001_triangle_square/scripts/reproduce.py
        ```

        Filed replay commands:

        - `python3 lairez_port.py cases/triangle_square.json --max-order 5 --json-output /tmp/triangle_square_lairez.json`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `backends/sphere_curves/data/examples/triangle_square`
- `backends/pierre_comparison/cases/triangle_square.json`
