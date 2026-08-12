#!/usr/bin/env python3
from pathlib import Path
import os
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.mplconfig'))
import numpy as np
import matplotlib.pyplot as plt
FIG=ROOT/'figures'; FIG.mkdir(exist_ok=True); (ROOT/'.mplconfig').mkdir(exist_ok=True)
ks=[0.12,0.30,0.50,0.72,0.90]
phi=np.linspace(0,2*np.pi,2500)
fig=plt.figure(figsize=(11,6.5))
for i,k in enumerate(ks,1):
    ax=fig.add_subplot(2,3,i,projection='3d')
    x=k*np.sin(phi)+np.sin(2*phi)
    y=k*np.cos(phi)-np.cos(2*phi)
    z=np.sin(3*phi)
    ax.plot(x,y,z,lw=1.6); ax.set_title(f'k={k:.2f}'); ax.set_axis_off()
    ax.set_box_aspect((1,1,.8)); ax.view_init(elev=25,azim=42)
fig.suptitle('Cyclic R3 trefoil family: exact parametrized curves')
fig.tight_layout(rect=[0,0,1,.95]); fig.savefig(FIG/'cyclic_R3_family.png',dpi=220,bbox_inches='tight'); plt.close(fig)
kv=np.linspace(.04,.96,800)
Tv=np.pi*(1+kv**2)/(kv*(1-kv**2)**3*np.sqrt(kv**2+4))
fig,ax=plt.subplots(figsize=(7.4,4.3)); ax.plot(kv,Tv)
ax.set_xlabel('shape parameter k'); ax.set_ylabel('T(k)'); ax.set_title('Exact cross-product period')
ax.grid(True,alpha=.25); fig.tight_layout(); fig.savefig(FIG/'period_curve.png',dpi=220,bbox_inches='tight'); plt.close(fig)
print('wrote figures')
