TRIANGLE-RECTANGLE CERTIFICATE v5.17 - AUTONOMOUS REVIEW

Normalization:
  alpha=2H in 0<=alpha<1,
  p_new=2*p_old, q_new=2*q_old, alpha_new=4*alpha_old.

The verifier first proves exactly that
  F_new(p,q)=4*F_old(p/2,q/2)
and then checks only formulas written in the new normalization.

Replay:
  python3 verify_certificate.py
  python3 generate_quantized_levels.py --check
  python3 generate_figure.py
  sha256sum -c MANIFEST.sha256

Key coordinate checks:
  real wells: (0,0), (0,-4)
  Abel-Wick center: (0,-2)
  reflection: q -> -4-q
  certificate shift: x=q+2
  energy separatrix: alpha=1
  period graph axis: 0 to 1

Expected verifier ending:
  ALL CHECKS PASS
  35 proof-level checks passed; all data were regenerated in the alpha in [0,1] normalization.
