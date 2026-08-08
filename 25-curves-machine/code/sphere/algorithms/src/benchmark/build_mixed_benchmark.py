#!/usr/bin/env python3
from fractions import Fraction as Q
import json, os, random

ROOT=os.path.dirname(os.path.dirname(__file__))
MODELDIR=os.path.join(ROOT,'models')
os.makedirs(MODELDIR,exist_ok=True)

R2={(2,0):Q(1),(0,2):Q(1)}
C3={(0,3):Q(1),(2,1):Q(-3)}
S3={(1,2):Q(3),(3,0):Q(-1)}
C4={(4,0):Q(1),(2,2):Q(-6),(0,4):Q(1)}
S4={(1,3):Q(4),(3,1):Q(-4)}
R4={(4,0):Q(1),(2,2):Q(2),(0,4):Q(1)}
L3q={(2,1):Q(1),(0,3):Q(1)}
L3p={(3,0):Q(1),(1,2):Q(1)}
Q2R2={(0,4):Q(1),(4,0):Q(-1)}
PQR2={(3,1):Q(2),(1,3):Q(2)}
BASIS={'C3':C3,'S3':S3,'C4':C4,'S4':S4,'R4':R4,'L3q':L3q,'L3p':L3p,'Q2R2':Q2R2,'PQR2':PQR2}

def add(*polys):
    z={}
    for poly in polys:
        for k,v in poly.items():
            z[k]=z.get(k,Q(0))+v
            if not z[k]: del z[k]
    return z

def scale(poly,c): return {k:c*v for k,v in poly.items() if c*v}

def power_linear(a,b,n):
    from math import comb
    return {(i,n-i):Q(comb(n,i))*a**i*b**(n-i) for i in range(n+1)}

def transform(poly,kind):
    swap,sp,sq=kind; z={}
    for (i,j),c in poly.items():
        if not swap:k=(i,j);sg=(sp**i)*(sq**j)
        else:k=(j,i);sg=(sp**i)*(sq**j)
        z[k]=z.get(k,Q(0))+c*sg
    return {k:v for k,v in z.items() if v}
D4=[(sw,sp,sq) for sw in (False,True) for sp in (-1,1) for sq in (-1,1)]
def d4_name(t):
    sw,sp,sq=t
    if not sw:return f'(p,q)->({"" if sp==1 else "-"}p,{"" if sq==1 else "-"}q)'
    return f'(p,q)->({"" if sp==1 else "-"}q,{"" if sq==1 else "-"}p)'
def symmetries(poly): return [d4_name(t) for t in D4 if transform(poly,t)==poly]

def record(name,E,category,notes,seed=None):
    mons={'3':[],'4':[]}
    for (pe,qe),c in sorted(E.items()):
        if pe+qe in (3,4): mons[str(pe+qe)].append([pe,qe,str(c)])
    assert mons['3'] and mons['4']
    rec={
      'example_id':name,'category':category,'notes':notes,'seed':seed,
      'monomials':mons,
      'E_terms':[{'p':pe,'q':qe,'coefficient':str(c)} for (pe,qe),c in sorted(E.items())],
      'signed_coordinate_symmetries':symmetries(E),
      'support_counts':{'cubic':len(mons['3']),'quartic':len(mons['4'])}
    }
    path=os.path.join(MODELDIR,name+'.json')
    with open(path,'w') as f:json.dump(rec,f,indent=2);f.write('\n')
    return {'example_id':name,'category':category,'path':path,'notes':notes,'signed_coordinate_symmetries':rec['signed_coordinate_symmetries'],'support_counts':rec['support_counts']}

index=[]
# 20 dense generic all-coefficient mixtures. Cubic has all 4 and quartic all 5 terms.
for k in range(20):
    rng=random.Random(31000+k)
    cn=[rng.choice([-3,-2,-1,1,2,3]) for _ in range(4)]
    qn=[rng.choice([-3,-2,-1,1,2,3]) for _ in range(5)]
    dc=rng.choice([7,8,9,10,11,12]); dq=rng.choice([8,9,10,11,12,13])
    C={(3-i,i):Q(cn[i],dc) for i in range(4)}
    Q4={(4-i,i):Q(qn[i],dq) for i in range(5)}
    E=add(R2,C,Q4)
    index.append(record(f'dense_generic_{k+1:02d}',E,'dense_generic','all cubic and quartic monomials nonzero',31000+k))

# 6 semi-dense generic mixtures with varied supports, still no intended symmetry.
supports=[
 [(3,0),(2,1),(0,3)],[(3,0),(1,2),(0,3)],[(3,0),(2,1),(1,2)],
 [(2,1),(1,2),(0,3)],[(3,0),(2,1),(0,3)],[(3,0),(1,2),(0,3)]
]
qsupports=[
 [(4,0),(3,1),(2,2),(0,4)],[(4,0),(2,2),(1,3),(0,4)],[(4,0),(3,1),(1,3),(0,4)],
 [(4,0),(3,1),(2,2),(1,3)],[(4,0),(2,2),(1,3),(0,4)],[(4,0),(3,1),(2,2),(0,4)]
]
for k,(cs,qs) in enumerate(zip(supports,qsupports)):
    rng=random.Random(32000+k)
    C={m:Q(rng.choice([-3,-2,-1,1,2,3]),rng.choice([7,9,11])) for m in cs}
    Q4={m:Q(rng.choice([-3,-2,-1,1,2,3]),rng.choice([8,10,12,13])) for m in qs}
    E=add(R2,C,Q4)
    index.append(record(f'semidense_generic_{k+1:02d}',E,'semidense_generic','broad nonsymmetric support control',32000+k))

# 4 aligned / hidden-reflection harmonic controls.
aligned=[
 {'C3':Q(1,5),'C4':Q(1,8)},
 {'C3':Q(2,7),'C4':Q(-1,9),'R4':Q(1,12)},
 {'S3':Q(1,6),'S4':Q(1,10),'R4':Q(1,14)},
 {'C3':Q(1,7),'S3':Q(1,7),'C4':Q(-7,100),'S4':Q(24,100),'R4':Q(1,15)},
]
for k,modes in enumerate(aligned):
    E=dict(R2)
    for lab,c in modes.items(): E=add(E,scale(BASIS[lab],c))
    index.append(record(f'aligned_control_{k+1:02d}',E,'aligned_harmonic','common or intended hidden reflection'))

# 4 chiral / phase-mismatched harmonic controls.
chiral=[
 {'C3':Q(1,5),'S4':Q(1,8),'R4':Q(1,13)},
 {'S3':Q(1,7),'C4':Q(1,9),'R4':Q(-1,14)},
 {'C3':Q(1,6),'S3':Q(1,10),'C4':Q(1,11),'S4':Q(-1,13)},
 {'C3':Q(2,9),'S3':Q(-1,8),'C4':Q(1,12),'S4':Q(1,10),'R4':Q(1,15)},
]
for k,modes in enumerate(chiral):
    E=dict(R2)
    for lab,c in modes.items(): E=add(E,scale(BASIS[lab],c))
    index.append(record(f'chiral_control_{k+1:02d}',E,'chiral_harmonic','phase-mismatched triangle-square mixture'))

# 3 generic cubic plus radial quartic controls.
for k,cn in enumerate([(1,2,-1,1),(2,-1,3,-2),(-1,3,2,1)]):
    C={(3-i,i):Q(cn[i],9+k) for i in range(4)}
    E=add(R2,C,scale(R4,Q(k+1,13+2*k)))
    index.append(record(f'cubic_radial_{k+1:02d}',E,'cubic_plus_radial','dense cubic plus radial quartic'))

# 3 one-coordinate mechanical families under rational rotations.
rots=[(Q(1),Q(1)),(Q(2),Q(1)),(Q(3),Q(2))]
for k,(a,b) in enumerate(rots):
    L3=power_linear(a,b,3); L4=power_linear(a,b,4)
    E=add(R2,scale(L3,Q(1,5*(a*a+b*b))),scale(L4,Q((-1)**k,7*(a*a+b*b)**2)))
    index.append(record(f'mechanical_rotated_{k+1:02d}',E,'mechanical_rotated','cubic and quartic depend on one rational linear coordinate'))

# 3 separable and near-separable controls.
sep_specs=[
 ({(3,0):Q(1,7),(0,3):Q(1,9)},{(4,0):Q(1,11),(0,4):Q(-1,13)},'separable'),
 ({(3,0):Q(1,8),(0,3):Q(-2,9)},{(4,0):Q(2,11),(0,4):Q(1,12)},'separable'),
 ({(3,0):Q(1,7),(0,3):Q(1,9),(2,1):Q(1,10)},{(4,0):Q(1,11),(0,4):Q(1,13),(2,2):Q(-1,12)},'near-separable')
]
for k,(C,Q4,label) in enumerate(sep_specs):
    index.append(record(f'{label}_control_{k+1:02d}',add(R2,C,Q4),label,'two-coordinate nonlinear control'))

with open(os.path.join(ROOT,'candidate_index.json'),'w') as f:json.dump(index,f,indent=2);f.write('\n')
print('wrote',len(index),'models')
