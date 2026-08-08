# Icosahedral Plus Jz

        Stable case ID: `S0006`  
        Status: `blocked_partial`

        Odd perturbation of the normalized icosahedral model; completed data retained at the external time limit.

        ## Representations

        - `C01`: Perturbed action-angle model
- `C02`: Eliminated polynomial model

        ## Replay

        From the repository root:

        ```bash
        python3 examples/sphere/S0006_icosahedral_plus_z/scripts/reproduce.py
        ```

        Filed replay commands:

        - `python3 code/tools/verify_filed_case.py S0006`
- `mkdir -p ../../examples/sphere/S0006_icosahedral_plus_z/runs/replay_output/examples/sphere_curves && CURVES_MACHINE_DATA_ROOT=../../examples/sphere/S0006_icosahedral_plus_z/runs/replay_output python3 algorithms/scripts/run_icosahedral_perturbation.py z`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `branches/worktrees/sphere_curves/data/examples/sphere_curves/icosahedral_perturbation_z.json`
