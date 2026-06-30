# Executed status

The public low-family statements are fully backed by Go-produced atlases and
Python independent replay reports:

* `square_L2_N4`: zero cap survivors across all 256 starts.
* `dodecagon_L2_N2` and `dodecagon_L3_N2`: zero cap survivors across all 672
  ordinary cardinal/lattice pair starts.
* `dodecagon_centered`: 16 raw cap-500 runners across 68 all-face centered
  starts, reducing to two ternary words. Lex-min is `face=1, incoming=(E,N)`.
* `24gon_L2_N2`: 16 raw cap-100 runners across 96 starts, reducing to two
  D4 classes. They are time reversals at the same sites.
* `octagon_L2_N3`: retained context atlas; 16 raw cap-256 runners, two D4
  classes.

Important certificates:

```text
data/dodecagon_centered/certificates/centered_dodecagon_f1_EN_cap500.json
data/dodecagon_centered/certificates/centered_dodecagon_f1_EN_cap2000.json
data/dodecagon_centered/certificates/centered_dodecagon_f1_EN_reverse_stem.json
data/dodecagon_centered/centered_dodecagon_f1_EN_cap4000_compact.json
data/dodecagon_centered/centered_dodecagon_f1_EN_cap6000_compact.json
data/dodecagon_centered/centered_dodecagon_f1_EN_cap7500_compact.json
data/24gon_L2_N2/certificates/24gon_L2_N2_class_A_ES_cap100.json
data/24gon_L2_N2/certificates/24gon_L2_N2_class_B_WN_cap100.json
```

Every listed full certificate has a matching `check/*.python.json` independent
report. The compact 7,500-event dodecagon checkpoint also has one.
