"""Python mirror of verify_A120593.jl, translated line-for-line, to validate
the algorithm since no Julia runtime is available in this sandbox."""
from fractions import Fraction as F
from math import factorial

def ptrim(a):
    a = a[:]
    while len(a) > 1 and a[-1] == 0: a.pop()
    return a

def padd(a, b):
    n = max(len(a), len(b))
    a = a + [F(0)]*(n-len(a)); b = b + [F(0)]*(n-len(b))
    return [x+y for x,y in zip(a,b)]

def pneg(a): return [-x for x in a]
def psub(a,b): return padd(a, pneg(b))
def pscale(a,c): return [x*c for x in a]

def pmul(a,b):
    out = [F(0)]*(len(a)+len(b)-1)
    for i,ai in enumerate(a):
        if ai == 0: continue
        for j,bj in enumerate(b):
            out[i+j]+=ai*bj
    return out

def ppow(a,k):
    out=[F(1)]
    for _ in range(k): out=pmul(out,a)
    return out

def ushift(a,k): return [F(0)]*k + a if k>0 else a

def pderiv(a):
    if len(a)<=1: return [F(0)]
    return [a[i]*i for i in range(1,len(a))]

def is_zero_poly(a): return all(c==0 for c in a)

Dpoly = [F(1), F(-6), F(-4), F(-1)]

N_by_n_degree = {
  2: [F(x) for x in [-491, 6396, 204, -8524, -5136, 2784, 4496, 2304, 576, 64]],
  1: [F(x) for x in [-491, 6648, -948, -11872, -6228, 5784, 7988, 4032, 1008, 112]],
  0: [F(x) for x in [0, 0, 40, -440, 640, 2960, 2960, 1440, 360, 40]],
}

def Ppolys(n):
    P0 = -8*(4*n+5)*(2*n+1)*(4*n-1)
    P1 = -64*(n+1)*(48*n**2+96*n+43)
    P2 = -6144*(2*n+3)*(n+2)*(n+1)
    P3 = 491*(n+3)*(n+2)*(n+1)
    return (P0,P1,P2,P3)

def N_of_n(n):
    out=[F(0)]*10
    for d,coeffs in N_by_n_degree.items():
        for e,c in enumerate(coeffs):
            out[e]+=c*F(n)**d
    return out

def q_multinomial(n):
    if n==0: return 1
    total=0
    for i in range(0,n+2):
        for j in range(0,n+2):
            for k in range(0,n+2):
                if i+2*j+3*k==n-1:
                    m=n+i+j+k
                    total += factorial(m-1)*6**i*4**j//(factorial(n)*factorial(i)*factorial(j)*factorial(k))
    return total

def check_multinomial():
    claimed=[1,1,6,76,1201,21252]
    computed=[q_multinomial(n) for n in range(6)]
    ok = computed==claimed
    print("[check 1] multinomial closed form vs claimed q_0..q_5")
    print("          computed:", computed)
    print("          claimed: ", claimed)
    print("          PASS =", ok)
    return ok

def check_recurrence(nmax=14):
    q=[q_multinomial(n) for n in range(nmax+1)]
    ok=True
    for n in range(0,nmax-2):
        P=Ppolys(n)
        lhs=sum(P[r]*q[n+r] for r in range(4))
        if lhs!=0:
            ok=False; print("          FAIL at n=",n,"residual=",lhs)
    print(f"[check 2] P-recurrence holds exactly for n=0..{nmax-3}: PASS =",ok)
    return ok

def series_trunc(a,ordr):
    n=min(len(a),ordr); out=[F(0)]*ordr
    for i in range(n): out[i]=a[i]
    return out

def series_mul(a,b,ordr): return series_trunc(pmul(a,b),ordr)

def series_pow(a,k,ordr):
    out=series_trunc([F(1)],ordr)
    for _ in range(k): out=series_mul(out,a,ordr)
    return out

def compute_Q_series(ordr):
    Q=[F(0)]*ordr
    for _ in range(ordr+2):
        Q2=series_mul(Q,Q,ordr); Q3=series_mul(Q2,Q,ordr); Q4=series_mul(Q3,Q,ordr)
        x=[F(0)]*ordr
        if ordr>=2: x[1]=F(1)
        Q=series_trunc(padd(padd(x,pscale(Q2,F(6))),padd(pscale(Q3,F(4)),Q4)),ordr)
    return Q

def check_algebraic(ordr=14):
    Q=compute_Q_series(ordr)
    A=series_trunc(padd(Q,[F(1)]),ordr)
    A4=series_pow(A,4,ordr)
    x=[F(0)]*ordr
    if ordr>=2: x[1]=F(1)
    residual=series_trunc(psub(psub(pscale(A,F(5)),padd([F(4)],x)),A4),ordr)
    ok=is_zero_poly(residual)
    qvals=[Q[n] for n in range(1,min(6,ordr))]
    claimed=[F(v) for v in [1,6,76,1201,21252]][:len(qvals)]
    ok2 = qvals==claimed
    print(f"[check 3] algebraic equation 5A=4+x+A^4 holds to order {ordr-1}: PASS =",ok)
    print("          Q coeffs vs multinomial agree: PASS =",ok2)
    return ok and ok2

def check_differential(ordr=16):
    Q=compute_Q_series(ordr)
    A=series_trunc(padd(Q,[F(1)]),ordr)
    dA=pderiv(A); d2A=pderiv(dA); d3A=pderiv(d2A)
    x=[F(0)]*ordr
    if ordr>=2: x[1]=F(1)
    c3=series_trunc(padd([F(-491)],padd(pscale(x,F(12288)),padd(pscale(pmul(x,x),F(3072)),pscale(pmul(pmul(x,x),x),F(256))))),ordr)
    c2=series_trunc(padd([F(18432)],padd(pscale(x,F(9216)),pscale(pmul(x,x),F(1152)))),ordr)
    c1=series_trunc(padd([F(2752)],pscale(x,F(688))),ordr)
    lhs=padd(padd(series_mul(c3,d3A,ordr),series_mul(c2,d2A,ordr)),padd(series_mul(c1,dA,ordr),pscale(A,F(-40))))
    residual=series_trunc(lhs,ordr-4)
    ok=is_zero_poly(residual)
    print(f"[check 4] differential operator holds to order {ordr-5}: PASS =",ok)
    return ok

def check_telescoping(nrange=range(1,9)):
    ok_all=True
    for n in nrange:
        P=Ppolys(n)
        lhs_num=[F(0)]
        for r in range(4):
            term=pscale(pmul(ushift([F(1)],3-r),ppow(Dpoly,3-r)),F(P[r],n+r))
            lhs_num=padd(lhs_num,term)
        lhs_den=pmul(ushift([F(1)],n+3),ppow(Dpoly,n+3))
        f=N_of_n(n)
        g=pscale(pmul(ushift([F(1)],n+2),ppow(Dpoly,n+2)),F(n))
        fprime=pderiv(f); gprime=pderiv(g)
        rhs_num=psub(pmul(fprime,g),pmul(f,gprime))
        rhs_den=pmul(g,g)
        diff=psub(pmul(lhs_num,rhs_den),pmul(rhs_num,lhs_den))
        ok=is_zero_poly(ptrim(diff))
        ok_all &= ok
        print(f"          n={n}: identity holds exactly = {ok}")
    print("[check 5] creative-telescoping identity: PASS =",ok_all)
    return ok_all

if __name__=='__main__':
    print("Python mirror of verify_A120593.jl -- validating algorithm correctness")
    print("="*72)
    r1=check_multinomial()
    r2=check_recurrence()
    r3=check_algebraic()
    r4=check_differential()
    r5=check_telescoping()
    print("="*72)
    print("ALL CHECKS PASS:", r1 and r2 and r3 and r4 and r5)
