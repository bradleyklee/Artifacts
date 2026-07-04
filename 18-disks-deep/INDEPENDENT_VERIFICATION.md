# Independent verification task for Artifact 18

Artifact 18 includes the original producer so that the campaign can be rerun.
That producer is **not** independent evidence. For an independent audit, write
a separate exact two-body runner from `DATA_FORMAT.md`; do not port the Go
logic or call `bin/burner` from that runner.

## Required checks

1. **Delivered-data integrity.** Run `sha256sum -c SHA256SUMS`; then validate
   each chosen compact block's internal `SHA256SUMS`, its V3 stream lengths,
   and lane chain linkage. `make corpus-check` is a producer-side structural
   convenience, not an independent dynamics test.

2. **Fresh exact replay.** For every selected block, initialize only from its
   `start_state.json` and `BLOCK.json` geometry. For all 1,000 local events:

   - compute the next event with exact arithmetic;
   - reject a tie/corner/non-singleton candidate rather than imposing an order;
   - compare kind against `event_codes.u8`;
   - whenever the stream marks a polygon-polygon event, compare the active
     face with aligned `pair_steps.u16` and `pair_faces.u8`;
   - compare absolute exact time, both labelled positions, and both labelled
     velocities against `end_state.json` after event 1,000.

3. **Telemetry cross-check.** For a replayed block, derive post-event bit
   lengths from independently recomputed exact absolute times and compare the
   fields supplied in that block's `complexity.csv.gz`.

4. **Integer-word provenance.** Run `make words-check` before using a saved
   residue word. It verifies that each word is the specified quotient of the
   chronological native pair word derived from the recorded 50,000-event lane.
   For d12, its first term is the separately retained `INITIAL_PAIR_FACE` at
   exact time zero, face 1; the remaining 9,999 terms come from compact-block
   labels. The compact d12 start state is already post-seed, so replaying a
   block alone must not add this event. To establish a word from physics rather
   than from supplied records, independently verify the centered seed contact,
   replay the continuation, then compare bytes and certificate digests.

5. **Report.** State precisely which blocks were replayed, implementation
   language and exact-number/sign-comparison strategy, elapsed results, first
   mismatch if any, and whether a terminal/tie case arose. Do not describe
   checksum agreement alone as a physics verification.

## Scope

The compact corpus is present: three 50-block lanes, each covering recorded
events 1–50,000. d12 additionally retains a documented initial pair contact
at event step 0 for whole-experiment integer-word extraction. No subset is selected or concealed by this packet. Every block is
self-starting from its exact embedded state, so the reviewer may select a
cross-lane, early/middle/late slice plan or replay the whole corpus.

## What a pass establishes

A fresh replay pass for a given block shows agreement on its full 1,000-event
kind/face stream and exact endpoint from that embedded start state. It does not
prove any block that has not been replayed.
