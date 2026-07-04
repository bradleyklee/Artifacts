# Validation

Development-only checks.  They are not part of `reference/`.

```sh
python3 validation/check_claude.py
```

This compares the 160 exchanged values, ignoring only the different `S`/`n`
labels in the two files.
