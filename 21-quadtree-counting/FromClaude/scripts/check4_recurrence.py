from sympy import symbols, Rational, simplify, expand, factorial

n = symbols('n')

P0 = -8*(4*n+5)*(2*n+1)*(4*n-1)
P1 = -64*(n+1)*(48*n**2+96*n+43)
P2 = -6144*(2*n+3)*(n+2)*(n+1)
P3 = 491*(n+3)*(n+2)*(n+1)

P = [P0,P1,P2,P3]

# compute q[n] via multinomial sum for a longer range, then test recurrence for all valid n
from math import factorial as fact
def q_multinomial(nn):
    if nn == 0:
        return 1
    total = 0
    for i in range(0, nn+2):
        for j in range(0, nn+2):
            for k in range(0, nn+2):
                if i + 2*j + 3*k == nn-1:
                    m = nn + i + j + k
                    total += fact(m-1) * (6**i) * (4**j) // (fact(nn)*fact(i)*fact(j)*fact(k))
    return total

Nmax = 15
q = [q_multinomial(nn) for nn in range(0, Nmax)]
print("q values:", q)

ok = True
for nn in range(0, Nmax-3):
    lhs = sum(P[r].subs(n, nn) * q[nn+r] for r in range(4))
    if lhs != 0:
        ok = False
        print(f"FAIL at n={nn}: {lhs}")
print("Recurrence holds for all tested n:", ok)
