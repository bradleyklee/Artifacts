# A303790 cubic note transfer packet

Start with `TRANSFER_PACKET.md`.

To regenerate and verify everything:

```text
python run_all.py
python -m pytest -q
```

The package is self-contained and uses exact symbolic calculations for all
critical points, factorizations, recurrences, and certificates. Floating-point
sampling is used only to draw the exact algebraic curves.
