# Executed assembly log

This is a concise record of commands and outcomes, not a substitute for the
stored data.

```text
Go: go test ./...                                      PASS
Go: square L=2,N=4 exhaustive atlas (256 raw starts)   PASS
Go: dodecagon L=2,N=2 exhaustive atlas (96 starts)    PASS
Go: dodecagon L=3,N=2 exhaustive atlas (576 starts)   PASS
Go: centered dodecagon all-face atlas cap 500 (68)     PASS
Go: centered dodecagon off-cardinal atlas cap 500 (48) PASS
Go: 24-gon L=2,N=2 exhaustive atlas cap 100 (96)       PASS
Go: octagon L=2,N=3 context atlas cap 256 (256)        PASS
Go: dodecagon lex-min full cert cap 500                PASS
Go: dodecagon lex-min full cert cap 2000               PASS
Go: dodecagon lex-min compact checkpoint cap 4000, cap 6000, and cap 7500      PASS
Go: 24-gon A/B full certs cap 100                      PASS
Python: independent replay reports for all above       PASS
Python: ternary/D4 derivation                           PASS
Pillow/FFmpeg: two vertical Shorts                      PASS
```

The common-field Go engine did not complete an 8,000- or 12,000-batch centered
dodecagon run during this assembly. This packet therefore asserts only the
checked 7,500-batch compact checkpoint. `docs/PERFORMANCE_NOTES.md` records the
next optimisation target.
