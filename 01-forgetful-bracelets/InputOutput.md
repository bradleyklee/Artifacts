# Harm.On.ica Triangle Raw Usage and Output

## Self-test, default closed repeat-letter mode

Command:

```bash
python3 harmonica_triangle_reference.py 10 --self-test
```

Output:

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

## Brute-force repeat-letter mode through N=5

Command:

```bash
python3 harmonica_triangle_reference.py 5 --mode brute
```

Output:

```text
triangle:
1;
  1,1;
  3,2,1;
  10,6,3,1;
  55,20,10,4,1;
  377,120,35,15,5,1

sequence:
1,2,6,20,90,553

first_differences:
1,1,4,14,70,463

tail_differences:
0;
  1,0;
  3,1,0;
  10,4,1,0;
  65,15,5,1,0
```

## No-repeat / Pascal mode through N=10

Command:

```bash
python3 harmonica_triangle_reference.py 10 --no-repeat
```

Output:

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

first_differences:
1,1,2,4,8,16,32,64,128,256,512

tail_differences:
0;
  1,0;
  2,1,0;
  3,3,1,0;
  4,6,4,1,0;
  5,10,10,5,1,0;
  6,15,20,15,6,1,0;
  7,21,35,35,21,7,1,0;
  8,28,56,70,56,28,8,1,0;
  9,36,84,126,126,84,36,9,1,0
```

## Brute-force no-repeat mode through N=10

Command:

```bash
python3 harmonica_triangle_reference.py 10 --mode brute --no-repeat
```

Output should match the no-repeat / Pascal output above.
