# Mechanical Rotated 03

        Stable case ID: `P0014`  
        Status: `exact_certificate`

        Curated exact reductive example imported from the mixed quartic factory corpus.

        ## Representations

        - `C01`: Cartesian plane coordinates

        ## Replay

        From the repository root:

        ```bash
        python3 examples/plane/P0014_mechanical_rotated_03/scripts/reproduce.py
        ```

        Filed replay commands:

        - `python3 code/tools/verify_filed_case.py P0014`
- `python3 src/exact_reductive_generic.py ../mixed_quartic_benchmark/models/mechanical_rotated_03.json --order 2 --q-bound 6 --output /tmp/P0014_exact_reductive.json`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `branches/worktrees/sphere_curves/data/examples/quartic_order2/mechanical_rotated_03_exact_reductive.json`
