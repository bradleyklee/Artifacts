# Reflection-XY Sphere Quartic

        Stable case ID: `S0002`  
        Status: `exact_order4_certificate`

        Reflection quotient lowers the generic even-quartic ceiling and closes at exact order four.

        ## Representations

        - `C01`: Ambient Cartesian sphere coordinates
- `C02`: Reflection-invariant quotient
- `C03`: Hyperelliptic reduction

        ## Replay

        From the repository root:

        ```bash
        python3 examples/sphere/S0002_reflection_xy/scripts/reproduce.py
        ```

        Filed replay commands:

        - `mkdir -p ../../examples/sphere/S0002_reflection_xy/runs/replay_output/examples/sphere_curves ../../examples/sphere/S0002_reflection_xy/runs/replay_output/bounds && CURVES_MACHINE_DATA_ROOT=../../examples/sphere/S0002_reflection_xy/runs/replay_output python3 algorithms/scripts/replay_even_sphere_reflection.py`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `branches/worktrees/sphere_curves/data/examples/sphere_curves/reflection_xy_exact_certificate.json`
