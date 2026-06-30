# Assembly status

This packet follows artifact 15's useful division: compact seeds, full
self-contained positive certificates, independent checker reports, derived
sequence files, code-generated visuals, manifests, and explicit finite-prefix
language.

Completed in this assembly:

* canonical Go exact engine for square, octagon, dodecagon, and 24-gon models;
* Go exhaustive atlases for each listed low family;
* Python independent replay reports for the committed atlases and positive full
  certificates;
* full cap-500 and cap-2000 dodecagon certificates plus its 3-batch reverse-stem certificate; a cap-4000, cap-6000, and cap-7500 compact checkpoints;
* full cap-100 certificates for both 24-gon D4 representatives;
* D4/time-reversal and ternary derivations;
* two code-generated vertical Shorts totaling 89 seconds.

Not claimed:

* a proof that any finite-horizon survivor is chaotic, aperiodic, or infinite;
* a completed 8,000- or 12,000-event Go common-field replay;
* a complete larger-box or larger-body classification.

## Foreground verification note

The full `make check` command regenerates fifteen independent reports and can
exceed a short foreground tool time limit. During assembly it was run in
smaller groups; every committed `check/*.python.json` report is `PASS`, including
all highlighted certificates and the 7,500-batch compact checkpoint. A fresh
reviewer can run the single `make check` target without relying on this note.
