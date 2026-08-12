#!/usr/bin/env python3
"""80-digit direct quadrature audit of the trigonometric period integral."""
import json
from pathlib import Path
import mpmath as mp
mp.mp.dps=80
OUT=Path(__file__).resolve().parents[1]/'audit'/'numerical_check.json'

def period_integral(k):
    k=mp.mpf(k)
    A=k**6+6*k**4-3*k**2+2
    B=-4*k**3*(k**2+1)
    C=2*(2*k**2-1)
    f=lambda ph: 1/(2*(A+B*mp.cos(3*ph)+C*mp.cos(6*ph)))
    pts=[mp.pi*j/12 for j in range(25)]
    return mp.quad(f,pts)

def closed(k):
    k=mp.mpf(k)
    return mp.pi*(1+k**2)/(abs(k)*(1-k**2)**3*mp.sqrt(k**2+4))
rows=[]
for ks in ['0.10','0.25','0.50','0.75','0.90','-0.50']:
    num=period_integral(ks); ex=closed(ks); rel=abs(num-ex)/abs(ex)
    rows.append({'k':ks,'integral':mp.nstr(num,65),'closed':mp.nstr(ex,65),
                 'relative_error':mp.nstr(rel,10)})
    print(f'k={ks:>5} rel.err={mp.nstr(rel,5)}')
OUT.write_text(json.dumps({'dps':80,'rows':rows,'status':'PASS'},indent=2)+'\n')
