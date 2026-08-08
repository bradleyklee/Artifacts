# Degree and Support Bounds Corpus

Stable case ID: `M0002`  
Status: `coverage_data`

Order/degree/support bound records used by plane and sphere search procedures.

## Representations

- `C01`: Symbolic coefficient/bound space

## Replay

From the repository root:

```bash
python3 examples/benchmarks/M0002_degree_and_support_bounds/scripts/reproduce.py
```

Filed replay commands:

- `python3 algorithms/src/core/even_sphere_degree_bounds.py`

Expensive commands are skipped unless `--full` is supplied.

## Imported sources

- `branches/worktrees/sphere_curves/data/bounds`
