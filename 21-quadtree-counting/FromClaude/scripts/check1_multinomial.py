from sympy import symbols, Rational, factorial, series, Symbol
from math import factorial as fact

# independent computation of multinomial sum formula
# q[n] = sum_{i,j,k>=0, i+2j+3k=n-1} (n+i+j+k-1)! * 6^i * 4^j / (n! i! j! k!)

def q_multinomial(n):
    if n == 0:
        return 1  # given q0=1 by convention, checked directly
    total = 0
    for i in range(0, n+2):
        for j in range(0, n+2):
            for k in range(0, n+2):
                if i + 2*j + 3*k == n-1:
                    m = n + i + j + k
                    total += fact(m-1) * (6**i) * (4**j) / (fact(n)*fact(i)*fact(j)*fact(k))
    return total

vals = [q_multinomial(n) for n in range(0,6)]
print("Multinomial sum q[0..5]:", vals)
print("Claimed:", [1,1,6,76,1201,21252])
