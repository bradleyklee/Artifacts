from fractions import Fraction as F

def polymul(a, b):
    res = [F(0)] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai == 0: continue
        for j, bj in enumerate(b):
            res[i+j] += ai * bj
    return res

def polyadd(a, b):
    n = max(len(a), len(b))
    a = a + [F(0)]*(n-len(a)); b = b + [F(0)]*(n-len(b))
    return [x+y for x,y in zip(a,b)]

def polyscale(a, c):
    return [x*c for x in a]

def polypow(a, k):
    res = [F(1)]
    for _ in range(k):
        res = polymul(res, a)
    return res

def polyderiv(a):
    if len(a) <= 1: return [F(0)]
    return [a[i]*i for i in range(1,len(a))]

def trim(a):
    a = a[:]
    while len(a) > 1 and a[-1] == 0: a.pop()
    return a

def is_zero(a):
    return all(c == 0 for c in a)

# D(u) = 1 - 6u - 4u^2 - u^3
D = [F(1), F(-6), F(-4), F(-1)]

N_by_n_degree = {
  2: [-491, 6396, 204, -8524, -5136, 2784, 4496, 2304, 576, 64],
  1: [-491, 6648, -948, -11872, -6228, 5784, 7988, 4032, 1008, 112],
  0: [0, 0, 40, -440, 640, 2960, 2960, 1440, 360, 40],
}

def Ppoly(n):
    P0 = -8*(4*n+5)*(2*n+1)*(4*n-1)
    P1 = -64*(n+1)*(48*n**2+96*n+43)
    P2 = -6144*(2*n+3)*(n+2)*(n+1)
    P3 = 491*(n+3)*(n+2)*(n+1)
    return [P0,P1,P2,P3]

def N_of_n(n):
    # returns polynomial in u for fixed integer n
    res = [F(0)]*10
    for d, coeffs in N_by_n_degree.items():
        for e,c in enumerate(coeffs):
            res[e] += F(c) * (n**d)
    return res

def check_identity(n):
    P = Ppoly(n)
    # LHS: sum_r [P_r/(n+r)] * u^(3-r) * D^(3-r)   over common denom u^(n+3) D^(n+3)
    lhs_num = [F(0)]
    for r in range(4):
        term = polyscale(polymul([F(0)]*(3-r) + [F(1)], polypow(D, 3-r)), F(P[r], n+r))
        lhs_num = polyadd(lhs_num, term)
    # lhs_den = u^(n+3) * D^(n+3)  -- represented implicitly; we'll build explicit poly
    lhs_den = polymul([F(0)]*(n+3) + [F(1)], polypow(D, n+3))

    # RHS = d/du (f/g), f = N(n,u), g = n * u^(n+2) * D^(n+2)
    f = N_of_n(n)
    g = polyscale(polymul([F(0)]*(n+2)+[F(1)], polypow(D,n+2)), F(n))
    fprime = polyderiv(f)
    gprime = polyderiv(g)
    rhs_num = polyadd(polymul(fprime,g), polyscale(polymul(f,gprime), F(-1)))
    rhs_den = polymul(g,g)

    # cross multiply: lhs_num*rhs_den - rhs_num*lhs_den should be 0
    lval = polymul(lhs_num, rhs_den)
    rval = polymul(rhs_num, lhs_den)
    diff = polyadd(lval, polyscale(rval, F(-1)))
    return is_zero(trim(diff)), trim(diff)

for n in range(1,9):
    ok, diff = check_identity(n)
    print(f"n={n}: identity holds = {ok}" + ("" if ok else f"  residual leading terms: {diff[:5]}"))
