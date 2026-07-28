#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
import math
import numpy as np
import pandas as pd
import sympy as sp
from numpy.polynomial.legendre import leggauss
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib import cm, colors

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compute_mesh_area_series import compute, restricted_map_xy

OUT=Path(__file__).resolve().parents[1]
DATA=OUT/'data'
FIGURES=OUT/'figures'
DATA.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)
SQ3=math.sqrt(3.0)
LAM=2.0/(3.0*SQ3)
J0=math.sqrt(6267.0)/4.0

# Numeric map in harmonic coordinates.
def uv_from_xy(x,y):
    u=1/3+x/3+y/(3*SQ3)
    v=1/3-x/3+y/(3*SQ3)
    return u,v

def G_xy(x,y):
    u,v=uv_from_xy(np.asarray(x),np.asarray(y))
    d=u-v; s=u+v
    U=-(3*d*d-2)*(243*d**4*s-171*d**4-324*d*d*s+156*d*d+108*s-4)/32.0
    V=9*d*(81*d**4*s-57*d**4-108*d*d*s+52*d*d+36*s-4)/16.0
    W=-d*(27*d*d*s-19*d*d-8)/4.0
    return np.stack([U,V,W],axis=-1)

# Lambdify exact cross-product norm.
xs,ys=sp.symbols('x y', real=True)
Ue,Ve,We=restricted_map_xy()
Gx=sp.Matrix([sp.diff(Ue,xs),sp.diff(Ve,xs),sp.diff(We,xs)])
Gy=sp.Matrix([sp.diff(Ue,ys),sp.diff(Ve,ys),sp.diff(We,ys)])
Qe=sp.expand(Gx.cross(Gy).dot(Gx.cross(Gy)))
Jfun=sp.lambdify((xs,ys),sp.sqrt(Qe),'numpy')


def radial_triangle_boundary(theta):
    c=np.cos(theta); s=np.sin(theta)
    candidates=[]
    a=c+s/SQ3
    mask=a<0
    candidates.append(np.where(mask,-1.0/a,np.inf))
    a=-c+s/SQ3
    mask=a<0
    candidates.append(np.where(mask,-1.0/a,np.inf))
    mask=s>0
    candidates.append(np.where(mask,SQ3/(2.0*s),np.inf))
    return np.minimum.reduce(candidates)


def Mpolar(r,theta):
    return r*r-LAM*r**3*np.sin(3*theta)


def boundary_radius(m,theta):
    theta=np.asarray(theta)
    lo=np.zeros_like(theta,dtype=float)
    hi=radial_triangle_boundary(theta)
    # M(hi)=1, and the radial segment stays in the triangle.
    for _ in range(70):
        mid=(lo+hi)/2
        val=Mpolar(mid,theta)
        lo=np.where(val<m,mid,lo)
        hi=np.where(val>=m,mid,hi)
    return (lo+hi)/2


def quadrature_area(m,ntheta=320,nrho=90):
    zt,wt=leggauss(ntheta)
    theta=math.pi*(zt+1.0)
    wtheta=math.pi*wt
    zr,wr=leggauss(nrho)
    rho=(zr+1.0)/2.0
    wrho=wr/2.0
    R=boundary_radius(m,theta)
    # broadcast rho x theta
    rr=rho[:,None]*R[None,:]
    tt=theta[None,:]
    xx=rr*np.cos(tt); yy=rr*np.sin(tt)
    J=Jfun(xx,yy)
    integrand=J*rho[:,None]*R[None,:]**2
    return float(np.sum(integrand*wrho[:,None]*wtheta[None,:]))


def structured_mesh(m,nr=12,ntheta=60):
    theta=np.linspace(0,2*math.pi,ntheta,endpoint=False)
    R=boundary_radius(m,theta)
    verts=[G_xy(0.0,0.0)]
    domain=[np.array([0.0,0.0])]
    # rings 1..nr
    for j in range(1,nr+1):
        frac=j/nr
        r=frac*R
        x=r*np.cos(theta); y=r*np.sin(theta)
        pts=G_xy(x,y)
        verts.extend(list(pts))
        domain.extend(list(np.column_stack([x,y])))
    verts=np.asarray(verts,float)
    domain=np.asarray(domain,float)
    tris=[]
    # center fan
    first=1
    for k in range(ntheta):
        tris.append((0,first+k,first+(k+1)%ntheta))
    # between rings
    for j in range(1,nr):
        a0=1+(j-1)*ntheta
        b0=1+j*ntheta
        for k in range(ntheta):
            k1=(k+1)%ntheta
            tris.append((a0+k,b0+k,b0+k1))
            tris.append((a0+k,b0+k1,a0+k1))
    tris=np.asarray(tris,int)
    return domain,verts,tris


def mesh_area(verts,tris):
    a=verts[tris[:,0]]; b=verts[tris[:,1]]; c=verts[tris[:,2]]
    return float(0.5*np.linalg.norm(np.cross(b-a,c-a),axis=1).sum())


def separatrix_edges(n=600):
    # vertices in x,y corresponding to (u,v)=(0,0),(1,0),(0,1)
    P=np.array([[0.0,-SQ3],[1.5,SQ3/2],[-1.5,SQ3/2]])
    images=[]
    for i,j in [(0,1),(1,2),(2,0)]:
        t=np.linspace(0,1,n)
        xy=(1-t)[:,None]*P[i]+t[:,None]*P[j]
        images.append(G_xy(xy[:,0],xy[:,1]))
    return images


def generate_headliner(m=0.70,nr=12,ntheta=60):
    dom,verts,tris=structured_mesh(m,nr,ntheta)
    area=mesh_area(verts,tris)
    faces=verts[tris]
    # radial fractions from domain centroid of each triangle
    r=np.linalg.norm(dom,axis=1)
    tri_r=r[tris].mean(axis=1)
    tri_r=(tri_r-tri_r.min())/(tri_r.max()-tri_r.min()+1e-15)
    cmap=plt.get_cmap('coolwarm')
    facecols=cmap(0.05+0.68*tri_r) # reserve pure red
    facecols[:,3]=0.82

    fig=plt.figure(figsize=(12.5,6.6))
    # domain inset / left
    ax1=fig.add_subplot(121)
    poly=PolyCollection(dom[tris],facecolors=facecols,edgecolors=(0.2,0.2,0.2,0.35),linewidths=0.35)
    ax1.add_collection(poly)
    ax1.autoscale_view()
    tri=np.array([[0,-SQ3],[1.5,SQ3/2],[-1.5,SQ3/2],[0,-SQ3]])
    ax1.plot(tri[:,0],tri[:,1],color='red',linewidth=2.5,label='separatrix')
    ax1.set_aspect('equal',adjustable='box')
    ax1.set_title(f'Domain region $D_m$ and its triangular mesh\n$m={m:.2f}$')
    ax1.set_xlabel('$x$'); ax1.set_ylabel('$y$')
    ax1.legend(loc='upper right')
    ax1.grid(True,alpha=0.2)

    ax2=fig.add_subplot(122,projection='3d')
    pc=Poly3DCollection(faces,facecolors=facecols,edgecolors=(0.1,0.1,0.1,0.40),linewidths=0.30)
    ax2.add_collection3d(pc)
    for edge in separatrix_edges():
        ax2.plot(edge[:,0],edge[:,1],edge[:,2],color='red',linewidth=2.3)
    q=np.array([-0.25,0,0])
    ax2.scatter([q[0]],[q[1]],[q[2]],color='red',s=35)
    mins=verts.min(axis=0); maxs=verts.max(axis=0)
    # include separatrix ranges
    seps=np.vstack(separatrix_edges(150))
    mins=np.minimum(mins,seps.min(axis=0)); maxs=np.maximum(maxs,seps.max(axis=0))
    ctr=(mins+maxs)/2; span=(maxs-mins)*0.58
    ax2.set_xlim(ctr[0]-span[0],ctr[0]+span[0])
    ax2.set_ylim(ctr[1]-span[1],ctr[1]+span[1])
    ax2.set_zlim(ctr[2]-span[2],ctr[2]+span[2])
    ax2.set_box_aspect(np.maximum(maxs-mins,1e-6))
    ax2.view_init(elev=23,azim=-61)
    ax2.set_xlabel('$U$'); ax2.set_ylabel('$V$'); ax2.set_zlabel('$W$')
    ax2.set_title('The same triangles after the polynomial map\n(actual 3-D mesh area)')
    fig.suptitle('A filled elliptic oval mapped into three-dimensional range space',fontsize=16,y=0.99)
    fig.text(0.5,0.012,f'Triangulated range area shown: {area:.8f}  ({len(tris):,} triangles)',ha='center',fontsize=10)
    fig.tight_layout(rect=[0,0.035,1,0.965])
    path=FIGURES/'true_surface_mesh_headliner.png'
    fig.savefig(path,dpi=240)
    plt.close(fig)
    return path,area,len(tris)


def main():
    # Exact series.
    exact=compute(20)
    coeffs=exact['coeffs']
    C=2*27*2089**2
    rows=[]
    for n in range(1,21):
        p=sp.factor(coeffs[n])
        derivative_scaled=sp.factor(n*p*C**(n-1))
        rows.append({
            'n':n,
            'area_coefficient_c_n':str(p),
            'scaled_shell_coefficient':str(derivative_scaled),
            'is_integer':bool(sp.denom(derivative_scaled)==1),
        })
    pd.DataFrame(rows).to_csv(DATA/'true_surface_area_series.csv',index=False)

    # Validation values.
    ms=[0.02,0.05,0.10,0.20,0.40,0.60,0.70]
    val=[]
    for m in ms:
        ref=quadrature_area(m,ntheta=360,nrho=100)
        series=[]
        for N in [4,8,12,20]:
            norm=sum(float(coeffs[n])*m**n for n in range(1,N+1))
            series.append(math.pi*J0*norm)
        row={'m':m,'quadrature_area':ref}
        for N,a in zip([4,8,12,20],series): row[f'series_{N}']=a
        for nr,nt in [(6,24),(12,48),(24,96),(40,160)]:
            _,verts,tris=structured_mesh(m,nr,nt)
            row[f'mesh_{len(tris)}tri']=mesh_area(verts,tris)
        val.append(row)
        print('m',m,'area',ref)
    vdf=pd.DataFrame(val)
    vdf.to_csv(DATA/'true_surface_area_validation.csv',index=False)

    # Headliner.
    path,area,ntri=generate_headliner(0.70,14,72)

    # Convergence plot at m=.70.
    m0=.70
    ref=quadrature_area(m0,ntheta=500,nrho=130)
    ns=[]; errs=[]; vals=[]
    for nr,nt in [(3,12),(4,16),(6,24),(8,32),(12,48),(16,64),(24,96),(32,128),(48,192)]:
        _,vv,tt=structured_mesh(m0,nr,nt)
        a=mesh_area(vv,tt)
        ns.append(len(tt)); vals.append(a); errs.append(abs(a-ref))
    fig=plt.figure(figsize=(7.7,5.2)); ax=fig.add_subplot(111)
    ax.loglog(ns,errs,marker='o')
    ax.set_xlabel('number of triangles'); ax.set_ylabel('absolute error')
    ax.set_title(r'Mesh convergence for $m=0.70$')
    ax.grid(True,which='both',alpha=.35)
    fig.tight_layout(); fig.savefig(FIGURES/'true_surface_mesh_convergence.png',dpi=240); plt.close(fig)

    # Function plot normalized.
    grid=np.linspace(.005,.82,55)
    direct=np.array([quadrature_area(float(mm),ntheta=220,nrho=70)/(math.pi*J0) for mm in grid])
    ser12=np.array([sum(float(coeffs[n])*mm**n for n in range(1,13)) for mm in grid])
    ser20=np.array([sum(float(coeffs[n])*mm**n for n in range(1,21)) for mm in grid])
    fig=plt.figure(figsize=(7.8,5.3)); ax=fig.add_subplot(111)
    ax.plot(grid,direct,label='direct surface integral',linewidth=2.1)
    ax.plot(grid,ser12,'--',label='12-term series',linewidth=1.5)
    ax.plot(grid,ser20,':',label='20-term series',linewidth=2.0)
    ax.set_xlabel('$m$'); ax.set_ylabel(r'$\Psi(m)=\mathcal{A}(m)/(\pi J_0)$')
    ax.set_title('True 3-D mesh area and its harmonic-center series')
    ax.grid(True,alpha=.3); ax.legend()
    fig.tight_layout(); fig.savefig(FIGURES/'true_surface_area_function.png',dpi=240); plt.close(fig)

    # Save concise exact formula report.
    report=[]
    report.append('TRUE 3-D SURFACE AREA\n')
    report.append('A(m) = integral integral over D_m of ||G_x cross G_y|| dx dy.')
    report.append('D_m = {M(x,y)<=m}, with')
    report.append('M=x^2+y^2+(2/(3sqrt(3))) y(y^2-3x^2).')
    report.append(f'J0=||G_x cross G_y||(0,0)=sqrt(6267)/4.')
    report.append('Psi(m)=A(m)/(pi J0)=sum c_n m^n.')
    for n in range(1,13): report.append(f'c_{n} = {coeffs[n]}')
    report.append('Shell derivative: Psi\'(m)=sum_{k>=0} b_k m^k.')
    report.append(f'With C={C}, b_k*C^k is integral for k=0..19 (exactly checked).')
    (DATA/'true_surface_area_notes.txt').write_text('\n'.join(report),encoding='utf-8')

    print('headliner',path,area,ntri)
    print(vdf.to_string(index=False))

if __name__=='__main__':
    main()
