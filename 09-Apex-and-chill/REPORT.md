# DH12 Apex 852 Final Extraction

This packet archives the DH12 C6 local-rule search state after the 696 plateau was broken and the current best result reached **852 cells**.

## Certified Apex

- Model: `dh12` two-tile / six-orientation C6 search model
- Final target certification used in late sweeps: target level 5
- Level-5 target size: 15,840 cells
- Current best cell count: **852**
- Best known depth at 852: **60**
- Status: `CLOSED_CHILL`

## Best candidates

- Verified 852 replay: `a2804b864d9556bb`, 852 cells, depth 57, source dh12_anti_knob_852_results.zip
- Slowest 852 candidate: `b388dc860d68030f`, depth 60, source dh12_pool_diff_continue_results.zip
- Fastest 852 candidate: `ff338fe79dcc5a3a`, depth 55, source dh12_target5_quick_sweep_results.zip

## Data scanned

- Total records scanned: 5853
- Unique rule hashes scanned: 4805
- Unique 800+ records archived: 467
- Unique 852 records archived: 209

## Search conclusion

The 852 plateau is robust. Many mutate/mate/anti-mate and differential operator families reproduce 852, but the only clear improvement over the old 696 plateau was the looser anti-knob / accept-biased family. Subsequent method tournaments did not produce >852.

The remaining technically distinct next experiment is a context-sensitive late-wall exception layer: do not globally accept wall rules; allow sparse overrides only when the late 852 wall context appears.
