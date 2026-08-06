# Exact certificates for models 5 and 7

These files provide the exact Hamiltonian and Laurent certificates used by the
unified complete-case verifier.

The checks include

```text
exact scalar Hamiltonian residual modulo 2H-E
exact Laurent telescoping residual
12 direct constant-term coefficients
Laurent-to-period annihilator comparison
31 stored recurrence terms
```

Run all complete cases with

```text
python3 code/certificates/verify_complete_cases.py
```
