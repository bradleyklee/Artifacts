# Unrestricted Single-Harmonic Catalog

        Stable case ID: `S0012`  
        Status: `benchmark_study`

        Filed sphere calculation/study from the verified sphere branch.

        ## Representations

        - `C01`: Ambient Cartesian sphere coordinates
- `C02`: Action-angle or quotient representation

        ## Replay

        From the repository root:

        ```bash
        python3 examples/sphere/S0012_single_harmonic_catalog/scripts/reproduce.py
        ```

        Filed replay commands:

        - `python3 code/tools/verify_filed_case.py S0012`
- `mkdir -p ../../examples/sphere/S0012_single_harmonic_catalog/runs/replay_output/examples/sphere_curves && CURVES_MACHINE_DATA_ROOT=../../examples/sphere/S0012_single_harmonic_catalog/runs/replay_output python3 algorithms/scripts/replay_unrestricted_single_harmonic.py`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `branches/worktrees/sphere_curves/data/examples/sphere_curves/unrestricted_single_harmonic_benchmark.json`
- `branches/worktrees/sphere_curves/data/examples/sphere_curves/showcase_period_data.json`
