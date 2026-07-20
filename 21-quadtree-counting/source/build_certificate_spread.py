#!/usr/bin/env python3
"""Build the code-only A120593 certificate spread in the approved zine style.

No raster or generative imagery is used.  Quadtrees, typography, rules, and
layout are emitted as SVG.  A spatial registry rejects overlaps before export.
The full JSON certificate is embedded in the final PDF but never painted.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from pathlib import Path
from io import BytesIO
import hashlib, html, json, os, re
os.environ.setdefault('MPLCONFIGDIR','/tmp/matplotlib-quadtree-certificate')
import fitz
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties
from matplotlib.mathtext import math_to_image
from matplotlib.textpath import TextToPath
rcParams['mathtext.fontset']='stix'
rcParams['mathtext.default']='it'

HERE = Path(__file__).resolve().parent
PAGE = HERE.parent
REPO = PAGE.parents[1]
STYLE = json.loads((REPO/'pages/_common_zine_style/data/interior_prose_page_style.json').read_text())
DATA_PATH = PAGE/'data/certificate.json'
DATA = json.loads(DATA_PATH.read_text())
OUT = PAGE/'output'; OUT.mkdir(parents=True, exist_ok=True)
W,H = 675,900; ML,MR = 42,42
PAPER='#fbfaf7'; INK='#211f1b'; QUIET='#615b52'; RULE='#49453e'; GRAY='#c9c5bd'
LEAF=()
TEXT_PATH=TextToPath()
SVG_FONT_SCALE=1.0
WRAP_METRIC_SCALE=.75  # CairoSVG renders these font advances at 3/4 TextPath units.
RENDERED_MATH=[]

@dataclass(frozen=True)
class Box:
    name:str; x:float; y:float; w:float; h:float
    @property
    def x2(self): return self.x+self.w
    @property
    def y2(self): return self.y+self.h

class SpatialRegistry:
    """Page-space manager: bounds, square invariants, and collision rejection."""
    def __init__(self,page:int): self.page=page; self.boxes=[]
    def add(self,name,x,y,w,h,*,square=False,overlap_with=()):
        b=Box(name,x,y,w,h)
        assert x>=ML and b.x2<=W-MR and y>=43 and b.y2<=851, f'{name}: outside live area'
        if square: assert abs(w-h)<1e-9, f'{name}: non-square viewport {w}x{h}'
        for a in self.boxes:
            ix=min(a.x2,b.x2)-max(a.x,b.x); iy=min(a.y2,b.y2)-max(a.y,b.y)
            if ix>0 and iy>0 and a.name not in overlap_with:
                raise RuntimeError(f'page {self.page} collision: {a.name} x {b.name} ({ix:.2f}x{iy:.2f})')
        self.boxes.append(b); return b
    def audit(self):
        return {'page':self.page,'boxes':[b.__dict__ for b in self.boxes],
                'collisions':0,'square_viewports':sum('tree' in b.name for b in self.boxes)}

def esc(s): return html.escape(str(s))
def text(x,y,s,size=14,cls='body',anchor='start',weight=None,style=None,tracking=None):
    colors={'body':INK,'quiet':QUIET,'mono':INK,'header':'#24211e','title':'#111'}
    families={'body':'DejaVu Serif','quiet':'DejaVu Serif','mono':'DejaVu Sans Mono',
              'header':'DejaVu Serif','title':'DejaVu Serif'}
    extra=f' fill="{colors.get(cls,INK)}" font-family="{families.get(cls,"DejaVu Serif")}"'
    if weight: extra+=f' font-weight="{weight}"'
    if style: extra+=f' font-style="{style}"'
    if tracking is not None: extra+=f' letter-spacing="{tracking}"'
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" text-anchor="{anchor}"{extra}>{esc(s)}</text>'

def justified_text(x,y,s,width,size=14,cls='body'):
    """Justify by positioning measured words; PDF renderers may ignore textLength."""
    words=s.split(); prop=FontProperties(family='DejaVu Serif',size=size)
    advances=[SVG_FONT_SCALE*TEXT_PATH.get_text_width_height_descent(w,prop,False)[0] for w in words]
    if len(words)<2:return text(x,y,s,size,cls)
    gap=(width-sum(advances))/(len(words)-1)
    assert gap>=0, f'justified line exceeds measure: {s}'
    out=['<g>']; xx=x
    for word,advance in zip(words,advances):
        out.append(text(xx,y,word,size,cls)); xx+=advance+gap
    out.append('</g>'); return ''.join(out)

def paragraph_svg(x,y,s,width,size=10,leading=14,cls='body'):
    """Greedy measured reflow; justify every line except the paragraph ending."""
    prop=FontProperties(family='DejaVu Serif',size=size)
    target=.95*width
    space=WRAP_METRIC_SCALE*TEXT_PATH.get_text_width_height_descent(' ',prop,False)[0]
    words=s.split(); lines=[]; current=[]; used=0
    for word in words:
        advance=WRAP_METRIC_SCALE*TEXT_PATH.get_text_width_height_descent(word,prop,False)[0]
        trial=used+(space if current else 0)+advance
        if current and trial>target:
            lines.append(' '.join(current)); current=[word]; used=advance
        else:
            current.append(word); used=trial
    if current:lines.append(' '.join(current))
    return ''.join(text(x,y+i*leading,line,size,cls) for i,line in enumerate(lines))

_math_serial=0
def math_svg(expr,x,y,size=14,anchor='start'):
    """Inline Matplotlib mathtext SVG as paths, preserving vector output."""
    global _math_serial; _math_serial+=1; RENDERED_MATH.append(expr)
    b=BytesIO(); math_to_image(f'${expr}$',b,format='svg',dpi=100,
        prop=FontProperties(family='DejaVu Serif',size=size),color=INK)
    raw=b.getvalue().decode()
    root=re.search(r'<svg[^>]*width="([0-9.]+)pt" height="([0-9.]+)pt"[^>]*viewBox="([^"]+)"[^>]*>',raw)
    if not root: raise RuntimeError('cannot parse math SVG')
    width,height=float(root.group(1)),float(root.group(2)); view=root.group(3)
    inner=raw[root.end():raw.rfind('</svg>')]
    # math_to_image includes a white figure patch; remove it so formulas sit
    # transparently on the zine paper rather than in visible white boxes.
    inner=re.sub(r'<g id="patch_1">.*?</g>','',inner,flags=re.S)
    # Glyph IDs repeat between formulas; namespace each nested fragment.
    ids=set(re.findall(r'id="([^"]+)"',inner)); prefix=f'm{_math_serial}_'
    for old in sorted(ids,key=len,reverse=True):
        inner=inner.replace(f'id="{old}"',f'id="{prefix}{old}"')
        inner=inner.replace(f'#{old}',f'#{prefix}{old}')
    xx=x-width/2 if anchor=='middle' else x-width if anchor=='end' else x
    return (f'<g transform="translate({xx:.2f},{y:.2f})">'
            f'<svg x="0" y="0" width="{width:.2f}" height="{height:.2f}" '
            f'viewBox="{view}" overflow="visible">{inner}</svg></g>')

def base(meta):
    return [f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="506.25pt" height="675pt" viewBox="0 0 {W} {H}">
<style>
.paper{{fill:{PAPER}}}.rule{{stroke:{RULE};stroke-width:.9}}.soft{{stroke:#827c72;stroke-width:.55}}
.header{{font-family:"DejaVu Serif";fill:#24211e}}.title{{font-family:"DejaVu Serif";fill:#111}}
.body{{font-family:"DejaVu Serif";fill:{INK}}}.quiet{{font-family:"DejaVu Serif";fill:{QUIET}}}
.mono{{font-family:"DejaVu Sans Mono";fill:{INK}}}.grid{{stroke:#111;stroke-width:1;fill:none}}
</style>''',f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
    text(ML,30,meta['publication'],12,'header',tracking=2),
    text(W-MR,30,meta['running'],9.6,'quiet','end',style='italic'),
    f'<line x1="{ML}" y1="42" x2="{W-MR}" y2="42" stroke="{RULE}" stroke-width=".9"/>',
    text(ML,92,meta['title'],39,'title'), text(ML,119,meta['subtitle'],15,'quiet',style='italic')]

def footer(meta):
    return [f'<line x1="{ML}" y1="850" x2="{W-MR}" y2="850" stroke="{RULE}" stroke-width=".9"/>',
            f'<line x1="{ML}" y1="853.5" x2="{W-MR}" y2="853.5" stroke="#827c72" stroke-width=".55"/>',
            text(W/2,889,str(meta['page']),31,'title','middle'),
            '</svg>']

# Ordered reduced quadrant trees and their global D4 action.
XY=((-1,1),(1,1),(-1,-1),(1,-1))
CCW=(0,2,3,1)  # NW, SW, SE, NE.
def d4_maps():
    maps=[]
    for refl in (False,True):
      for turns in range(4):
        p=[]
        for x,y in XY:
          if refl:x=-x
          for _ in range(turns):x,y=-y,x
          p.append(XY.index((x,y)))
        if tuple(p) not in maps:maps.append(tuple(p))
    assert len(maps)==8; return maps
D4=d4_maps()
def leaves(t):return 1 if t==LEAF else sum(leaves(c) for c in t if c is not None)
@lru_cache(None)
def trees(n):
    if n==1:return (LEAF,)
    choices=[None]+[t for m in range(1,n) for t in trees(m)]; out=set()
    for ch in product(choices,repeat=4):
        occ=[c for c in ch if c is not None]
        if 2<=len(occ)<=4 and sum(map(leaves,occ))==n:out.add(ch)
    return tuple(sorted(out,key=repr))
def transform(t,p):
    if t==LEAF:return LEAF
    out=[None]*4
    for old,c in enumerate(t):
        if c is not None:out[p[old]]=transform(c,p)
    return tuple(out)
def canon(t):return min((transform(t,p) for p in D4),key=repr)
def inventory(t):
    if t==LEAF:return (0,0,0)
    a=[0,0,0]; a[sum(c is not None for c in t)-2]+=1
    for c in t:
        if c is not None:
            z=inventory(c); a=[a[i]+z[i] for i in range(3)]
    return tuple(a)
def ccw_key(t):
    if t==LEAF:return '1'
    return '2(' + ''.join('0' if t[p] is None else ccw_key(t[p]) for p in CCW) + ')'
def reps(n):
    g={}
    for t in trees(n):g.setdefault(canon(t),set()).add(t)
    return sorted(((k,len(v)) for k,v in g.items()),key=lambda z:(inventory(z[0]),ccw_key(z[0])))

def tree_svg(t,x,y,s):
    """A recursively subdivided square; x/y/s are native page units."""
    out=[f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="white" stroke="#111" stroke-width="1"/>']
    if t==LEAF:
        out.append(f'<rect x="{x+1.5}" y="{y+1.5}" width="{s-3}" height="{s-3}" fill="{GRAY}"/>'); return out
    out += [f'<line x1="{x+s/2}" y1="{y}" x2="{x+s/2}" y2="{y+s}" class="grid"/>',
            f'<line x1="{x}" y1="{y+s/2}" x2="{x+s}" y2="{y+s/2}" class="grid"/>']
    slots=((x,y),(x+s/2,y),(x,y+s/2),(x+s/2,y+s/2))
    for c,(xx,yy) in zip(t,slots):
        if c is not None:out += tree_svg(c,xx,yy,s/2)
    return out

def abstract_tree_svg(t,x,y,w,h):
    """Draw the rooted plane tree obtained after forgetting empty quadrants."""
    children=lambda z: [] if z==LEAF else [c for c in z if c is not None]
    def depth(z):
        cc=children(z); return 0 if not cc else 1+max(map(depth,cc))
    maxd=depth(t); leaf_serial=0; nodes=[]; edges=[]
    def place(z,d):
        nonlocal leaf_serial
        cc=children(z)
        if not cc:
            xx=x+w/2 if leaves(t)==1 else x+3+(w-6)*leaf_serial/(leaves(t)-1)
            leaf_serial+=1
        else:
            child_pos=[place(c,d+1) for c in cc]; xx=sum(p[0] for p in child_pos)/len(child_pos)
            for p in child_pos: edges.append(((xx,d),p))
        p=(xx,d); nodes.append(p); return p
    place(t,0)
    def py(d): return y+h/2 if maxd==0 else y+4+(h-8)*d/maxd
    out=[]
    for (a,d1),(b,d2) in edges:
        out.append(f'<line x1="{a:.2f}" y1="{py(d1):.2f}" x2="{b:.2f}" y2="{py(d2):.2f}" stroke="#211f1b" stroke-width="1"/>')
    for xx,d in nodes:
        out.append(f'<circle cx="{xx:.2f}" cy="{py(d):.2f}" r="2.15" fill="#211f1b"/>')
    return out

def tree_code(t):
    """Four-slot code in counterclockwise order: NW, SW, SE, NE."""
    if t==LEAF:return '▪'
    return '⟨'+','.join('□' if t[p] is None else tree_code(t[p]) for p in CCW)+'⟩'

def page_one():
    reg=SpatialRegistry(1); s=base({'publication':'ZINE OF ZANY SAGES','running':'Mathematical Separator',
      'title':'Counting the quadrant trees','subtitle':'A combinatorial derivation'})
    # n=1 and n=2 band
    reg.add('small-atlas',42,145,591,108)
    s += [math_svg(r'a(1)=1',181,148,13,'middle'),
          math_svg(r'a(2)=6',488,148,13,'middle')]
    small=[(reps(1)[0],157),(reps(2)[0],406),(reps(2)[1],522)]
    for idx,((t,orb),x) in enumerate(small):
        reg.add(f'tree-small-{idx}',x,171,48,48,square=True,overlap_with=('small-atlas',))
        reg.add(f'tree-code-small-{idx}',x-18,222,84,14,overlap_with=('small-atlas',))
        s+=tree_svg(t,x,171,48)+[text(x+24,231,tree_code(t),8.3,'mono','middle'),text(x+24,247,f'×{orb}',10.2,'quiet','middle')]
    s.append('<line x1="42" y1="260" x2="633" y2="260" stroke="#827c72" stroke-width=".55"/>')
    # n=3 atlas, 6 + 5 exact square viewports
    reg.add('n3-heading',42,268,591,25); s.append(math_svg(r'a(3)=76',W/2,270,14,'middle'))
    rr=reps(3); positions=[]
    for row,count in enumerate((6,5)):
        gap=31 if count==6 else 45; total=count*62+(count-1)*gap; start=(W-total)/2
        for col in range(count):positions.append((start+col*(62+gap),304+row*100))
    for idx,((t,orb),(x,y)) in enumerate(zip(rr,positions)):
        reg.add(f'tree-n3-{idx}',x,y,58,58,square=True); i,j,k=inventory(t)
        reg.add(f'tree-code-n3-{idx}',x-14,y+62,86,13)
        s+=tree_svg(t,x,y,58)+[text(x+29,y+72,tree_code(t),6.9,'mono','middle'),
                              text(x+29,y+88,f'×{orb}',8.7,'body','middle')]
    reg.add('orbit-audit',42,502,591,34)
    sizes=[o for _,o in rr]
    s += [text(42,520,'ORBIT AUDIT',9.5,'quiet',weight='bold',tracking=1),
          text(151,520,' + '.join(map(str,sizes))+' = 76',11.2,'mono')]
    reg.add('orbit-caption',42,536,591,24)
    s.append(text(42,553,'D₄ representatives; multipliers recover placements. Codes run CCW: NW → SW → SE → NE.',9.7,'quiet'))
    s.append(f'<line x1="42" y1="567" x2="633" y2="567" stroke="{RULE}" stroke-width=".9"/>')
    # Counting derivation by preorder words, with a worked n=3 audit.
    reg.add('counting-proof',42,578,591,260)
    reg.add('proof-left',42,586,287,180,overlap_with=('counting-proof',))
    reg.add('proof-right',345,586,288,180,overlap_with=('counting-proof',))
    reg.add('proof-closed-form',42,774,591,63,overlap_with=('counting-proof',))
    s += [f'<line x1="337" y1="587" x2="337" y2="767" stroke="#aaa398" stroke-width=".6"/>',
          paragraph_svg(42,598,'A quadtree square needs to be split into quadrants, possibly recursively, if it contains two or more points. Apply this procedure recursively to obtain a perfect quaternary tree pointing to n points on n true leafs. Forget those branches not ending at a true leaf point.',287,8.5,14),
          paragraph_svg(42,666,'Now let i, j, k count nodes with 2, 3, or 4 valence only, and distinguish branch-like (bₓ) from true leafs (l₀). Each branch introduces a differential toward leaf count:',287,8.5,14),
          math_svg(r'b_x:X\longmapsto X\prime=X+x-1',185.5,702,10.2,'middle'),
          paragraph_svg(42,729,'Summing over all branch nodes, starting from one root and ending in n true leafs we obtain that:',287,8.5,14),
          math_svg(r'1+i+2j+3k-n=0',185.5,741,10.7,'middle'),
          paragraph_svg(345,598,'The total number of nodes including the root and true leafs will be m=i+j+k+n. The raw multinomial ordering of these symbols is:',288,8.5,14),
          math_svg(r'\binom{m}{n,i,j,k}\;=\;\frac{m!}{n!\,i!\,j!\,k!}',489,620,12.2,'middle'),
          paragraph_svg(345,658,'For each sequencing of bₓ and l₀ symbols there is exactly one cyclic rotation whose partial sums are non-zero until all leafs are consumed, so we divide the multinomial by m.',288,8.35,14),
          paragraph_svg(345,708,'The b₂ and b₃ branchings are associated to 6 and 4 distinct realizations in space, so we multiply by 6ⁱ and 4ʲ to obtain the final closed-form summand:',288,8.35,14),
          math_svg(r'\frac{(n+i+j+k-1)!}{n!\,i!\,j!\,k!}\,6^i4^j',489,742,9.7,'middle'),
          f'<line x1="42" y1="772" x2="633" y2="772" stroke="#aaa398" stroke-width=".6"/>',
          text(42,787,'The sum is taken over all non-negative indices subject to the zero-sum constraint:',8.7),
          math_svg(r'a(n)=\sum\frac{(n+i+j+k-1)!}{n!\,i!\,j!\,k!}\,6^i4^j,\qquad \mathrm{where}\quad i,j,k\geq0,\quad 1+i+2j+3k-n=0\,.',W/2,802,13.2,'middle')]
    s+=footer({'page':'?'})
    return ''.join(s),reg.audit()

def page_two():
    reg=SpatialRegistry(2); s=base({'publication':'ZINE OF ZANY SAGES','running':'Congrats, Hadrien Brochet',
      'title':'The witness certificate','subtitle':'Just the integral-differential facts'})
    reg.add('integral',42,138,591,240)
    s += [text(42,151,'INTEGRAL FORM',10,'quiet',weight='bold',tracking=1),
          math_svg(r'D(u)=1-6u-4u^2-u^3,\qquad H_n(u)=\frac{1}{n u^nD(u)^n},\qquad q_n=\frac{1}{2\pi i}\oint H_n(u)\,du',42,164,13.0),
          text(42,198,'Put B(u)=6u+4u²+u³, so D(u)=1−B(u). Expanding (1−B)⁻ⁿ and then Bᵐ gives the Laurent series',9.2,'quiet'),
          math_svg(r'q_n=\frac{1}{2\pi i}\oint\frac{1}{n}\sum\sum\binom{n+m-1}{m}\binom{m}{i,j,k}6^i4^j u^{i+2j+3k-n}\,du,\quad\mathrm{where}\quad m,i,j,k\geq0,\ i+j+k=m.',42,222,10.8),
          text(42,260,'A normalized contour integral around u=0 keeps exactly the u⁻¹ term:',9.2,'quiet'),
          math_svg(r'\frac{1}{2\pi i}\oint u^r\,du=1\ \ (r=-1),\qquad 0\ \ (r\neq-1).',42,274,11.2),
          text(42,303,'Thus the exponent condition moves underneath the sum:',9.2,'quiet'),
          math_svg(r'i+2j+3k-n=-1\quad\Longleftrightarrow\quad 1+i+2j+3k-n=0,',42,318,11.4),
          math_svg(r'q_n=\frac{1}{n}\sum\binom{n+m-1}{m}\binom{m}{i,j,k}6^i4^j,\quad\mathrm{where}\quad m,i,j,k\geq0,\ i+j+k=m,\ 1+i+2j+3k-n=0.',42,346,10.4),
          math_svg(r'\frac{1}{n}\binom{n+m-1}{m}\binom{m}{i,j,k}=\frac{(n+i+j+k-1)!}{n!\,i!\,j!\,k!}\quad\Longrightarrow\quad q_n=a(n).',42,370,9.8)]
    reg.add('identity',42,398,591,40)
    s += [text(42,410,'EXACT VERIFICATION IDENTITY',10.5,'quiet',weight='bold',tracking=1),
          math_svg(r'\sum_{r=0}^{3}P_r(n)H_{n+r}(u)=\frac{d}{du}\left(R(n,u)H_n(u)\right)',42,420,9.8)]
    reg.add('certificate-columns',42,444,591,210)
    reg.add('rational',42,444,328,210,overlap_with=('certificate-columns',))
    reg.add('recurrence',418,444,215,210,overlap_with=('certificate-columns',))
    s += [f'<line x1="382" y1="448" x2="382" y2="656" stroke="#aaa398" stroke-width=".7"/>',
          text(42,458,'RATIONAL CERTIFICATE',10.5,'quiet',weight='bold',tracking=1),
          math_svg(r'R(n,u)=\frac{N(n,u)}{u^2(u^3+4u^2+6u-1)^2}',42,473,14.0),
          math_svg(r'N(n,u)=n^2(64u^9+576u^8+2304u^7+4496u^6',42,512,11.6),
          math_svg(r'+2784u^5-5136u^4-8524u^3+204u^2+6396u-491)',58,533,11.6),
          math_svg(r'+n(112u^9+1008u^8+4032u^7+7988u^6',42,554,11.6),
          math_svg(r'+5784u^5-6228u^4-11872u^3-948u^2+6648u-491)',58,575,11.6),
          math_svg(r'+40u^9+360u^8+1440u^7+2960u^6',42,596,11.6),
          math_svg(r'+2960u^5+640u^4-440u^3+40u^2.',58,617,11.6),
          text(418,458,'RECURRENCE OPERATOR',10.0,'quiet',weight='bold',tracking=.7),
          math_svg(r'\sum_{r=0}^{3}P_r(n)q_{n+r}=0',418,473,13.5),
          math_svg(r'q_0,\ldots,q_5=1,1,6,76,1201,21252',418,522,9.2),
          text(418,548,'n=0 is checked directly.',9.3,'quiet'),
          math_svg(r'P_0=-8(4n+5)(2n+1)(4n-1)',418,572,9.6),
          math_svg(r'P_1=-64(n+1)(48n^2+96n+43)',418,599,9.6),
          math_svg(r'P_2=-6144(2n+3)(n+2)(n+1)',418,626,9.6),
          math_svg(r'P_3=491(n+3)(n+2)(n+1)',418,653,9.6)]
    reg.add('differential',42,666,591,94)
    s += [text(42,680,'ALGEBRAIC & DIFFERENTIAL OPERATORS',10.5,'quiet',weight='bold',tracking=1),
          '<text x="278" y="680" font-size="8.2" fill="#3c5870" font-family="DejaVu Serif">(from OEIS A120593)</text>',
          math_svg(r'5A(x)=4+x+A(x)^4\quad\Longleftrightarrow\quad Q=A-1,\quad Q=\frac{x}{D(Q)}',42,696,12.8),
          math_svg(r'(256x^3+3072x^2+12288x-491)A^{(3)}+(1152x^2+9216x+18432)A^{(2)}',42,724,12.5),
          math_svg(r'+(688x+2752)A^{(1)}-40A=0',58,749,12.5)]
    reg.add('reference',42,772,591,66)
    s += [text(42,786,'REFERENCE',9.2,'quiet',weight='bold',tracking=.7),
          text(42,807,'H. Brochet and B. Salvy, “Reduction-Based Creative Telescoping for Definite Summation of D-finite Functions,”',8.6,'quiet'),
          '<text x="42" y="834" font-size="9.2" fill="#3c5870" font-family="DejaVu Serif">https://arxiv.org/abs/2307.07216</text>']
    s+=footer({'page':'?+1'})
    return ''.join(s),reg.audit()

def svg_to_pdf(svg_text,path):
    doc=fitz.open(stream=svg_text.encode(),filetype='svg'); raw=doc.convert_to_pdf(); doc.close()
    pdf=fitz.open('pdf',raw); pdf.save(path,garbage=4,deflate=True); pdf.close()

def audit_payload_matches_print():
    """Reject any ordered machine datum that diverges from the printed spread."""
    assert DATA['sequence']=='A120593'
    assert DATA['initial_values']==[1,1,6,76,1201,21252]
    assert DATA['lagrange_certificate_setup']=={
        'D':'1-6*u-4*u^2-u^3',
        'H':'H[n](u)=1/(n*u^n*D(u)^n)',
        'coefficient_integral':'q[n]=(1/(2*pi*i))*contour_integral H[n](u) du'}
    assert DATA['generating_function']['algebraic_equation']=='A^4-5*A+4+x=0'
    assert DATA['multinomial_sum']['formula']=='q[n]=sum_{i,j,k>=0, i+2*j+3*k=n-1} (n+i+j+k-1)!*6^i*4^j/(n!*i!*j!*k!)'
    assert DATA['recurrence']['P']==[
        '-8*(4*n+5)*(2*n+1)*(4*n-1)',
        '-64*(n+1)*(48*n^2+96*n+43)',
        '-6144*(2*n+3)*(n+2)*(n+1)',
        '491*(n+3)*(n+2)*(n+1)']
    assert DATA['rational_certificate']['N_by_n_degree']=={
        '2':[-491,6396,204,-8524,-5136,2784,4496,2304,576,64],
        '1':[-491,6648,-948,-11872,-6228,5784,7988,4032,1008,112],
        '0':[0,0,40,-440,640,2960,2960,1440,360,40]}
    assert DATA['symmetry_audit']['oriented_counts_n_1_to_3']==[1,6,76]
    assert DATA['symmetry_audit']['orbits_n_1_to_3']==[1,2,11]
    assert DATA['symmetry_audit']['n3_orbit_sizes']==[o for _,o in reps(3)]
    assert DATA['symmetry_audit']['tree_representatives']=={
        str(n):[{'code':tree_code(t),'orbit_size':o,'inventory':list(inventory(t))}
                for t,o in reps(n)] for n in (1,2,3)}

def audit_rendered_math():
    """Every math path rendered on the human surface must originate in JSON."""
    expected=[item['latex'] for page in ('page_1','page_2')
              for item in DATA['surface_math'][page]]
    assert RENDERED_MATH==expected, {
        'rendered_count':len(RENDERED_MATH),'payload_count':len(expected),
        'first_difference':next(((i,a,b) for i,(a,b) in
                                 enumerate(zip(RENDERED_MATH,expected)) if a!=b),None)}

def postflight_pdf(path):
    """Audit realized glyph boxes after SVG conversion, not only planned regions."""
    doc=fitz.open(path); page=doc[0]; words=page.get_text('words')
    assert abs(page.rect.width-506.25)<.02 and abs(page.rect.height-675)<.02
    # A print page must contain no raster image XObjects. SVG paths and embedded
    # font glyphs remain resolution-independent at every output scale.
    assert len(page.get_images(full=True)) == 0, 'raster image found in vector print page'
    collisions=[]
    for i,a in enumerate(words):
        ra=fitz.Rect(a[:4])
        assert ra.x0>=-.1 and ra.y0>=-.1 and ra.x1<=page.rect.width+.1 and ra.y1<=page.rect.height+.1
        for b in words[i+1:]:
            # Text on the same source line may touch through kerning; require a
            # meaningful two-dimensional overlap before reporting collision.
            rb=fitz.Rect(b[:4]); inter=ra & rb
            if not inter.is_empty and inter.width>.6 and inter.height>.6:
                collisions.append((a[4],b[4],list(inter)))
    doc.close()
    if collisions: raise RuntimeError(f'post-render text collisions: {collisions[:5]}')
    return {'words':len(words),'text_collisions':0,'raster_images':0,
            'vector_only':True,'page_points':[506.25,675]}

def build():
    RENDERED_MATH.clear()
    assert [len(trees(n)) for n in (1,2,3)]==[1,6,76]
    assert [len(reps(n)) for n in (1,2,3)]==[1,2,11]
    audit_payload_matches_print()
    svgs=[]; audits=[]
    for num,fn in ((1,page_one),(2,page_two)):
        svg,audit=fn(); svgs.append(svg); audits.append(audit)
        (OUT/f'quadtree_certificate_page{num}.svg').write_text(svg)
        svg_to_pdf(svg,OUT/f'quadtree_certificate_page{num}.pdf')
        audits[-1]['postflight']=postflight_pdf(OUT/f'quadtree_certificate_page{num}.pdf')
        d=fitz.open(OUT/f'quadtree_certificate_page{num}.pdf'); p=d[0]
        pix=p.get_pixmap(matrix=fitz.Matrix(1350/506.25,1800/675),alpha=False)
        pix.save(OUT/f'quadtree_certificate_page{num}.png'); d.close()
    audit_rendered_math()
    # Merge, embed the exact JSON as a machine-only associated file, add checksum metadata.
    writer=PdfWriter()
    for num in (1,2):
        reader=PdfReader(OUT/f'quadtree_certificate_page{num}.pdf')
        writer.add_page(reader.pages[0])
    # SVG hyperlinks are not consistently retained by every converter. Add a
    # native PDF URI annotation over the two-line Brochet-Salvy citation.
    writer.add_uri(1,'https://oeis.org/A120593',
                   RectangleObject((208.5,159.0,317.5,173.0)),border=[0,0,0])
    writer.add_uri(1,'https://arxiv.org/abs/2307.07216',
                   RectangleObject((31.5,43.0,187.0,57.0)),border=[0,0,0])
    payload=DATA_PATH.read_bytes(); sha=hashlib.sha256(payload).hexdigest()
    writer.add_attachment('a120593_certificate.json',payload)
    writer.add_metadata({'/Title':'A120593 quadtree and rational certificate',
                         '/Subject':'Code-generated Zine of Zany Sages proof spread',
                         '/A120593CertificateSHA256':sha,
                         '/LayoutAudit':'zero collisions; all quadtree viewports square'})
    final=OUT/'a120593_quadtree_certificate_zine_spread.pdf'
    with final.open('wb') as f:writer.write(f)
    # Letter-size printer proof, using the repository's authoritative placement.
    natural=fitz.open(final); proof=fitz.open()
    for i in range(len(natural)):
        pp=proof.new_page(width=612,height=792)
        pp.show_pdf_page(fitz.Rect(52.875,58.5,559.125,733.5),natural,i,keep_proportion=False)
        if i==1:
            pp.insert_link({'kind':fitz.LINK_URI,
                            'from':fitz.Rect(261.375,565.0,370.375,582.0),
                            'uri':'https://oeis.org/A120593'})
            pp.insert_link({'kind':fitz.LINK_URI,
                            'from':fitz.Rect(84.375,681.0,239.875,698.0),
                            'uri':'https://arxiv.org/abs/2307.07216'})
    proof.save(OUT/'a120593_quadtree_certificate_zine_spread_printerproof.pdf',garbage=4,deflate=True)
    proof.close(); natural.close()
    audit={'status':'PASS','pages':audits,'embedded_payload':'a120593_certificate.json',
           'payload_sha256':sha,'oriented_counts':[1,6,76],'d4_orbits':[1,2,11]}
    (OUT/'layout_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit,indent=2)); print(final)

if __name__=='__main__':build()
