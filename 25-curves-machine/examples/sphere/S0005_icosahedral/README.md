# Normalized Icosahedral Sphere Model

        Stable case ID: `S0005`  
        Status: `exact_certificate`

        Normalized icosahedral sextic with exact order-two operator and primitive after angular elimination.

        ## Representations

        - `C01`: Ambient Cartesian sphere coordinates
- `C02`: Fivefold action-angle chart
- `C03`: Eliminated hyperelliptic model

        ## Replay

        From the repository root:

        ```bash
        python3 examples/sphere/S0005_icosahedral/scripts/reproduce.py
        ```

        Filed replay commands:

        - `mkdir -p ../../examples/sphere/S0005_icosahedral/runs/replay_output/examples/sphere_curves && CURVES_MACHINE_DATA_ROOT=../../examples/sphere/S0005_icosahedral/runs/replay_output python3 algorithms/scripts/replay_icosahedral_sphere.py`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `branches/worktrees/sphere_curves/data/examples/sphere_curves/icosahedral_search.json`
- `branches/worktrees/sphere_curves/data/examples/sphere_curves/icosahedral_normalization_audit.json`
