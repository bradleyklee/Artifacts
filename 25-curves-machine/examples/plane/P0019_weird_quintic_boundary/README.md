# Weird Quintic Boundary Case

Stable case ID: `P0019`  
Status: `inductive_only_blocked`

Quintic boundary case with modular holdout and bounded reductive search; exact reconstruction remains open.

## Representations

- `C01`: Cartesian polynomial coordinates

## Replay

From the repository root:

```bash
python3 examples/plane/P0019_weird_quintic_boundary/scripts/reproduce.py
```

Filed replay commands:

- `python3 code/tools/verify_filed_case.py P0019`

Expensive commands are skipped unless `--full` is supplied.

## Imported sources

- `branches/worktrees/sphere_curves/data/examples/quintic_boundary`
