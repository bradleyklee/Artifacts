#!/usr/bin/env python3
"""Quantize real action levels and tangent-match Abel-Wick energies.

For L displayed real contours, f_n=(n+1/2)/L.  Only the real action is
quantized.  Since p -> iP preserves the Hamiltonian value, the complex contour
is drawn at the same energy and is tangent to the real contour at their shared
turning point(s).
"""
from __future__ import annotations
import argparse, csv
from pathlib import Path
import contourpy
import numpy as np
from matplotlib.path import Path as MplPath
from scipy.optimize import brentq

SCRIPT_DIR=Path(__file__).resolve().parent
if SCRIPT_DIR.name=='scripts':
    ROOT=SCRIPT_DIR.parent; PAYLOAD=ROOT/'payload'
else:
    ROOT=SCRIPT_DIR; PAYLOAD=SCRIPT_DIR
OUTPUT=PAYLOAD/'quantized_levels_for_figure.csv'
LEVEL_COUNT=11
SEP_EPS=1e-6


def h_real(p,q):
    return p**2-q**2+p**4/25-(6/5)*p**2*q**2+q**4

def h_ip(p,q):
    return -p**2-q**2+p**4/25+(6/5)*p**2*q**2+q**4

def area(seg):
    x,y=seg[:,0],seg[:,1]
    return .5*abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

def component(gen,lev,point):
    lines=[s for s in gen.lines(float(lev)) if len(s)>=40]
    closed=[s for s in lines if np.linalg.norm(s[0]-s[-1])<1e-6]
    cand=closed or lines
    if not cand: raise RuntimeError(f'no contour at {lev}')
    inside=[s for s in cand if MplPath(s).contains_point(point)]
    if inside: return max(inside,key=area)
    target=np.asarray(point)
    return min(cand,key=lambda s:np.sum((np.mean(s,axis=0)-target)**2))

def generators():
    x=np.linspace(-1.12,1.12,1800)
    y=np.linspace(-.96,.96,1600)
    X,Y=np.meshgrid(x,y)
    return (
      contourpy.contour_generator(x=x,y=y,z=h_real(Y,X),name='serial'),
      contourpy.contour_generator(x=x,y=y,z=h_ip(Y,X),name='serial')
    )

def generate_rows(L=LEVEL_COUNT):
    gr,gi=generators()
    real_total=area(component(gr,-1/8-SEP_EPS,(1/np.sqrt(2),0)))
    def rf(E): return area(component(gr,E,(1/np.sqrt(2),0)))/real_total
    rows=[]
    for n in range(L):
        f=(n+.5)/L
        re=brentq(lambda E:rf(E)-f,-.25+1e-4,-.125-SEP_EPS,xtol=2e-13,rtol=2e-13)
        ie=re
        rows.append({'n':n,'action_fraction_(n+1/2)/L':f,'real_E':re,'real_z':re+.25,'ip_E':ie})
    return rows

def write(rows,path=OUTPUT):
    fields=['n','action_fraction_(n+1/2)/L','real_E','real_z','ip_E']
    with path.open('w',newline='',encoding='utf-8') as h:
        w=csv.DictWriter(h,fieldnames=fields);w.writeheader()
        for r in rows:
            w.writerow({k:(r[k] if k=='n' else f'{float(r[k]):.16g}') for k in fields})

def read(path=OUTPUT):
    out=[]
    with path.open(newline='',encoding='utf-8') as h:
        for r in csv.DictReader(h):
            frac_key='action_fraction_(n+1/2)/L' if 'action_fraction_(n+1/2)/L' in r else 'fraction_(n+1/2)/(N+1)'
            out.append({'n':int(r['n']),'action_fraction_(n+1/2)/L':float(r[frac_key]),'real_E':float(r['real_E']),'real_z':float(r['real_z']),'ip_E':float(r['ip_E'])})
    return out

def check(saved,new,tol_fraction=6e-3):
    if len(saved)!=len(new): raise SystemExit('row-count mismatch')
    gr,gi=generators()
    real_total=area(component(gr,-1/8-SEP_EPS,(1/np.sqrt(2),0)))
    for row in saved:
        f=float(row['action_fraction_(n+1/2)/L'])
        rf=area(component(gr,float(row['real_E']),(1/np.sqrt(2),0)))/real_total
        if abs(rf-f)>tol_fraction:
            raise SystemExit(f'real action fraction mismatch n={row["n"]}: {rf} vs {f}')
        if abs(float(row['ip_E'])-float(row['real_E']))>1e-12:
            raise SystemExit(f'tangent energy mismatch n={row["n"]}')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    rows=generate_rows()
    if args.check:
        check(read(),rows);print('QUANTIZED LEVELS PASS (11 real-action levels; IP energies tangent-matched)')
    else:
        write(rows);print(f'wrote {OUTPUT.relative_to(ROOT)}')
if __name__=='__main__':main()
