use std::fmt;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct Rat { n: i128, d: i128 }
impl Rat {
    fn new(mut n:i128, mut d:i128)->Self { assert!(d!=0); if d<0 {n=-n;d=-d}; let g=gcd(n,d); Self{n:n/g,d:d/g} }
    fn add(self,b:Self)->Self { Self::new(self.n*b.d+b.n*self.d,self.d*b.d) }
    fn sub(self,b:Self)->Self { Self::new(self.n*b.d-b.n*self.d,self.d*b.d) }
    fn mul(self,b:Self)->Self { Self::new(self.n*b.n,self.d*b.d) }
    fn div(self,b:Self)->Self { assert!(b.n!=0); Self::new(self.n*b.d,self.d*b.n) }
    fn neg(self)->Self { Self{n:-self.n,d:self.d} }
    fn cmp(self,b:Self)->i8 { let z=self.n*b.d-b.n*self.d; if z<0{-1}else if z>0{1}else{0} }
}
fn gcd(mut a:i128,mut b:i128)->i128 { a=a.abs(); b=b.abs(); while b!=0 { let t=a%b;a=b;b=t }; if a==0{1}else{a} }
impl fmt::Display for Rat { fn fmt(&self,f:&mut fmt::Formatter<'_>)->fmt::Result { if self.d==1 {write!(f,"{}",self.n)} else {write!(f,"{}/{}",self.n,self.d)} } }
#[derive(Clone,Copy)] struct Disk { x:Rat, v:Rat }
#[derive(Clone,Copy)] struct State { a:Disk, b:Disk, time:Rat }
const FNV_OFFSET:u64=14695981039346656037; const FNV_PRIME:u64=1099511628211;
fn fnv(mut h:u64,s:&str)->u64 { for b in s.bytes(){h^=b as u64;h=h.wrapping_mul(FNV_PRIME);}h }
fn wall_time(d:Disk,lo:Rat,hi:Rat)->Option<Rat>{ if d.v.cmp(Rat::new(0,1))>0 {Some(hi.sub(d.x).div(d.v))} else if d.v.cmp(Rat::new(0,1))<0 {Some(lo.sub(d.x).div(d.v))} else {None} }
fn pair_time(s:State,diameter:Rat)->Option<Rat>{ let gap=s.b.x.sub(s.a.x).sub(diameter); let rel=s.a.v.sub(s.b.v); if rel.cmp(Rat::new(0,1))<=0{return None}; let t=gap.div(rel); if t.cmp(Rat::new(0,1))>0{Some(t)}else{None} }
fn advance(s:&mut State,dt:Rat){s.a.x=s.a.x.add(s.a.v.mul(dt));s.b.x=s.b.x.add(s.b.v.mul(dt));s.time=s.time.add(dt);}
fn main(){
    // Equal hard disks of radius 1/2 in [0,8] x [0,3], constrained to y=3/2.
    // Exact 1D invariant subfamily of hard-disk billiards.
    let (lo,hi,diameter)=(Rat::new(1,2),Rat::new(15,2),Rat::new(1,1));
    let mut s=State{a:Disk{x:Rat::new(1,1),v:Rat::new(1,1)},b:Disk{x:Rat::new(6,1),v:Rat::new(-2,1)},time:Rat::new(0,1)};
    let mut h=FNV_OFFSET;
    const N:usize=100000;
    for i in 0..N {
        let ta=wall_time(s.a,lo,hi); let tb=wall_time(s.b,lo,hi); let tp=pair_time(s,diameter);
        let (kind,dt)=match (tp,ta,tb) {
            (Some(p),a,b) if a.map_or(true,|x|p.cmp(x)<0) && b.map_or(true,|x|p.cmp(x)<0) => ("PAIR",p),
            (_,Some(a),b) if b.map_or(true,|x|a.cmp(x)<0) => ("A_WALL",a),
            (_,_,Some(b)) => ("B_WALL",b),
            _ => panic!("tie or no event"),
        };
        advance(&mut s,dt);
        match kind { "PAIR"=>{let v=s.a.v;s.a.v=s.b.v;s.b.v=v;}, "A_WALL"=>s.a.v=s.a.v.neg(), "B_WALL"=>s.b.v=s.b.v.neg(), _=>unreachable!() }
        let row=format!("{}|{}|{}|{}|{}|{}|{},{}\n",i+1,kind,dt,s.time,s.a.x,s.a.v,s.b.x,s.b.v);
        h=fnv(h,&row);
        if i<12 { print!("{}",row); }
    }
    println!("SUMMARY events={} time={} ax={} av={} bx={} bv={} fnv64={:016x}",N,s.time,s.a.x,s.a.v,s.b.x,s.b.v,h);
}
