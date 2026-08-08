#!/usr/bin/env python3
import json,sys
from modular_ode_screen_numpy import matrix,rank_mod

def scan(path,p=65521,nterms=90,maxr=10,maxd=20):
 seq=json.load(open(path))['terms']; hits=[]; mins=[]
 for r in range(1,maxr+1):
  first=None
  for d in range(0,maxd+1):
   u=(r+1)*(d+1);eq=nterms-r
   if u>eq:break
   M=matrix(seq,r,d,p,nterms);rk=rank_mod(M,p);nu=u-rk
   if nu:
    first=(d,nu);hits.append((r,d,nu));break
  mins.append((r,first))
 return mins,hits
if __name__=='__main__':
 for f in sys.argv[1:]:
  mins,hits=scan(f);print(f);print('first_by_order',mins);print('hits',hits)
