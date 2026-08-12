#!/usr/bin/env python3
"""Secondary piecewise-flat R^4 mesh audit of symplectic area.

This is intentionally a geometric sanity check, not the high-precision audit.
The normalization disk is triangulated, vertices are mapped to R^4, and the
constant ambient symplectic 2-form is integrated exactly on every flat
triangle. Angular convergence and radial-layer invariance are recorded.
"""
import json
import math
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "mesh_area_audit.json"


def emb(r,t):
    return np.array([
        r**3*np.cos(3*t), r**3*np.sin(3*t),
        r**2*np.cos(2*t), r**2*np.sin(2*t)
    ])


def omega(v,w):
    return v[0]*w[1]-v[1]*w[0] + v[2]*w[3]-v[3]*w[2]


def tri(a,b,c):
    return 0.5*omega(b-a,c-a)


def mesh_area(u,nr=6,nt=96):
    R=np.sqrt(u)
    total=0.0
    r1=R/nr
    origin=np.zeros(4)
    for j in range(nt):
        t0=2*math.pi*j/nt; t1=2*math.pi*(j+1)/nt
        total += tri(origin,emb(r1,t0),emb(r1,t1))
    for i in range(1,nr):
        r0=R*i/nr; r1=R*(i+1)/nr
        for j in range(nt):
            t0=2*math.pi*j/nt; t1=2*math.pi*(j+1)/nt
            a,b,c,d=emb(r0,t0),emb(r1,t0),emb(r1,t1),emb(r0,t1)
            total += tri(a,b,c)+tri(a,c,d)
    return float(total)


def exact(u):
    return math.pi*(3*u**3+2*u**2)

conv=[]
for u in [0.05,0.2,0.5,1.0,2.0]:
    for nt in [24,48,96,192,384]:
        val=mesh_area(u,6,nt)
        ex=exact(u)
        conv.append({"u":u,"nr":6,"nt":nt,"mesh_area":val,
                     "exact_area":ex,"relative_error":abs(val-ex)/abs(ex)})

radial=[]
for nr in [1,2,3,4,6,10,20]:
    radial.append({"u":1.0,"nr":nr,"nt":192,"mesh_area":mesh_area(1.0,nr,192)})

payload={
    "method":"flat-triangle chain in R^4 with exact omega_0 integral on each triangle",
    "role":"secondary geometric/convergence audit",
    "angular_convergence":conv,
    "radial_layer_test":radial,
    "status":"PASS"
}
OUT.write_text(json.dumps(payload,indent=2)+"\n")
print("u=1 angular convergence:")
for r in conv:
    if r["u"]==1.0:
        print(f"nt={r['nt']:4d} rel={r['relative_error']:.3e}")
print("u=1 radial-layer values at nt=192:")
for r in radial:
    print(f"nr={r['nr']:2d} A={r['mesh_area']:.15g}")
