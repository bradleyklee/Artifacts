# Package contents and merge decision

The merge is intentionally additive:

- The publication PDF/certificate layer is kept intact under `data/v88_pdf_packet`.
- Seed/search-result records are kept intact under `data/dh12_seed_data`.
- The older search transfer document is kept as documentation only; it is not
  treated as runnable code because its summary says `search_code_included: false`.
- New generated outputs go only under `build/` and are reproducible through the
  Makefile.

The main release command is:

```bash
make test
```

The optional exploratory command is:

```bash
make search
```

The 48-rule card command is:

```bash
make rules-card
```
