# Artifact 24 - Binder-ready executable paper

This package translates the computational content of **Jacobian
Counter-example and Elliptic Integrals** into a Python package, a paper-ordered notebook, an arithmetic/mesh
extension notebook, and interactive companion notebooks.

## Entry points

- `notebooks/artifact24_executable_paper.ipynb` - paper-ordered executable
  notebook with formulas, checks, tables, quadrature, and interactive plots.
- `notebooks/artifact24_voila.ipynb` - simplified app-like interactive viewer.
- `notebooks/artifact24_integer_periods_and_mesh.ipynb` - extension of the paper and executable notebook: exact red/Abel-Wick mapped-area periods, integer rescaling, direct Gram quadrature, mapped-triangle mesh checks, and the Q/R coordinate-net depiction.
- `paper/` - original PDF and TeX.
- `artifact24/` - reusable Python implementation.

## What was translated into Python

- the polynomial map \(F=(P,Q,R)\);
- the triangle embedding and restricted map \(G\);
- the first integral \(H(u,v)\);
- the centered cubic model \(M(x,y)\);
- the pre-image hypergeometric area and action;
- the symbolic cross product \(G_x\times G_y\);
- the intrinsic image-area density;
- direct image-area quadrature;
- OEIS coefficient formulas;
- exact collision and critical-point checks;
- red closed curves and the three bounded Abel-Wick families;
- exact matched-level intersections;
- exact mapped-area period coefficients for red, green, yellow, and blue;
- integer rescaling checks from a transparent CSV cache;
- direct Gram-integral and mapped-mesh validation for all four families;
- warning-free Q/R coordinate-net and missing-cubic overlays;
- rotatable Plotly domain and range graphics.

The continuous-folding question remains explicitly labeled as an open
geometric problem; it is not silently replaced by an arbitrary interpolation.

## New period-extension files

- `original_scripts/abel_wick_period_series.py` - exact rational action-angle
  calculation for green, yellow, and blue.
- `original_scripts/build_mapped_area_period_cache.py` - regenerates the plain
  CSV coefficient cache from the red and Abel-Wick derivations.
- `original_scripts/validate_mapped_area_periods.py` - direct Gram quadrature
  and mapped-triangle mesh checks for all four families.
- `original_scripts/qr_coordinate_net_safe.py` - warning-free extension of the
  existing Plotly picture by constant-Q/R curves and the pink missing cubic.
- `data/mapped_area_period_scaled_integers.csv` - transparent 90/100-term exact
  coefficient cache, kept outside notebook state.

## Binder

Binder uses `binder/environment.yml`. After uploading this directory to a
public GitHub repository, generate links using `BINDER_LINKS.md`.

The original executable notebook follows the paper. The integer-period notebook
builds on it and on `picture_candidates.ipynb`; it is the entry point for the
new arithmetic and mesh-verification work. The Voilà notebook is best for
people who only want the original interactive geometry.

## Local run

```bash
conda env create -f binder/environment.yml
conda activate artifact24
jupyter lab
```

For the app-like view:

```bash
voila notebooks/artifact24_voila.ipynb
```


## Smoke test

From the repository root:

```bash
python smoke_test.py
```

Expected output:

```text
PASS
```

The notebooks now locate the project root automatically, use root-relative
data paths, use an offline Plotly renderer, and are compatible with Plotly's
strict boolean validation.
