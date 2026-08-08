# Mechanical Rotated 02

        Stable case ID: `P0013`  
        Status: `exact_certificate`

        Curated exact reductive example imported from the mixed quartic factory corpus.

        ## Representations

        - `C01`: Cartesian plane coordinates

        ## Replay

        From the repository root:

        ```bash
        python3 examples/plane/P0013_mechanical_rotated_02/scripts/reproduce.py
        ```

        Filed replay commands:

        - `python3 code/tools/verify_filed_case.py P0013`
- `python3 src/exact_reductive_generic.py ../mixed_quartic_benchmark/models/mechanical_rotated_02.json --order 2 --q-bound 6 --output /tmp/P0013_exact_reductive.json`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `branches/worktrees/sphere_curves/data/examples/quartic_order2/mechanical_rotated_02_exact_reductive.json`
