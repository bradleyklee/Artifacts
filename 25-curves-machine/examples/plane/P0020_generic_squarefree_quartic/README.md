# Generic Squarefree Quartic Coverage

        Stable case ID: `P0020`  
        Status: `modular_order6_partial`

        Coverage record for generic squarefree quartics: lower orders excluded at declared bounds and order six found modularly.

        ## Representations

        - `C01`: Generic Cartesian quartic family

        ## Replay

        From the repository root:

        ```bash
        python3 examples/plane/P0020_generic_squarefree_quartic/scripts/reproduce.py
        ```

        Filed replay commands:

        - `python3 code/tools/verify_filed_case.py P0020`
- `mkdir -p ../../examples/plane/P0020_generic_squarefree_quartic/runs/replay_output && python3 algorithms/src/core/quartic_universal_bounds.py ../../examples/plane/P0007_q2_generic/results/model.json --output ../../examples/plane/P0020_generic_squarefree_quartic/runs/replay_output/q2_universal_bounds.json`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `branches/worktrees/sphere_curves/data/bounds`
- `branches/worktrees/sphere_curves/data/examples/quartic_order6`
