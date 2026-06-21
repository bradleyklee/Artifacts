# Validation material

- `scipy_shape_check_n10.txt`: independent SciPy/HiGHS classification agrees
  shape-for-shape with the exact C++ output through order 10.
- `../results/exhaustive_n1_n14.txt` and `.csv`: fresh direct exhaustive C++ run.
- `../results/successor_depth1_n15_n20.txt` and `.csv`: fresh depth-1 continuation.

The SciPy check is deliberately a cross-check only.  The project's acceptance
claim is made by the C++ exact-rational simplex, not by a floating-point LP.
