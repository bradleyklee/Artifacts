import os
os.environ['MPLCONFIGDIR'] = os.path.join(os.path.dirname(__file__), '.mplconfig')

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(__file__)
E_STAR = 4.0/27.0
VIEW = np.array([0.98692742, 0.15800316, 0.03176909], dtype=float)


def positive_u(E):
    roots = np.roots([1.0, 1.0, 0.0, -float(E)])
    rr = [r.real for r in roots if abs(r.imag) < 1e-10 and r.real > 0]
    assert len(rr) == 1
    return float(rr[0])


def stereo_curve(E, n=2200, normalize=True):
    """Return stereographic R^3 coordinates of K_E and u(E).

    C: z^2 = w^3 with z=s^3, w=s^2, s=sqrt(u)e^{i theta}.
    Stereographic projection is from north pole y2=R to y2=0.
    If normalize=True, divide R^3 coordinates by R=sqrt(E) so that
    panels compare shape rather than overall physical scale.
    """
    u = positive_u(E)
    R = np.sqrt(E)
    th = np.linspace(0.0, 2*np.pi, n, endpoint=False)
    z = u**1.5 * np.exp(3j*th)
    w = u * np.exp(2j*th)
    x1, y1 = z.real, z.imag
    x2, y2 = w.real, w.imag
    fac = R/(R-y2)
    P = np.column_stack((fac*x1, fac*y1, fac*x2))
    if normalize:
        P = P/R
    return P, th, u


def basis_from_view(v):
    v = np.asarray(v, dtype=float)
    v /= np.linalg.norm(v)
    a = np.array([0.0, 0.0, 1.0])
    if abs(a @ v) > 0.90:
        a = np.array([0.0, 1.0, 0.0])
    e1 = np.cross(a, v)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(v, e1)
    return e1, e2, v


def screen_depth(P, view=VIEW):
    e1, e2, v = basis_from_view(view)
    return np.column_stack((P @ e1, P @ e2)), P @ v


def crossings(xy, depth):
    """All transverse crossings of a closed polygonal curve.

    Returns segment indices i,j, segment parameters a,b, common screen point,
    and interpolated depths di,dj.
    """
    n = len(xy)
    q = np.roll(xy, -1, axis=0)
    out = []
    for i in range(n):
        p = xy[i]
        r = q[i] - p
        js = np.arange(i+2, n)
        if i == 0:
            js = js[js != n-1]
        if not len(js):
            continue
        s = q[js] - xy[js]
        qp = xy[js] - p
        den = r[0]*s[:,1] - r[1]*s[:,0]
        good = np.abs(den) > 1e-12
        if not np.any(good):
            continue
        js = js[good]
        s = s[good]
        qp = qp[good]
        den = den[good]
        aa = (qp[:,0]*s[:,1] - qp[:,1]*s[:,0]) / den
        bb = (qp[:,0]*r[1] - qp[:,1]*r[0]) / den
        hit = (aa > 1e-6) & (aa < 1-1e-6) & (bb > 1e-6) & (bb < 1-1e-6)
        for j, a, b in zip(js[hit], aa[hit], bb[hit]):
            pt = p + a*r
            di = depth[i] + a*(depth[(i+1) % n] - depth[i])
            dj = depth[j] + b*(depth[(j+1) % n] - depth[j])
            out.append((i, int(j), float(a), float(b), pt, float(di), float(dj)))
    return out


def interp_periodic(arr, s):
    n = len(arr)
    s %= n
    i = int(np.floor(s))
    a = s - i
    return (1-a)*arr[i] + a*arr[(i+1) % n]


def marker_points(xy, cs, delta=7.0):
    """Put a red marker on the over strand and green on under strand.

    The markers are moved a few samples away from the exact common screen
    point so both remain visible while staying on the computed curve.
    """
    red = []
    green = []
    for i, j, a, b, pt, di, dj in cs:
        si = i + a
        sj = j + b
        if di > dj:
            so, su = si, sj
        else:
            so, su = sj, si
        red.append(interp_periodic(xy, so + delta))
        green.append(interp_periodic(xy, su - delta))
    return np.asarray(red), np.asarray(green)




def branch_segment(xy, s0, halfspan=18.0, samples=41):
    """Return a short actual-curve segment centered at periodic sample s0.

    The returned polyline follows the sampled projected knot rather than a
    tangent approximation. This makes the crossing overlay reproducible from
    the same coordinate data used to locate the crossing.
    """
    ss = np.linspace(s0-halfspan, s0+halfspan, samples)
    return np.asarray([interp_periodic(xy, s) for s in ss])


def crossing_segments(xy, cs, halfspan=18.0):
    """Return (red_over, green_under) short branch segments for crossings.

    Both segments are centered at the exact screen crossing. The green
    under-segment is drawn first, and the red over-segment is drawn last, so
    the graphic convention itself preserves over/under order.
    """
    out=[]
    for i, j, a, b, pt, di, dj in cs:
        si=i+a; sj=j+b
        if di > dj:
            so, su = si, sj
        else:
            so, su = sj, si
        red = branch_segment(xy, so, halfspan=halfspan)
        green = branch_segment(xy, su, halfspan=halfspan)
        out.append((red, green))
    return out



def tangent_at(xy, s0, delta=3.0):
    """Unit screen tangent at periodic curve parameter s0."""
    t = interp_periodic(xy, s0 + delta) - interp_periodic(xy, s0 - delta)
    nrm = np.linalg.norm(t)
    if nrm == 0:
        raise ValueError('degenerate screen tangent')
    return t / nrm


def straight_crossing_segments(xy, cs, half_length):
    """Short straight branch-direction segments centered at crossings.

    Tangent directions and depth order come from the sampled curve.  The
    segments have equal screen length, making all three crossings visible.
    """
    out=[]
    for i, j, a, b, pt, di, dj in cs:
        si=i+a; sj=j+b
        ti=tangent_at(xy,si); tj=tangent_at(xy,sj)
        if di > dj:
            to,tu=ti,tj
        else:
            to,tu=tj,ti
        red=np.vstack((pt-half_length*to, pt+half_length*to))
        green=np.vstack((pt-half_length*tu, pt+half_length*tu))
        out.append((red,green))
    return out

def crossing_points_3d(P, cs):
    red, green = [], []
    pairs = []
    for i, j, a, b, pt, di, dj in cs:
        Pi = (1-a)*P[i] + a*P[(i+1) % len(P)]
        Pj = (1-b)*P[j] + b*P[(j+1) % len(P)]
        if di > dj:
            over, under = Pi, Pj
        else:
            over, under = Pj, Pi
        red.append(over)
        green.append(under)
        pairs.append((over, under))
    return np.asarray(red), np.asarray(green), pairs


# Energy levels in the positive interval up to the first positive singular
# coefficient of the q-ODE, E_* = 4/27 (equivalently u=1/3).
fractions = [1/64, 1/16, 1/4, 1/2, 3/4, 1]
energies = [E_STAR*f for f in fractions]

# Build composite: one explicit 3D depth view plus six full projected curves.
fig = plt.figure(figsize=(10.2, 3.65))
gs = fig.add_gridspec(2, 5, width_ratios=[1.45, 1, 1, 1, 1], wspace=0.10, hspace=0.16)

# Left: 3D curve in the screen/depth basis at E=E_*.
P, th, ustar = stereo_curve(E_STAR, n=2600, normalize=True)
e1, e2, v = basis_from_view(VIEW)
Q = np.column_stack((P @ e1, P @ e2, P @ v))
xy = Q[:, :2]
depth = Q[:, 2]
cs = crossings(xy, depth)
assert len(cs) == 3
red3, green3, pairs = crossing_points_3d(Q, cs)

ax3 = fig.add_subplot(gs[:, 0], projection='3d')
ax3.plot(Q[:,0], Q[:,1], Q[:,2], color='black', linewidth=1.25)
for over, under in pairs:
    ax3.plot([over[0], under[0]], [over[1], under[1]], [over[2], under[2]],
             color='0.72', linewidth=0.8, linestyle='--')
ax3.scatter(red3[:,0], red3[:,1], red3[:,2], s=28, color='red', depthshade=False, zorder=5)
ax3.scatter(green3[:,0], green3[:,1], green3[:,2], s=28, color='green', depthshade=False, zorder=5)
ax3.view_init(elev=18, azim=-58)
ax3.set_axis_off()
mins, maxs = Q.min(0), Q.max(0)
ctr = (mins+maxs)/2
span = (maxs-mins).max()/2*1.10
ax3.set_xlim(ctr[0]-span, ctr[0]+span)
ax3.set_ylim(ctr[1]-span, ctr[1]+span)
ax3.set_zlim(ctr[2]-span, ctr[2]+span)
ax3.set_title(r'$E=E_*=4/27$'+'\n'+r'screen/depth coordinates', fontsize=8.5, pad=0)

# Right: six continuous whole-curve screen projections with crossing markers.
family_axes = []
records = []
for k, (frac, E) in enumerate(zip(fractions, energies)):
    row = k // 4
    col = 1 + (k % 4)
    # last two panels go on second row, centered across cols 2 and 3
    if k >= 4:
        col = 2 + (k-4)
    ax = fig.add_subplot(gs[row, col])
    family_axes.append(ax)
    Pk, _, uk = stereo_curve(E, n=1800, normalize=True)
    xyk, dk = screen_depth(Pk, VIEW)
    csk = crossings(xyk, dk)
    assert len(csk) == 3, (E, len(csk))
    red, green = marker_points(xyk, csk, delta=7.0)
    ax.plot(xyk[:,0], xyk[:,1], color='black', linewidth=1.0)
    ax.scatter(red[:,0], red[:,1], s=12, color='red', zorder=4)
    ax.scatter(green[:,0], green[:,1], s=12, color='green', zorder=4)
    ax.set_aspect('equal', adjustable='box')
    ax.set_axis_off()
    label = r'$E/E_*=' + (str(frac) if frac == 1 else f'{frac:g}') + '$'
    ax.set_title(label, fontsize=7.4, pad=0)
    # pad so the entire curve is visible
    xmin,ymin = xyk.min(0); xmax,ymax = xyk.max(0)
    dx,dy=xmax-xmin,ymax-ymin
    ax.set_xlim(xmin-.06*dx,xmax+.06*dx)
    ax.set_ylim(ymin-.06*dy,ymax+.06*dy)
    records.append({
        'E_over_Estar': frac,
        'E': E,
        'u': uk,
        'crossings': [
            {'segments':[int(c[0]),int(c[1])], 'a':c[2], 'b':c[3],
             'screen':[float(c[4][0]),float(c[4][1])],
             'depths':[c[5],c[6]], 'over':'i' if c[5]>c[6] else 'j'}
            for c in csk
        ]
    })

# Legend in unused lower-right cell.
axleg = fig.add_subplot(gs[1,4])
axleg.axis('off')
legend_handles = [
    Line2D([0],[0], marker='o', linestyle='None', markerfacecolor='red', markeredgecolor='red', markersize=5, label='over strand'),
    Line2D([0],[0], marker='o', linestyle='None', markerfacecolor='green', markeredgecolor='green', markersize=5, label='under strand'),
]
axleg.legend(handles=legend_handles, loc='center', frameon=False, fontsize=7.3, handletextpad=.4)
axleg.text(.5,.22, r'$E_*=4/27$', ha='center', va='center', fontsize=7.5)
axleg.text(.5,.10, r'$u(E_*)=1/3$', ha='center', va='center', fontsize=7.5)

fig.savefig(os.path.join(HERE, 'trefoil_family_crossings.pdf'), bbox_inches='tight', pad_inches=0.015)
fig.savefig(os.path.join(HERE, 'trefoil_family_crossings.png'), dpi=260, bbox_inches='tight', pad_inches=0.015)
plt.close(fig)

with open(os.path.join(HERE, 'crossing_family.json'), 'w') as f:
    json.dump({'E_star':E_STAR, 'view':VIEW.tolist(), 'records':records}, f, indent=2)

print('E_star=', E_STAR, 'u_star=', ustar)
print('energy crossings=', [(r['E_over_Estar'], len(r['crossings'])) for r in records])


# Publication figure requested by the user: only complete projected curves,
# no crossing gaps. Red dots lie on over-strands and green dots on under-strands.
fractions_pub = [1/256, 1/64, 1/16, 1/8, 1/4, 1/2, 3/4, 1]
pub_data=[]
for frac in fractions_pub:
    E=E_STAR*frac
    Pk,_,uk=stereo_curve(E,n=2200,normalize=True)
    xyk,dk=screen_depth(Pk,VIEW)
    csk=crossings(xyk,dk)
    assert len(csk)==3, (E,len(csk))
    red,green=marker_points(xyk,csk,delta=14.0)
    pub_data.append((frac,E,uk,xyk,red,green,csk))

allxy=np.vstack([d[3] for d in pub_data])
xmin,ymin=allxy.min(0); xmax,ymax=allxy.max(0)
dx,dy=xmax-xmin,ymax-ymin
xmin-=.045*dx; xmax+=.045*dx; ymin-=.045*dy; ymax+=.045*dy

fig,axs=plt.subplots(2,4,figsize=(10.2,4.15))
for ax,(frac,E,uk,xyk,red,green,csk) in zip(axs.ravel(),pub_data):
    ax.plot(xyk[:,0],xyk[:,1],color='black',linewidth=1.2)
    ax.scatter(red[:,0],red[:,1],s=17,color='red',zorder=5)
    ax.scatter(green[:,0],green[:,1],s=17,color='green',zorder=5)
    ax.set_aspect('equal',adjustable='box')
    ax.set_xlim(xmin,xmax); ax.set_ylim(ymin,ymax)
    ax.set_axis_off()
    if frac == 1:
        title=r'$E/E_*=1$'
    elif frac in (1/2,1/4,1/8,1/16,1/64,1/256):
        den=round(1/frac)
        title=rf'$E/E_*=1/{den}$'
    else:
        title=rf'$E/E_*={frac:g}$'
    ax.set_title(title,fontsize=8.5,pad=1)

handles=[
    Line2D([0],[0],marker='o',linestyle='None',markerfacecolor='red',markeredgecolor='red',markersize=5,label='over'),
    Line2D([0],[0],marker='o',linestyle='None',markerfacecolor='green',markeredgecolor='green',markersize=5,label='under'),
]
fig.legend(handles=handles,loc='lower center',ncol=2,frameon=False,fontsize=8,
           bbox_to_anchor=(0.5,-0.01),handletextpad=.35,columnspacing=1.2)
fig.tight_layout(rect=(0,0.045,1,1),pad=.15,w_pad=.25,h_pad=.45)
fig.savefig(os.path.join(HERE,'trefoil_energy_family.pdf'),bbox_inches='tight',pad_inches=.015)
fig.savefig(os.path.join(HERE,'trefoil_energy_family.png'),dpi=280,bbox_inches='tight',pad_inches=.015)
plt.close(fig)

# Final publication view used by trefoil_certificate.tex.  The whole projected
# curve is black. At each exact screen crossing, a short green segment marks
# the under branch and a short red segment marks the over branch. Green is
# drawn first and red last, so red-over-green is the fixed visual convention.
PUB_VIEW=np.array([0.083001,-0.991613,-0.099067],dtype=float)
fracs_final=[1/256,1/64,1/16,1/8,1/4,1/2,3/4,1]
final_data=[]
records_final=[]
for frac in fracs_final:
    E=E_STAR*frac
    Pk,_,uk=stereo_curve(E,n=2200,normalize=True)
    xyk,dk=screen_depth(Pk,PUB_VIEW)
    csk=crossings(xyk,dk)
    assert len(csk)==3
    final_data.append((frac,E,uk,xyk,csk))
    records_final.append({
        'E_over_E_star': frac,
        'E': E,
        'u': uk,
        'crossing_count': len(csk),
        'crossings': [
            {
                'segments':[int(c[0]),int(c[1])],
                'segment_parameters':[c[2],c[3]],
                'screen':[float(c[4][0]),float(c[4][1])],
                'depths':[c[5],c[6]],
                'over':'first' if c[5]>c[6] else 'second'
            } for c in csk
        ]
    })

fig,axs=plt.subplots(2,4,figsize=(10.2,4.0))
for ax,(frac,E,uk,xyk,csk) in zip(axs.ravel(),final_data):
    ax.plot(xyk[:,0],xyk[:,1],color='black',linewidth=1.05,zorder=1)
    mn=xyk.min(0); mx=xyk.max(0); span=mx-mn
    segs=straight_crossing_segments(xyk,csk,half_length=.032*max(span))
    # Under first, over last: red-over-green at the crossing is the convention.
    for red,green in segs:
        ax.plot(green[:,0],green[:,1],color='green',linewidth=3.0,
                solid_capstyle='round',zorder=4)
        ax.plot(red[:,0],red[:,1],color='red',linewidth=3.0,
                solid_capstyle='round',zorder=5)
    ax.set_aspect('equal',adjustable='box'); ax.set_axis_off()
    ax.set_xlim(mn[0]-.06*span[0],mx[0]+.06*span[0])
    ax.set_ylim(mn[1]-.06*span[1],mx[1]+.06*span[1])
    if frac==1: title=r'$E/E_*=1$'
    elif frac==3/4: title=r'$E/E_*=3/4$'
    else: title=rf'$E/E_*=1/{round(1/frac)}$'
    ax.set_title(title,fontsize=8.5,pad=1)
handles=[
    Line2D([0,1],[0,0],linestyle='-',color='red',linewidth=3,label='over'),
    Line2D([0,1],[0,0],linestyle='-',color='green',linewidth=3,label='under')]
fig.legend(handles=handles,loc='lower center',ncol=2,frameon=False,fontsize=8,
           bbox_to_anchor=(.5,-.005),handletextpad=.45,columnspacing=1.2)
fig.tight_layout(rect=(0,.045,1,1),pad=.15,w_pad=.25,h_pad=.45)
fig.savefig(os.path.join(HERE,'trefoil_energy_family_view2.pdf'),bbox_inches='tight',pad_inches=.015)
fig.savefig(os.path.join(HERE,'trefoil_energy_family_view2.png'),dpi=280,bbox_inches='tight',pad_inches=.015)
plt.close(fig)

with open(os.path.join(HERE,'crossing_family_view2.json'),'w') as f:
    json.dump({'view':PUB_VIEW.tolist(),'records':records_final},f,indent=2)
