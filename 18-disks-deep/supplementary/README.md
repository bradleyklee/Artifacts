# Supplementary retained source records

These files were present in the input archive and are retained so the handoff
does not discard supplied data. They are intentionally not part of the primary
verification path.

- `initial-block-source-records/` contains verbose producer records only for
  the first 1,000-event block of each lane. For d12, its manifest and first
  `pair_faces.csv` row are required provenance for the time-zero pair contact
  that begins the derived integer words.
- `producer-provenance/compaction_manifest.json` is the delivered compaction
  record.

The canonical, uniformly structured full corpus is `../blocks/`.
