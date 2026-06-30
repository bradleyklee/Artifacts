# Review prompt: exact lattice-polygon claims

Audit the following claims without assuming the producer is correct.

1. **Square negative control.** Verify that the stated `L=2,N=4` scan contains
   all 256 ordered cardinal velocity words on the only four occupied centroids,
   and has no `CAP` result under the declared strict batch rule.
2. **Ordinary dodecagon negative control.** Verify the complete `L=2,N=2` and
   `L=3,N=2` cardinal/lattice atlases have no `CAP` result through 100 batches.
3. **Centered dodecagon positive finite prefix.** Replay the full
   `centered_dodecagon_f1_EN_cap2000.json` certificate from its embedded seed.
   Confirm every globally earliest contact, every collision response, and the
   face-mod-3 sequence. Do not upgrade finite `CAP` to chaos.
4. **Past branch.** Replay `centered_dodecagon_f1_EN_reverse_stem.json` from its
   explicit velocity-negated resolved state; confirm the three-batch terminal.
5. **24-gon pair.** Replay both class-A and class-B full certificates and verify
   direct velocity negation maps `(E,S)` to `(W,N)` at the same sites.
6. **Simultaneous batches.** Search for a disjoint same-time batch and a shared
   one. Ensure the declared v2 policy resolves only the former.

Relevant primary inputs:

```text
../docs/EXPERIMENT_CONTRACT.md
../docs/CERTIFICATE_FORMAT.md
../data/square_L2_N4/atlas.json
../data/dodecagon_L2_N2/atlas.json
../data/dodecagon_L3_N2/atlas.json
../data/dodecagon_centered/certificates/centered_dodecagon_f1_EN_cap2000.json
../data/dodecagon_centered/certificates/centered_dodecagon_f1_EN_reverse_stem.json
../data/24gon_L2_N2/certificates/24gon_L2_N2_class_A_ES_cap100.json
../data/24gon_L2_N2/certificates/24gon_L2_N2_class_B_WN_cap100.json
../check/*.python.json
```

Report any disagreement as a concrete earliest event, exact coordinate, face
label, or batch-class mismatch. Treat an inability to replay a record as an
unresolved issue, not confirmation.
