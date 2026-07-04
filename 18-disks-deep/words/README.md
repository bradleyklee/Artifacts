# Artifact 18 integer words

Each `.txt` file is one plain comma-separated sequence of 10,000 decimal
residues. Terms are in chronological polygon-polygon (`PAIR`) order and then
reduced as named by the file. The compact block lanes cover recorded steps
1–50,000. **d12 additionally has one documented `INITIAL_PAIR_FACE` at exact
time zero: face 1 is term 0 before reduction.** Thus its 10,000-term files
contain that seed term plus the first 9,999 pair labels from recorded blocks.
24A and 24B have no declared time-zero pair contact. No timestamps, wall
markers, coordinates, or record tuples appear in these files.

For a regular `N`-gon, the two retained views are exactly:

- `mod N/2`: opposite-face (antipodal) identification;
- `mod N/4`: quadrupole identification.

Thus this directory contains `d12` modulo 6 and 3, and `24A` / `24B` modulo 12
and 6.

`make words-print WORD_TERMS=50` is a read-only prefix display. It checks every saved word file against its manifest checksum; for d12 mod 3 and every mod-6 view, it then recertifies the complete retained 50,000-event lane, verifies that the saved 10,000-term word is its prefix, and prints a base-10 prefix only when the 10,000-term and complete-stream intervals force the same digits. These are numeric views of the same sequences, not additional codes.

`make words-check` is the required derivation check. It traverses the complete
50,000-event compact lane for each model; verifies every block's internal
checksums, exact end/start chain linkage, event-kind stream, and face/step
alignment; and for d12 cross-checks the retained seed manifest and its raw
step-0 `pair_faces.csv` row before recomputing and byte-comparing all six
saved words.

`WORDS_CERTIFICATE.json` records the resulting whole-lane and prefix digests.
It certifies that these files are derived from the recorded corpus—not that the
recorded dynamics are independently correct. That remains the exact-replay
review task.
