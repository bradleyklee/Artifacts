# Dihedral Sphere Comparison

        Stable case ID: `S0008`  
        Status: `verified_study`

        Filed sphere calculation/study from the verified sphere branch.

        ## Representations

        - `C01`: Ambient Cartesian sphere coordinates
- `C02`: Action-angle or quotient representation

        ## Replay

        From the repository root:

        ```bash
        python3 examples/sphere/S0008_dihedral_comparison/scripts/reproduce.py
        ```

        Filed replay commands:

        - `python3 code/tools/verify_filed_case.py S0008`
- `python3 algorithms/scripts/replay_dihedral_sphere_comparison.py`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `branches/worktrees/sphere_curves/data/examples/sphere_curves/dihedral_sphere_comparison.json`
