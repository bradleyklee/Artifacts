#!/usr/bin/env python3
from fractions import Fraction as Q
from generic_even_p_quintic import fadd, monomial_fourier, period_coefficients

# E1 = p^2+q^2 + (2p^4-3p^2q^2+5q^4)/8 + (3p^2q-2q^3)/10
MONOMIALS={
 3:[(2,1,Q(3,10)),(0,3,Q(-1,5))],
 4:[(4,0,Q(1,4)),(2,2,Q(-3,8)),(0,4,Q(5,8))],
}

def components():
 out=[]
 for d,mons in sorted(MONOMIALS.items()):
  g={}
  for pe,qe,c in mons:g=fadd(g,monomial_fourier(pe,qe,c))
  out.append((d,g))
 return out

def energy_sparse():
 E={(0,2,0):Q(1),(0,0,2):Q(1)}
 for mons in MONOMIALS.values():
  for pe,qe,c in mons:E[(0,pe,qe)]=E.get((0,pe,qe),Q(0))+c
 return E

if __name__=='__main__':
 import argparse,json
 ap=argparse.ArgumentParser();ap.add_argument('--terms',type=int,default=240);ap.add_argument('--output')
 ns=ap.parse_args();seq=period_coefficients(components(),ns.terms)
 rec={'example_id':'semi_random_quartic_q1_p_even','E':'p**2+q**2+(2*p**4-3*p**2*q**2+5*q**4)/8+(3*p**2*q-2*q**3)/10','H':'E/2','symmetry':{'p_reflection':True,'q_reflection':False},'quantity':'T(alpha)/(2*pi)','terms':[str(x) for x in seq]}
 txt=json.dumps(rec,indent=2)+'\n'
 if ns.output:open(ns.output,'w').write(txt)
 else:print(txt)
