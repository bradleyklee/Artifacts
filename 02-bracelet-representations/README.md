# Bracelet Representations
This artifact continues the bracelet-count table in artifact 01.

## Usage

Print the standard bracelet table (`A051137`):

```bash
python3 implementation.py --table A1 --max-n 6 --max-k 6
```

```text
A1 table; rows n, columns k

n\k    1    2    3    4    5    6
  1    1    2    3    4    5    6
  2    1    3    6   10   15   21
  3    1    4   10   20   35   56
  4    1    6   21   55  120  231
  5    1    8   39  136  377  888
  6    1   13   92  430 1505 4291
```

Print the chiral-pair table (`A293496`):

```bash
python3 implementation.py --table A2 --max-n 6 --max-k 6
```

```text
A2 table; rows n, columns k

n\k    1    2    3    4    5    6
  1    0    0    0    0    0    0
  2    0    0    0    0    0    0
  3    0    0    1    4   10   20
  4    0    0    3   15   45  105
  5    0    0   12   72  252  672
  6    0    1   38  270 1130 3535
```

Print the even-n alternating tables (NaN?):

```bash
python3 implementation.py --table B1 --max-n 6 --max-k 6
```

```text
B1 table; rows n, columns k

n\k    1    2    3    4    5    6
  1    -    -    -    -    -    -
  2    0    1    3    6   10   15
  3    -    -    -    -    -    -
  4    0    3   15   45  105  210
  5    -    -    -    -    -    -
  6    0    7   73  386 1420 4145
```

```bash
python3 implementation.py --table B2 --max-n 6 --max-k 6
```

```text
B2 table; rows n, columns k

n\k    1    2    3    4    5    6
  1    -    -    -    -    -    -
  2    0    0    0    0    0    0
  3    -    -    -    -    -    -
  4    0    1    6   21   55  120
  5    -    -    -    -    -    -
  6    0    3   46  290 1170 3605
```

Print the primitive Fourier/Lyndon table (A074650):

```bash
python3 implementation.py --table E:1 --max-n 6 --max-k 6
```

```text
E:1 table; rows n, columns k

n\k    1    2    3    4    5    6
  1    -    -    -    -    -    -
  2    -    -    -    -    -    -
  3    0    2    8   20   40   70
  4    0    3   18   60  150  315
  5    0    6   48  204  624 1554
  6    0    9  116  670 2580 7735
```

Print a decomposition:

```bash
python3 implementation.py --decompose 4 4
```

```text
D_4 decomposition for k=4; total dimension 256
  A1: multiplicity=55         dim=1 contribution=55
  A2: multiplicity=15         dim=1 contribution=15
  B1: multiplicity=45         dim=1 contribution=45
  B2: multiplicity=21         dim=1 contribution=21
 E:1: multiplicity=60         dim=2 contribution=120
sum=256
```

## 4,4 example

Generate the worked `4,4` word data:

```bash
python3 example.py
```

This writes:

```text
dihedral_4_4_words.dat
```

The `B1/B2` word labels in `dihedral_4_4_words.dat` use one chosen convention:
right-rotation B-pool, then greedy projector-rank split with B1 first. 

For construction of the projectors, we referred to William Harter's book
"Principles of Symmetry, Dynamics, and Spectroscopy". 

Online here: https://modphys.hosted.uark.edu/markup/PSDS_Info.html



