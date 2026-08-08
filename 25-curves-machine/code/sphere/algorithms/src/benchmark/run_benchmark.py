#!/usr/bin/env python3
import argparse, json, os, sys, time, traceback
from fractions import Fraction as F
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
import sympy as sp

ROOT=os.path.dirname(os.path.dirname(__file__))
MODEDIR=os.path.join(ROOT,'models'); DATADIR=os.path.join(ROOT,'data'); LOGDIR=os.path.join(ROOT,'logs')
os.makedirs(DATADIR,exist_ok=True);os.makedirs(LOGDIR,exist_ok=True)
SRC='/mnt/data/quartic_mode_search_2026-08-02/src'
RED='/mnt/data/_quartic_work/semi_random_quartics_2026-08-02/src'
sys.path.insert(0,SRC);sys.path.insert(0,RED)
from general_quartic_series_mod import series
from scan_first_operator import scan
from cartesian_cohomology_reduction import exact_image_map, common_derivative_numerators
from polynomial_hamiltonian_to_ode import mono
from modular_ode_screen_numpy import rank_mod

PRIME_ALPHA=[(65521,7),(65497,11)]
NTERMS=270
MAX_ORDER=6
DEGREE_CAP=35

def energy(rec):
    E={(0,2,0):F(1),(0,0,2):F(1)}
    for mons in rec['monomials'].values():
        for pe,qe,c in mons:
            E[(0,int(pe),int(qe))]=E.get((0,int(pe),int(qe)),F(0))+F(c)
    return E

def qmod(c,p): return c.numerator%p*pow(c.denominator%p,-1,p)%p

def ev(poly,a,p):
    z={}
    for (ae,pe,qe),c in poly.items():
        z[(pe,qe)]=(z.get((pe,qe),0)+qmod(c,p)*pow(a,ae,p))%p
    return {k:v for k,v in z.items() if v}

def binary_quartic_info(rec):
    coeff={(int(pe),int(qe)):F(c) for pe,qe,c in rec['monomials']['4']}
    t=sp.symbols('t')
    f=sum(sp.Rational(c.numerator,c.denominator)*t**pe for (pe,qe),c in coeff.items() if pe+qe==4)
    # q=1, p=t. All generated models have a nonzero p^4 coefficient.
    a4=coeff.get((4,0),F(0))
    if not a4:
        return {'p4_nonzero':False,'discriminant':None,'squarefree_at_infinity':None}
    disc=sp.factor(sp.discriminant(f,t))
    return {'p4_nonzero':True,'discriminant':str(disc),'squarefree_at_infinity':bool(disc!=0)}

def reductive_order(E,r,p,alpha,B):
    t=time.time(); im=exact_image_map(E,r)
    labels=[(pe,qe) for pe in range(4) for qe in range(B-pe+1)]
    ex=[ev(im(mono(0,pe,qe)),alpha,p) for pe,qe in labels]
    der=[ev(w,alpha,p) for w in common_derivative_numerators(E,r)]
    rows=sorted(set().union(*(x.keys() for x in ex+der)))
    pos={k:i for i,k in enumerate(rows)}
    C=np.zeros((len(rows),len(ex)),dtype=np.int64)
    W=np.zeros((len(rows),r+1),dtype=np.int64)
    for j,x in enumerate(ex):
        for k,v in x.items():C[pos[k],j]=v
    for j,x in enumerate(der):
        for k,v in x.items():W[pos[k],j]=v
    rc=rank_mod(C,p);ra=rank_mod(np.hstack([C,W]),p)
    return {'order':r,'bound':B,'rows':len(rows),'source_columns':len(ex),'rank_C':int(rc),'rank_CW':int(ra),
            'relation_dimension':int(r+1-(ra-rc)),'seconds':time.time()-t}

def work(path):
    rec=json.load(open(path)); name=rec['example_id']; started=time.time(); out={'example_id':name,'category':rec['category'],'model_path':path,'status':'RUNNING'}
    try:
        E=energy(rec); qi=binary_quartic_info(rec); out['quartic_infinity']=qi
        inductive=[]
        for p,a in PRIME_ALPHA:
            t=time.time(); seq=series(rec['monomials'],NTERMS,p)
            sf=os.path.join(DATADIR,f'{name}_series_{p}.json')
            json.dump({'example_id':name,'prime':p,'terms':seq,'seconds':time.time()-t},open(sf,'w'),indent=2);open(sf,'a').write('\n')
            sc=scan(sf,NTERMS,MAX_ORDER,DEGREE_CAP)
            inductive.append(sc)
        out['inductive']=inductive
        hits=[x['first_hit'] for x in inductive]
        out['inductive_agreement']=hits[0]==hits[1]
        out['first_hit']=hits[0] if out['inductive_agreement'] else None
        reductive=[]
        if qi.get('squarefree_at_infinity'):
            for p,a in PRIME_ALPHA:
                rr=[]
                for r in range(1,MAX_ORDER+1):
                    B=6*r-3
                    z=reductive_order(E,r,p,a,B);rr.append(z)
                    # Continue through first relation to demonstrate lower-order exclusions; then stop.
                    if z['relation_dimension']>0: break
                reductive.append({'prime':p,'alpha':a,'records':rr,'first_hit':next(({'order':z['order'],'relation_dimension':z['relation_dimension']} for z in rr if z['relation_dimension']>0),None)})
            out['deductive_bound_status']='GENERIC_BOUND_APPLIED'
        else:
            # Still exercise reductive mode with a conservative empirical triangular bound, but do not call it exhaustive.
            for p,a in PRIME_ALPHA:
                rr=[]
                for r in range(1,MAX_ORDER+1):
                    B=6*r+3
                    z=reductive_order(E,r,p,a,B);z['bound_status']='EMPIRICAL_NOT_PROVED';rr.append(z)
                    if z['relation_dimension']>0: break
                reductive.append({'prime':p,'alpha':a,'records':rr,'first_hit':next(({'order':z['order'],'relation_dimension':z['relation_dimension']} for z in rr if z['relation_dimension']>0),None)})
            out['deductive_bound_status']='DEGENERATE_INFINITY_EMPIRICAL_ONLY'
        out['reductive']=reductive
        rh=[x['first_hit'] for x in reductive]
        out['reductive_agreement']=rh[0]==rh[1]
        out['reductive_first_hit']=rh[0] if out['reductive_agreement'] else None
        out['mode_agreement']=bool(out['inductive_agreement'] and out['reductive_agreement'] and ((out['first_hit'] or {}).get('order')==(out['reductive_first_hit'] or {}).get('order')))
        out['status']='PASS' if out['mode_agreement'] else 'MISMATCH'
    except Exception as e:
        out['status']='ERROR';out['error']=repr(e);out['traceback']=traceback.format_exc()
    out['seconds_total']=time.time()-started
    dest=os.path.join(DATADIR,name+'_result.json')
    with open(dest,'w') as f:json.dump(out,f,indent=2);f.write('\n')
    return name,out['status'],out.get('first_hit'),out.get('reductive_first_hit'),out['seconds_total']

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=4);ap.add_argument('--limit',type=int,default=0);ns=ap.parse_args()
    idx=json.load(open(os.path.join(ROOT,'candidate_index.json'))); paths=[x['path'] for x in idx if not os.path.exists(os.path.join(DATADIR,x['example_id']+'_result.json'))]
    if ns.limit:paths=paths[:ns.limit]
    with ProcessPoolExecutor(max_workers=ns.workers) as ex:
        futs={ex.submit(work,p):p for p in paths}
        for fut in as_completed(futs):
            try: print(fut.result(),flush=True)
            except Exception as e: print('WORKER_FAILURE',futs[fut],repr(e),flush=True)
if __name__=='__main__':main()
