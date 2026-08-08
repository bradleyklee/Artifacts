#!/usr/bin/env python3
import argparse,json,hashlib
from modular_ode_screen_numpy import matrix
from reconstruct_operator_modular import null_vector_mod,falling

def verify(seq,v,p,R,D,start,end):
 for n in range(start,end):
  z=0;t=0
  for j in range(R+1):
   for e in range(D+1):
    c=v[t];t+=1;k=n-e+j
    if c and n>=e and k>=j and k<len(seq):z=(z+c*falling(k,j)*seq[k])%p
  if z:return {'pass':False,'first_failure_n':n,'residual':z}
 return {'pass':True,'equations_checked':end-start}
ap=argparse.ArgumentParser();ap.add_argument('series');ap.add_argument('--order',type=int,required=True);ap.add_argument('--degree',type=int,required=True);ap.add_argument('--train',type=int,required=True);ap.add_argument('--output',required=True);ns=ap.parse_args();d=json.load(open(ns.series));seq=d['terms'];p=d['prime'];R=ns.order;D=ns.degree;A=matrix(seq,R,D,p,ns.train);v,f=null_vector_mod(A,p);out={'example_id':d['example_id'],'prime':p,'order':R,'degree':D,'train_terms':ns.train,'full_terms':len(seq),'matrix_shape':list(A.shape),'free_column':f,'null_vector_sha256':hashlib.sha256(','.join(map(str,v)).encode()).hexdigest(),'training':verify(seq,v,p,R,D,0,ns.train-R),'heldout':verify(seq,v,p,R,D,ns.train-R,len(seq)-R)};json.dump(out,open(ns.output,'w'),indent=2);open(ns.output,'a').write('\n');print(out)
