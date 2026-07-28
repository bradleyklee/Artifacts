# Artifact 24 - Binder-ready executable paper

This package translates the computational content of **Jacobian
Counter-example and Elliptic Integrals** into a Python package and two
notebooks.

## Entry points

- `notebooks/artifact24_executable_paper.ipynb` - paper-ordered executable
  notebook with formulas, checks, tables, quadrature, and interactive plots.
- `notebooks/artifact24_voila.ipynb` - simplified app-like interactive viewer.
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
- rotatable Plotly domain and range graphics.

The continuous-folding question remains explicitly labeled as an open
geometric problem; it is not silently replaced by an arbitrary interpolation.

## Binder

Binder uses `binder/environment.yml`. After uploading this directory to a
public GitHub repository, generate links using `BINDER_LINKS.md`.

The full notebook is best for mathematical inspection. The Voilà notebook is
best for people who only want the interactive geometry.

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
