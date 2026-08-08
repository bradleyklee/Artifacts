# Icosahedral Plus Jz^2

        Stable case ID: `S0007`  
        Status: `order6_relation_partial`

        Even perturbation with first exact rank dependence at order six; operator normalization and primitive reconstruction remain open.

        ## Representations

        - `C01`: Perturbed action-angle model
- `C02`: Even-power reduction

        ## Replay

        From the repository root:

        ```bash
        python3 examples/sphere/S0007_icosahedral_plus_z2/scripts/reproduce.py
        ```

        Filed replay commands:

        - `python3 code/tools/verify_filed_case.py S0007`
- `mkdir -p ../../examples/sphere/S0007_icosahedral_plus_z2/runs/replay_output/examples/sphere_curves && CURVES_MACHINE_DATA_ROOT=../../examples/sphere/S0007_icosahedral_plus_z2/runs/replay_output python3 algorithms/scripts/run_icosahedral_perturbation.py z2`
- `mkdir -p ../../examples/sphere/S0007_icosahedral_plus_z2/runs/replay_output/examples/sphere_curves && CURVES_MACHINE_DATA_ROOT=../../examples/sphere/S0007_icosahedral_plus_z2/runs/replay_output python3 algorithms/scripts/screen_icosahedral_columns.py z2 --max-order 6`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `branches/worktrees/sphere_curves/data/examples/sphere_curves/icosahedral_perturbation_z2.json`
- `branches/worktrees/sphere_curves/data/examples/sphere_curves/icosahedral_perturbation_z2_columns.json`
