# Even Sphere Refinement Study

        Stable case ID: `S0009`  
        Status: `data_study`

        Filed sphere calculation/study from the verified sphere branch.

        ## Representations

        - `C01`: Ambient Cartesian sphere coordinates
- `C02`: Action-angle or quotient representation

        ## Replay

        From the repository root:

        ```bash
        python3 examples/sphere/S0009_even_sphere_refinement/scripts/reproduce.py
        ```

        Filed replay commands:

        - `python3 code/tools/verify_filed_case.py S0009`
- `mkdir -p ../../examples/sphere/S0009_even_sphere_refinement/runs/replay_output/examples/sphere_curves && cp ../../examples/sphere/S0009_even_sphere_refinement/results/even_quartic_catalog.json ../../examples/sphere/S0009_even_sphere_refinement/runs/replay_output/examples/sphere_curves/ && CURVES_MACHINE_DATA_ROOT=../../examples/sphere/S0009_even_sphere_refinement/runs/replay_output python3 algorithms/scripts/run_even_sphere_refinement_loop.py`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `branches/worktrees/sphere_curves/data/examples/sphere_curves/even_sphere_refinement_stats.json`
- `branches/worktrees/sphere_curves/data/examples/sphere_curves/even_quartic_catalog.json`
