# Implementation decision ledger

| Change | Reason | Verification status |
|---|---|---|
| generic Go `OrderFunc` | support ordered values independent of key identity | exhaustive suite PASS |
| strong `Validate` invariant | make structural failures observable | corruption tests PASS |
| contiguous `[]link` towers | reduce per-node maps/allocations | full B1 suite PASS |
| index-addressed node arena | improve locality and allocation behavior | full B1 suite PASS |
| direct sentinels | remove map lookups/allocations | full B1 suite PASS |
| arena-aligned index-to-key slice | remove reverse lookup map | full B1 suite PASS |
| retain key-to-index Go map | expected O(1) exact identity lookup | differential tests PASS |
| retain baseline type-2 closure priority | nearby recurse-first alternatives have executable counterexamples | exhaustive suite PASS |
