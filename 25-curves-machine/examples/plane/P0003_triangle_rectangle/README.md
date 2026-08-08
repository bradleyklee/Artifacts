# Triangle-Rectangle

        Stable case ID: `P0003`  
        Status: `exact_certificate_showcase`

        Genus-one must-have example with exact certificate, Abel identity, and birational/hypergeometric transformation chain.

        ## Representations

        - `C01`: Cartesian plane coordinates
- `C02`: Jacobi quartic model
- `C03`: Legendre cubic model

        ## Replay

        From the repository root:

        ```bash
        python3 examples/plane/P0003_triangle_rectangle/scripts/reproduce.py
        ```

        Filed replay commands:

        - `python3 verify_certificate.py`
- `python3 scripts/verify_hypergeometric_transform_chain.py`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `certificates/raw/triangle_rectangle`
- `certificates/pretty/triangle_rectangle`
- `backends/pierre_comparison/cases/elliptic_must_have.json`
