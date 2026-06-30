# Independent checker brief

The production engine is Go (`internal/engine`, invoked through `cmd/lattice`).
The post-checker is Python (`scripts/postcheck_go.py`) and does not invoke Go.
It re-creates every start from the emitted JSON, independently enumerates all
wall and pair candidates, applies the declared disjoint-batch policy, and
checks exact times, contact labels, face words, metrics, and (for full
certificates) every pre/post state.

Run:

```sh
python3 scripts/postcheck_go.py data/.../atlas.json --out check/...python.json
python3 scripts/postcheck_go.py data/.../certificate.json --out check/...python.json
```

The `lattice_collision/` Python package is retained as an exact-geometry
reference implementation. Its historical `run()` is not the authority for the
v2 batch policy; the post-checker contains its own explicit run loop so that
valid disjoint pair batches are resolved rather than stopped.
