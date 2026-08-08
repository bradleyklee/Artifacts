# Algorithm success update protocol

Whenever an algorithm succeeds on a new case or family:

1. Save the complete raw run record and raw certificate.
2. Add the case to the algorithm's `success_cases` list.
3. Update the language-neutral pseudocode with the successful bounds, basis,
   normalization, and exact stopping condition.
4. Record which earlier failures the success explains or supersedes.
5. Add an independent regression replay.
6. Refresh coverage and the lessons ledger.
7. Decide whether the success is crystalline enough for a pretty certificate.

A successful implementation without a pseudocode update is incomplete project
state.
