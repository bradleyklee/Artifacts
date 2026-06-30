# Transfer packet

Treat `reference/` and the legacy finisher payload as examples, not truth.
The authoritative rebuilt records are Go outputs under `data/`, with matching
Python reports in `check/`.

## First commands

```sh
make test
make check
python3 scripts/derive_sequences_and_symmetry.py
```

## Rebuild order

1. `cmd/lattice` / `internal/engine` is canonical. Do not add floating-point
   physics or silently serialize simultaneous contact batches.
2. Re-run a low atlas and its `scripts/postcheck_go.py` report before changing
   an experimental claim.
3. Promote a candidate only by writing a v2 full certificate and independent
   report. Use compact checkpoints only for longer progress scans.
4. Regenerate videos only from checked certificates. The renderer accepts no
   manually entered geometry.
5. Preserve the distinction between a finite regular survivor and a proof of
   chaos.

## Present evidence

* Squares: negative `L=2,N=4` control.
* Ordinary dodecagons: negative `N=2` controls.
* Centered dodecagon: special seed; one-sided finite complexity-ray evidence;
  lex-min face-1 `(E,N)` video representative.
* 24-gon: ordinary two-body cardinal-lattice threshold; two D4/time-reversed
  classes shown in a stacked video.
