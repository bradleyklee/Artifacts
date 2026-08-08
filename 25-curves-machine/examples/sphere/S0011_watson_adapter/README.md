# Watson Physics Adapter

        Stable case ID: `S0011`  
        Status: `verified_adapter`

        Filed sphere calculation/study from the verified sphere branch.

        ## Representations

        - `C01`: Ambient Cartesian sphere coordinates
- `C02`: Action-angle or quotient representation

        ## Replay

        From the repository root:

        ```bash
        python3 examples/sphere/S0011_watson_adapter/scripts/reproduce.py
        ```

        Filed replay commands:

        - `mkdir -p ../../examples/sphere/S0011_watson_adapter/runs/replay_output/examples/sphere_curves && CURVES_MACHINE_DATA_ROOT=../../examples/sphere/S0011_watson_adapter/runs/replay_output python3 algorithms/scripts/replay_watson_physics_adapter.py`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `branches/worktrees/sphere_curves/data/examples/sphere_curves/watson_physics_adapter.json`
