# Certificate format

Every important positive record uses
`lattice-chaos-self-contained-certificate/v2`.

```text
schema, certificate_id, producer
model, container, dynamics
instance                         complete exact seed and any time-zero contact
stopping_rule                    cap / terminal / exact return policy
evolution.events[]               append-only exact global earliest-event ledger
result                           exact terminal/cap witness, state, metrics, word
independent_check_contract       checker obligations
```

Each full event row includes the exact absolute and incremental time,
all same-time contacts, pre/post labelled states, state hashes, and coefficient
metrics. A checker must reconstruct the model and seed from the file alone,
recompute the globally earliest event batch, and require exact batch and
post-state equality. It must not call the Go producer.

`lattice-chaos-compact-progress/v1` is deliberately weaker: it has every exact
batch, time, and state hash plus a final exact state, but does not duplicate the
full pre/post coordinates for every row. It is used for deep progress evidence,
not as a substitute for a full certificate.

The Python post-checker is an independent reimplementation of the run loop and
simultaneous-batch rule. It verifies every committed scan and highlighted
certificate from the emitted seed data.
