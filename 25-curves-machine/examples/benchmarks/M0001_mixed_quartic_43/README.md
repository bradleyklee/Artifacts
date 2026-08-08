# Mixed Quartic 43-Model Benchmark

        Stable case ID: `M0001`  
        Status: `43_of_43_mode_agreement`

        Balanced 43-model plane-polynomial benchmark with inductive/reductive mode agreement for every row.

        ## Representations

        - `C01`: Cartesian polynomial models

        ## Replay

        From the repository root:

        ```bash
        python3 examples/benchmarks/M0001_mixed_quartic_43/scripts/reproduce.py
        ```

        Filed replay commands:

        - `python3 code/tools/verify_filed_case.py M0001`
- `python3 src/build_mixed_benchmark.py`
- `python3 src/run_benchmark.py --workers 4 --recompute`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `branches/worktrees/sphere_curves/data/benchmark`
