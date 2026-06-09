# DH12 Apex 852 Final Product

This directory is a standalone archival/search/render packet for the DH12 C6 local-rule search.

## What is included

- `data/summary.json` and `REPORT.md`: concise summary of the search state.
- `data/records/best/`: selected 852 records, including verified, fastest, and slowest candidates.
- `data/records/pools/`: deduplicated 800+, 852, and 69x pools in JSONL format.
- `mechanics/`: C6 target/replay mechanics and target catalogue data derived from REPHEX replacement rules.
- `scripts/generate_target_data.py`: regenerate simple JSON/CSV target data.
- `scripts/depict_record.py`: draw a final-state PNG from a record.
- `scripts/animate_record.py`: replay a record and render frames / MP4.
- `scripts/search.py`: simple mutate/mate/anti-mate search for future users.
- `videos/` and `images/`: verified 852 video and depictions.

## Quick start

```bash
make target
make depict
make video
make search
```

## Current Apex

Current certified best: **852 cells**, `CLOSED_CHILL`, target level 5 certified in later sweeps. Best known 852 depth is 60.

## Notes

The simple search script is intentionally conservative and easy to understand. It is not all of the experimental machinery used to find 852. It gives future users a clean starting point with three operators: mutate, mate, anti-mate.

If the project is resumed, the most promising next non-global idea is a context-sensitive late-wall exception layer: allow sparse overrides only in the late 852 wall context rather than accepting wall rules globally.

Video defaults are clean: fixed 1280x720 canvas, stable crop from final state, yellow/green wire palette, and a minimal sidebar. Use `--verbose-sidebar` or `--show-rules` only when needed.

Search status prints report mutate, mate, and anti-mate counts/bests separately during mixed runs.


## Simple usage

Generate target data:

```bash
make target
```

Generate a clean video:

```bash
make video
```

Optional video knobs:

```bash
make video WIDTH=1400 HEIGHT=900 TILE=12 SIDEBAR=260 FPS=2
```

Run the simple search:

```bash
make search
```

Search uses mutate, mate, and anti-mate in `OP=mixed` mode and prints separate status lines for all three methods. You can also run one method:

```bash
make search OP=mutate TRIALS=200
make search OP=mate TRIALS=200
make search OP=anti-mate TRIALS=200
```
