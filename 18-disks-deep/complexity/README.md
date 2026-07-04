# Supplied complexity telemetry

Each lane has a complete CSV and an SVG graph over accepted collisions 1–50,000.
`total_bits` is the producer’s common-denominator exact-clock coordinate measure:
the bit length of one positive common denominator plus the bit lengths of the
four corresponding common-basis numerators.

These files are retained prominently because they are the delivered long-run
growth evidence. They are **not mechanically reconstructible from the compact
blocks alone**: compact `complexity.csv.gz` files keep individual reduced
coefficient numerator/denominator bit lengths, but omit the per-event common
denominator and common numerator bit fields used to make `total_bits`.

A fresh exact replay can regenerate this quantity for any replayed event or
block. A claim about the entire plotted series requires either replaying the
full corpus or treating these CSVs as supplied producer telemetry rather than
independently regenerated evidence.
