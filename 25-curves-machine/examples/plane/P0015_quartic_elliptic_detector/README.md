# Quartic Elliptic Detector Study

        Stable case ID: `P0015`  
        Status: `verified_study`

        Regression study for detecting elliptic even-quartic models and comparing exact/modular series.

        ## Representations

        - `C01`: Even quartic Cartesian model
- `C02`: Klein-invariant description

        ## Replay

        From the repository root:

        ```bash
        python3 examples/plane/P0015_quartic_elliptic_detector/scripts/reproduce.py
        ```

        Filed replay commands:

        - `python3 even_quartic_klein.py`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `backends/plane_curves/search_analyze/quartic_elliptic_detector`
