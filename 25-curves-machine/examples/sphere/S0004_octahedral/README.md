# Octahedral Sphere Model

        Stable case ID: `S0004`  
        Status: `exact_multi_chart_certificate`

        One octahedral model with exact direct-chart and invariant-quotient certificates and a verified pullback relation.

        ## Representations

        - `C01`: Ambient Cartesian sphere coordinates
- `C02`: Direct squared/action chart
- `C03`: Reflection-invariant chart

        ## Replay

        From the repository root:

        ```bash
        python3 examples/sphere/S0004_octahedral/scripts/reproduce.py
        ```

        Filed replay commands:

        - `python3 scripts/check_filed_equivalence.py`
- `python3 algorithms/scripts/replay_even_sphere_octahedral.py`
- `python3 algorithms/scripts/replay_dihedral_sphere_comparison.py`

        Expensive commands are skipped unless `--full` is supplied.

        ## Imported sources

        - `branches/worktrees/sphere_curves/data/examples/sphere_curves/octahedral_direct_degree7_certificate.json`
- `branches/worktrees/sphere_curves/data/examples/sphere_curves/octahedral_exact_invariant_certificate.json`
