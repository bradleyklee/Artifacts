# Physics Generating-Sphere Study

        Stable case ID: `S0010`  
        Status: `verified_study`

        Filed sphere calculation/study from the verified sphere branch.

        ## Representations

        - `C01`: Ambient Cartesian sphere coordinates
- `C02`: Action-angle or quotient representation

        ## Replay

        From the repository root:

        ```bash
        python3 examples/sphere/S0010_physics_generating/scripts/reproduce.py
        ```

        Filed replay commands:

        - `mkdir -p ../../examples/sphere/S0010_physics_generating/runs/replay_output/examples/sphere_curves && CURVES_MACHINE_DATA_ROOT=../../examples/sphere/S0010_physics_generating/runs/replay_output python3 algorithms/scripts/replay_physics_generating_sphere.py`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `branches/worktrees/sphere_curves/data/examples/sphere_curves/physics_generating_function_stats.json`
