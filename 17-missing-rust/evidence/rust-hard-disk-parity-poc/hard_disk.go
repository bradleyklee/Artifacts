package main

import (
    "fmt"
)

type Rat struct { n, d int64 }
func abs(x int64) int64 { if x < 0 { return -x }; return x }
func gcd(a,b int64) int64 { a=abs(a); b=abs(b); for b!=0 { a,b=b,a%b }; if a==0 { return 1 }; return a }
func R(n,d int64) Rat { if d==0 { panic("zero denominator") }; if d<0 { n=-n; d=-d }; g:=gcd(n,d); return Rat{n/g,d/g} }
func (a Rat) Add(b Rat) Rat { return R(a.n*b.d+b.n*a.d, a.d*b.d) }
func (a Rat) Sub(b Rat) Rat { return R(a.n*b.d-b.n*a.d, a.d*b.d) }
func (a Rat) Mul(b Rat) Rat { return R(a.n*b.n, a.d*b.d) }
func (a Rat) Div(b Rat) Rat { if b.n==0 { panic("division zero") }; return R(a.n*b.d,a.d*b.n) }
func (a Rat) Neg() Rat { return Rat{-a.n,a.d} }
func (a Rat) Cmp(b Rat) int { z:=a.n*b.d-b.n*a.d; if z<0{return -1}; if z>0{return 1};return 0 }
func (a Rat) String() string { if a.d==1{return fmt.Sprintf("%d",a.n)}; return fmt.Sprintf("%d/%d",a.n,a.d) }

type Disk struct { x,v Rat }
type State struct { a,b Disk; time Rat }
const ( 
    FNVOffset uint64 = 14695981039346656037
    FNVPrime uint64 = 1099511628211
)
func fnv(h uint64, s string) uint64 { for i:=0;i<len(s);i++ { h^=uint64(s[i]); h*=FNVPrime }; return h }
func encode(i int, kind string, dt Rat, s State) string { return fmt.Sprintf("%d|%s|%s|%s|%s|%s|%s\n",i,kind,dt.String(),s.time.String(),s.a.x.String(),s.a.v.String(),s.b.x.String()+","+s.b.v.String()) }
func wallTime(d Disk, lo, hi Rat) (Rat,bool) { if d.v.Cmp(R(0,1))>0{return hi.Sub(d.x).Div(d.v),true}; if d.v.Cmp(R(0,1))<0{return lo.Sub(d.x).Div(d.v),true}; return R(0,1),false }
func pairTime(s State, diameter Rat) (Rat,bool) { gap:=s.b.x.Sub(s.a.x).Sub(diameter); rel:=s.a.v.Sub(s.b.v); if rel.Cmp(R(0,1))<=0{return R(0,1),false}; t:=gap.Div(rel); return t,t.Cmp(R(0,1))>0 }
func advance(s *State, dt Rat) { s.a.x=s.a.x.Add(s.a.v.Mul(dt)); s.b.x=s.b.x.Add(s.b.v.Mul(dt)); s.time=s.time.Add(dt) }
func main() {
    // Equal hard disks of radius 1/2 in [0,8] x [0,3], constrained to y=3/2.
    // This is an exact 1D invariant subfamily of hard-disk billiards.
    lo,hi,diameter:=R(1,2),R(15,2),R(1,1)
    s:=State{Disk{R(1,1),R(1,1)},Disk{R(6,1),R(-2,1)},R(0,1)}
    h:=uint64(FNVOffset)
    const N=100000
    for i:=0;i<N;i++ {
        ta,oka:=wallTime(s.a,lo,hi); tb,okb:=wallTime(s.b,lo,hi); tp,okp:=pairTime(s,diameter)
        kind:=""; dt:=R(0,1)
        if okp && (!oka || tp.Cmp(ta)<0) && (!okb || tp.Cmp(tb)<0) { kind="PAIR"; dt=tp
        } else if oka && (!okb || ta.Cmp(tb)<0) { kind="A_WALL"; dt=ta
        } else if okb && (!oka || tb.Cmp(ta)<0) { kind="B_WALL"; dt=tb
        } else { panic("tie or no event") }
        advance(&s,dt)
        switch kind { case "PAIR": s.a.v,s.b.v=s.b.v,s.a.v; case "A_WALL": s.a.v=s.a.v.Neg(); case "B_WALL": s.b.v=s.b.v.Neg() }
        row:=encode(i+1,kind,dt,s); h=fnv(h,row)
        if i<12 { fmt.Print(row) }
    }
    fmt.Printf("SUMMARY events=%d time=%s ax=%s av=%s bx=%s bv=%s fnv64=%016x\n",N,s.time.String(),s.a.x.String(),s.a.v.String(),s.b.x.String(),s.b.v.String(),h)
}
