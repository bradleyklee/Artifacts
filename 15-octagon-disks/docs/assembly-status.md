# Assembly status

The artifact was assembled from the previously generated exact ledgers and their
stored independent checker reports. During this packaging pass, `make smoke`
completed successfully: it independently checked three-body record 1489, clock
record 086, and regenerated all eighteen SVG initial-condition views.

The complete `make check` pass is intentionally available but was not allowed
to finish during this assembly session because it replays all 18 long exact
ledgers and exceeded the available foreground runtime. The committed `check/`
reports are preserved from the earlier completed checking runs; a fresh full
verification should be run before any stronger publication claim.
