# Forgetful Bracelets Triangle

Reference implementation: `implementation-01.py`

This program computes an integer triangle from a forgetful deletion process on
words, modulo dihedral symmetry.

## Definition

For `N >= 0` and `0 <= M <= N`, define `T(N,M)`.

Repeat-letter mode:

1. Start from all words of length `N` over alphabet `{1, ..., N}`.
2. Delete `M` positions recursively.
3. Canonicalize survivor words under rotation and reflection.
4. Count the distinct canonical survivor words.

Equivalently:

```text
T(N,M) = bracelets(N, N-M)
```

where `bracelets(q,L)` is the number of length-`L` bracelets over `q` colors.

No-repeat mode starts from the single word:

```text
1,2,...,N
```

Then deletion states do not collide, so:

```text
T(N,M) = binomial(N,M)
```

This gives Pascal's triangle.

## Output

The program prints:

```text
triangle
sequence
first_differences
tail_differences
```

where:

```text
sequence[N] = sum_M T(N,M)
tail_differences[N,M] = T(N+1,M+1) - T(N,M)
```

Output is comma/semicolon separated for search and comparison.

## Usage

Run the default closed-form repeat-letter calculation:

```bash
python3 implementation-01.py 10
```

Run self-tests first:

```bash
python3 implementation-01.py 10 --self-test
```

Run brute force for small repeat-letter cases:

```bash
python3 implementation-01.py 5 --mode brute
```

Run no-repeat / Pascal mode:

```bash
python3 implementation-01.py 10 --no-repeat
```

Run brute force no-repeat mode:

```bash
python3 implementation-01.py 10 --mode brute --no-repeat
```

## Example Output

Default repeat-letter output through `N=10`:

```text
triangle:
1;
  1,1;
  3,2,1;
  10,6,3,1;
  55,20,10,4,1;
  377,120,35,15,5,1;
  4291,888,231,56,21,6,1;
  60028,10528,1855,406,84,28,7,1;
  1058058,151848,23052,3536,666,120,36,8,1;
  21552969,2707245,344925,46185,6273,1035,165,45,9,1;
  500280022,55605670,6278140,719290,86185,10504,1540,220,55,10,1

sequence:
1,2,6,20,90,553,5494,72937,1237325,24658852,562981637

first_differences:
1,1,4,14,70,463,4941,67443,1164388,23421527,538322785

tail_differences:
0;
  1,0;
  3,1,0;
  10,4,1,0;
  65,15,5,1,0;
  511,111,21,6,1,0;
  6237,967,175,28,7,1,0;
  91820,12524,1681,260,36,8,1,0;
  1649187,193077,23133,2737,369,45,9,1,0;
  34052701,3570895,374365,40000,4231,505,55,10,1,0
```

No-repeat / Pascal output through `N=10`:

```text
triangle:
1;
  1,1;
  1,2,1;
  1,3,3,1;
  1,4,6,4,1;
  1,5,10,10,5,1;
  1,6,15,20,15,6,1;
  1,7,21,35,35,21,7,1;
  1,8,28,56,70,56,28,8,1;
  1,9,36,84,126,126,84,36,9,1;
  1,10,45,120,210,252,210,120,45,10,1

sequence:
1,2,4,8,16,32,64,128,256,512,1024
```

## Burnside Formula

For `L >= 1`:

```text
bracelets(N,L)
=
1/(2L) * (rotation_total + reflection_total)
```

with:

```text
rotation_total = sum_{k=0}^{L-1} N^gcd(L,k)
```

and:

```text
if L is odd:
    reflection_total = L * N^((L+1)/2)

if L is even:
    reflection_total = (L/2) * N^(L/2 + 1)
                     + (L/2) * N^(L/2)
```

The empty word has count:

```text
bracelets(N,0) = 1
```

The repeat-letter row sum is:

```text
A(N) = sum_{L=0}^{N} bracelets(N,L)
```

Initial row sums:

```text
1,2,6,20,90,553,5494,72937,1237325,24658852,562981637
```

## Notes

The implementation contains both brute-force and closed-form paths. Keep them
separate. The brute-force path is a checker for small cases; the closed-form
path is for speed and mathematical explanation.

Odd row sums can occur. For example, `A(5) = 553`.

The main open question is whether the row sums have a useful simplification or
recurrence. The rotation part reduces to divisor/totient sums and does not look
directly hypergeometric.
