# Simple Even Quartic

        Stable case ID: `P0011`  
        Status: `exact_certificate`

        Curated exact reductive example imported from the mixed quartic factory corpus.

        ## Representations

        - `C01`: Cartesian plane coordinates

        ## Replay

        From the repository root:

        ```bash
        python3 examples/plane/P0011_simple_even_quartic/scripts/reproduce.py
        ```

        Filed replay commands:

        - `python3 code/tools/verify_filed_case.py P0011`
- `python3 src/exact_reductive_generic.py models/simple_even_quartic.json --order 2 --q-bound 5 --output /tmp/P0011_exact_reductive.json`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `branches/worktrees/sphere_curves/data/examples/quartic_order2/simple_even_quartic_exact_reductive.json`
