#!/usr/bin/env python3
from fractions import Fraction
import argparse,json,hashlib
from modular_ode_screen_numpy import matrix
from reconstruct_operator_modular import null_vector_mod,falling

def qmod(x,p):
 x=Fraction(x);return (x.numerator%p)*pow(x.denominator%p,-1,p)%p

def verify(seq,v,p,R,D,start_n,end_n):
 for n in range(start_n,end_n):
  z=0;t=0
  for j in range(R+1):
   for e in range(D+1):
    c=v[t];t+=1;k=n-e+j
    if c and n>=e and k>=j and 0<=k<len(seq):
     z=(z+c*(falling(k,j)%p)*qmod(seq[k],p))%p
  if z:return {'pass':False,'first_failure_n':n,'residual':z}
 return {'pass':True,'equations_checked':max(0,end_n-start_n)}

def run(seq,p,R,D,train_terms):
 A=matrix(seq,R,D,p,train_terms);v,f=null_vector_mod(A,p)
 train=verify(seq,v,p,R,D,0,train_terms-R)
 hold=verify(seq,v,p,R,D,train_terms-R,len(seq)-R)
 flat=','.join(map(str,v)).encode()
 return {'prime':p,'order':R,'degree_bound':D,'training_terms':train_terms,'full_terms':len(seq),'matrix_shape':list(A.shape),'free_column':f,'normalization':'coordinate[free_column]=1','null_vector_sha256':hashlib.sha256(flat).hexdigest(),'null_vector_flat':v,'training_verification':train,'heldout_verification':hold}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('series');ap.add_argument('--order',type=int,required=True);ap.add_argument('--degree',type=int,required=True);ap.add_argument('--train',type=int,required=True);ap.add_argument('--output',required=True);ap.add_argument('--id',default='case')
 ns=ap.parse_args();seq=json.load(open(ns.series))['terms']
 out={'example_id':ns.id,'records':[run(seq,p,ns.order,ns.degree,ns.train) for p in (65521,65519)]}
 json.dump(out,open(ns.output,'w'),indent=2);open(ns.output,'a').write('\n')
 print([(r['prime'],r['training_verification'],r['heldout_verification'],r['null_vector_sha256']) for r in out['records']])
if __name__=='__main__':main()
