# Reverified models 5 and 7

These files were once quarantined because an earlier packaging run reported a
failed assertion. In this release they are promoted after a clean audit checked:

- the exact scalar Hamiltonian certificate modulo 2H-E;
- the exact Laurent telescoping identity;
- the first 12 constant-term coefficients against the stored plane period;
- the recurrence obtained from the Laurent certificate against the stored
  second-order period equation.

Run `python code/certificates/verify_promoted_cases.py` from the release root.
