from pathlib import Path
import json,time,math
import sympy as sp
p,q,t=sp.symbols('p q t')

def moment(a,b):
    return sp.factorial(2*a)*sp.factorial(2*b)/(sp.Integer(4)**(a+b)*sp.factorial(a)*sp.factorial(b)*sp.factorial(a+b))

def avg_structured(n,m,r,U,V):
    # average L2^(2n) L1^(2m), L2=q^2-rp^2, L1=sqrt(U)p+sqrt(V)q
    total=sp.S.Zero
    for a in range(2*n+1):
        c2=sp.binomial(2*n,a)*(-r)**(2*n-a)
        for c in range(m+1):
            c1=sp.binomial(2*m,2*c)*U**c*V**(m-c)
            ap=2*n-a+c
            bq=a+m-c
            total += c2*c1*moment(ap,bq)
    return sp.factor(total)

def coeffs_quartic(r,U,V,mu,N):
    vals=[]
    for n in range(N+1):
        total=sp.S.Zero
        for k in range(n+1):
            m=n-k
            comb=(-1)**k*sp.binomial(3*n-k,2*n-k)*sp.binomial(2*n-k,k)
            total += comb*mu**k*avg_structured(n,m,r,U,V)
        vals.append(sp.factor(total))
    return vals

def avg_poly(expr):
    po=sp.Poly(sp.expand(expr),p,q)
    total=0
    for (i,j),c in po.terms():
        if i%2 or j%2:continue
        total += c*moment(i//2,j//2)
    return sp.factor(total)

def coeffs_cubic(H3,N):
    vals=[]; power=sp.Integer(1); Hsq=sp.expand(H3**2)
    for n in range(N+1):
        if n>0: power=sp.expand(power*Hsq)
        vals.append(sp.factor(sp.binomial(3*n,2*n)*avg_poly(power)))
    return vals

def scale_candidate(vals):
    primes={}
    for n,v in enumerate(vals[1:],1):
        v=sp.cancel(v)
        assert v.is_Rational,(n,v)
        for pr,e in sp.factorint(int(v.q)).items():primes[pr]=max(primes.get(pr,0),(e+n-1)//n)
    M=1
    for pr,e in primes.items():M*=pr**e
    return M,primes

def guess_ode(seq,max_d=8):
    N=len(seq);tt=sp.symbols('t')
    for d2 in range(1,max_d+1):
      for d1 in range(0,d2+1):
       for d0 in range(0,d2):
        labels=[]; rows=[]
        for m in range(N-2):
          row=[]
          for order,d in [(2,d2),(1,d1),(0,d0)]:
           for j in range(d+1):
            nn=m-j+order
            if nn<order or nn>=N:val=0
            else:
             ff=sp.factorial(nn)/sp.factorial(nn-order)
             val=seq[nn]*ff
            row.append(val);labels.append((order,j)) if m==0 else None
          rows.append(row)
        M=sp.Matrix(rows);ns=M.nullspace()
        if not ns:continue
        for vec in ns:
          if all(vec[k]==0 for k,l in enumerate(labels) if l[0]==2):continue
          pol={0:0,1:0,2:0}
          for co,(o,j) in zip(vec,labels):pol[o]+=co*tt**j
          den=sp.ilcm(*[sp.denom(c) for v in pol.values() for c in sp.Poly(v,tt).all_coeffs()])
          pol={o:sp.expand(v*den) for o,v in pol.items()}
          nums=[abs(int(c)) for v in pol.values() for c in sp.Poly(v,tt).all_coeffs() if c]
          g=math.gcd(*nums) if nums else 1
          pol={o:sp.expand(v/g) for o,v in pol.items()}
          if sp.LC(sp.Poly(pol[2],tt))<0:pol={o:-v for o,v in pol.items()}
          return pol,(d2,d1,d0)
    return None,None

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RELEASE_ROOT = HERE.parents[1]
COVERAGE_FILE = RELEASE_ROOT / "examples" / "data" / "coverage_56_v1.json"
OUTPUT_FILE = RELEASE_ROOT / "examples" / "data" / "period_recompute.json"
REFERENCE_FILE = RELEASE_ROOT / "examples" / "data" / "models_11_release.json"


def load_jobs():
    cov = json.loads(COVERAGE_FILE.read_text())
    jobs = []
    model_index = 0
    for fam in cov['families']:
        for rec in fam['records']:
            if rec['status'] != 'exists_verified':
                continue
            model_index += 1
            jobs.append((model_index, fam, rec))
    return jobs


def compute_job(idx, fam, rec, terms: int, guess: bool):
    par = rec['witness']['parameters']
    st = time.time()
    top = terms - 1
    if fam['family'] == 'harmonic_plus_cubic':
        H3 = (sp.sympify(par['a'])*p**3 + sp.sympify(par['b'])*p**2*q
              + sp.sympify(par['c'])*p*q**2 + sp.sympify(par['d'])*q**3)
        vals = coeffs_cubic(H3, top)
        extra = {'H3': sp.sstr(H3)}
    else:
        r = sp.sympify(par['r'])
        U = sp.sympify(par['U'])
        V = sp.sympify(par['V'])
        mu = sp.sympify(par['mu'])
        vals = coeffs_quartic(r, U, V, mu, top)
        extra = {'r': str(r), 'U': str(U), 'V': str(V), 'mu': str(mu)}
    M, pr = scale_candidate(vals)
    A = [sp.factor(vals[n]*M**n) for n in range(len(vals))]
    assert all(v.is_Integer for v in A)
    ode, degs = guess_ode(A, 8) if guess else (None, None)
    return {
        'index': idx,
        'target': rec['target'],
        'family': fam['family'],
        'delta': rec['witness']['delta'],
        **extra,
        'scale_M': M,
        'scale_primes': pr,
        'coeff_E': [str(v) for v in vals],
        'integer_coefficients': [str(v) for v in A],
        'ode': {str(k): sp.sstr(v) for k, v in ode.items()} if ode else None,
        'ode_degrees': degs,
        'wall_seconds': round(time.time()-st, 3),
    }


def worker(index: int) -> None:
    jobs = {idx: (fam, rec) for idx, fam, rec in load_jobs()}
    if index not in jobs:
        raise SystemExit(f'unknown model index {index}')
    fam, rec = jobs[index]
    print(json.dumps(compute_job(index, fam, rec, terms=31, guess=True)))


def quick() -> None:
    reference = json.loads(REFERENCE_FILE.read_text())
    out = []
    for idx, fam, rec in load_jobs():
        sp.core.cache.clear_cache()
        record = compute_job(idx, fam, rec, terms=12, guess=False)
        expected = reference['models'][idx-1]['first_31_coefficients_at_observed_scale'][:12]
        if record['integer_coefficients'] != expected:
            raise AssertionError(f'period coefficient mismatch at model {idx}')
        out.append(record)
        print(idx, record['target'], '12 exact terms match', flush=True)
    OUTPUT_FILE.write_text(json.dumps(out, indent=2) + "\n")
    print('quick period audit matches the first 12 terms of all 11 models')


def full() -> None:
    out = []
    # Each model runs in a fresh interpreter to avoid long-lived SymPy cache
    # growth. This mode is slower because every worker imports SymPy anew.
    for index in range(1, 12):
        raw = subprocess.check_output(
            [sys.executable, str(Path(__file__).resolve()), '--worker', str(index)],
            text=True,
        )
        record = json.loads(raw)
        out.append(record)
        print(index, record['target'], 'sec', record['wall_seconds'], 'M', record['scale_M'], 'ode', record['ode_degrees'], flush=True)

    OUTPUT_FILE.write_text(json.dumps(out, indent=2) + "\n")
    reference = json.loads(REFERENCE_FILE.read_text())
    for record, model in zip(out, reference['models'], strict=True):
        if record['index'] != model['index']:
            raise AssertionError('model order mismatch')
        if record['integer_coefficients'] != model['first_31_coefficients_at_observed_scale']:
            raise AssertionError(f"period coefficient mismatch at model {record['index']}")
    print('full period recomputation matches all 31 terms of all 11 models')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker', type=int)
    parser.add_argument('--full', action='store_true')
    parser.add_argument('--quick', action='store_true')
    args = parser.parse_args()
    if args.worker is not None:
        worker(args.worker)
    elif args.full:
        full()
    else:
        quick()
