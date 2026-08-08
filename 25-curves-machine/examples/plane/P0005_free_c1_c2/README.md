# Free c1,c2 Triangle-Rectangle Family

        Stable case ID: `P0005`  
        Status: `symbolic_operator`

        Symbolic free-coefficient family and specialization grid retained from the independent comparison implementation.

        ## Representations

        - `C01`: Cartesian coefficient family

        ## Replay

        From the repository root:

        ```bash
        python3 examples/plane/P0005_free_c1_c2/scripts/reproduce.py
        ```

        Filed replay commands:

        - `python3 verify_free_specializations.py free_coefficients_symbolic_result.json`
- `python3 benchmark_free_specializations.py --help`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `backends/pierre_comparison/cases/elliptic_free_coefficients.json`
- `backends/pierre_comparison/timing/free_coefficients_symbolic_result.json`
