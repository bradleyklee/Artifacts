# Tetrahedral Sphere Model

        Stable case ID: `S0003`  
        Status: `exact_certificate`

        Exact tetrahedral sphere calculation closed in action-angle coordinates.

        ## Representations

        - `C01`: Ambient Cartesian sphere coordinates
- `C02`: Action-angle coordinates

        ## Replay

        From the repository root:

        ```bash
        python3 examples/sphere/S0003_tetrahedral/scripts/reproduce.py
        ```

        Filed replay commands:

        - `mkdir -p ../../examples/sphere/S0003_tetrahedral/runs/replay_output/examples/sphere_curves && CURVES_MACHINE_DATA_ROOT=../../examples/sphere/S0003_tetrahedral/runs/replay_output python3 algorithms/scripts/replay_tetrahedral_sphere.py`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `branches/worktrees/sphere_curves/data/examples/sphere_curves/tetrahedral_exact_certificate.json`
