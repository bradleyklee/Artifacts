#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <vector>
#include <stdexcept>

using i64=std::int64_t;
using i128=__int128_t;
using u64=std::uint64_t;
using u128=__uint128_t;

struct U256 { u64 w[4]={0,0,0,0}; };

void add_product(U256& z,int k,u128 p) {
    u128 t=u128(z.w[k])+u64(p);
    z.w[k]=u64(t); u64 carry=u64(t>>64);
    t=u128(z.w[k+1])+u64(p>>64)+carry;
    z.w[k+1]=u64(t); carry=u64(t>>64);
    for (int i=k+2;carry && i<4;++i) {
        t=u128(z.w[i])+carry; z.w[i]=u64(t); carry=u64(t>>64);
    }
}

U256 square128(u128 x) {
    const u64 lo=u64(x),hi=u64(x>>64);
    U256 z;
    add_product(z,0,u128(lo)*lo);
    add_product(z,1,u128(lo)*hi);
    add_product(z,1,u128(lo)*hi);
    add_product(z,2,u128(hi)*hi);
    return z;
}

U256 times64(const U256& x,u64 y) {
    U256 z; u128 carry=0;
    for (int i=0;i<4;++i) {
        const u128 t=u128(x.w[i])*y+carry;
        z.w[i]=u64(t); carry=t>>64;
    }
    if (carry) throw std::overflow_error("U256 overflow");
    return z;
}

int compare256(const U256& x,const U256& y) {
    for (int i=3;i>=0;--i)
        if (x.w[i]!=y.w[i]) return x.w[i]>y.w[i] ? 1:-1;
    return 0;
}

u128 magnitude(i128 x) { return x<0 ? u128(-(x+1))+1:u128(x); }

int sign_surd_wide(i128 p,i128 q,u64 d) {
    if (q==0 || d==0) return (p>0)-(p<0);
    if (p>=0 && q>0) return 1;
    if (p<=0 && q<0) return -1;
    const int cmp=compare256(square128(magnitude(p)),times64(square128(magnitude(q)),d));
    if (cmp==0) return 0;
    return p>0 ? cmp:-cmp;
}

int sign_surd(i128 p,i128 q,i128 d) {
    if (q==0 || d==0) return (p>0)-(p<0);
    if (p>=0 && q>0) return 1;
    if (p<=0 && q<0) return -1;
    const i128 pp=p*p,qq=q*q*d;
    if (pp==qq) return 0;
    if (p>0) return pp>qq ? 1:-1;
    return qq>pp ? 1:-1;
}

enum Kind { ENTER,EXIT,TOUCH };

struct Event {
    i64 a,b,s,m;
    int sign;
    Kind kind;
    long double angle;
};

bool in_sector(i64 a,i64 b,i64 s,i64 m,int sign) {
    const i64 d=s*m;
    // 2s*c=(s*a-sign*b*sqrt(d), s*b+sign*a*sqrt(d)).
    const i128 px=i128(s)*a, qx=-i128(sign)*b;
    const i128 py=i128(s)*b, qy= i128(sign)*a;
    return sign_surd(px,qx,d)>=0 && sign_surd(py,qy,d)>=0 &&
           sign_surd(px-py,qx-qy,d)>=0;
}

bool same_center(const Event& e,const Event& f) {
    // Test whether f's lattice point lies on e's event circle.
    const i64 A=f.s-f.a*e.a-f.b*e.b;
    const i64 B=i64(e.sign)*(-f.a*e.b+f.b*e.a);
    if (e.m==0) return A==0;
    if (B==0) return A==0;
    if ((A<0)!=(B<0) || A==0) return false;
    return i128(A)*A*e.s==i128(B)*B*e.m;
}

int compare_slope_to_dyadic(const Event& e,i64 k,i64 scale) {
    // sign(scale*c_y-k*c_x), with the common positive denominator removed.
    const i128 p=i128(scale)*e.s*e.b-i128(k)*e.s*e.a;
    const i128 q=i128(scale)*e.sign*e.a+i128(k)*e.sign*e.b;
    return sign_surd_wide(p,q,u64(e.s)*e.m);
}

bool certify_order(const std::vector<Event>& e) {
    // Dyadic separators; every proposed adjacent order is checked exactly.
    constexpr int bits=50;
    const i64 scale=i64(1)<<bits;
    for (std::size_t i=1;i<e.size();++i) {
        if (same_center(e[i-1],e[i])) continue;
        const long double left=std::tan(e[i-1].angle);
        const long double right=std::tan(e[i].angle);
        const i64 k=std::llround((left+right)/2*scale);
        const int l=compare_slope_to_dyadic(e[i-1],k,scale);
        const int r=compare_slope_to_dyadic(e[i],k,scale);
        if (l>=0 || r<=0) {
            std::cerr<<"uncertified pair: "<<e[i-1].a<<','<<e[i-1].b
                     <<" and "<<e[i].a<<','<<e[i].b<<" angles "
                     <<(double)e[i-1].angle<<' '<<(double)e[i].angle
                     <<" signs "<<l<<' '<<r<<'\n';
            return false;
        }
    }
    return true;
}

std::vector<Event> events(i64 n) {
    std::vector<Event> out;
    const i64 four_n2=4*n*n;
    for (i64 a=-2*n;a<=2*n;++a) for (i64 b=-2*n;b<=2*n;++b) {
        const i64 s=a*a+b*b;
        if (s==0 || s>four_n2) continue;
        const i64 m=four_n2-s;
        if (m==0) {
            if (!in_sector(a,b,s,m,1)) continue;
            const long double x=(long double)a/2,y=(long double)b/2;
            out.push_back({a,b,s,m,1,TOUCH,std::atan2(y,x)});
            continue;
        }
        const long double r=std::sqrt((long double)m/s);
        for (int sign:{-1,1}) {
            if (!in_sector(a,b,s,m,sign)) continue;
            const long double x=(a-sign*b*r)/2;
            const long double y=(b+sign*a*r)/2;
            // sign=-1 has increasing coverage; sign=+1 has decreasing coverage.
            out.push_back({a,b,s,m,sign,sign<0?ENTER:EXIT,std::atan2(y,x)});
        }
    }
    std::sort(out.begin(),out.end(),[](const Event& x,const Event& y) {
        return x.angle<y.angle;
    });
    if (!certify_order(out))
        throw std::runtime_error("event order was not exactly certified");
    return out;
}

i64 count_at_zero(i64 n) {
    i64 count=0;
    for (i64 x=0;x<=2*n;++x)
        for (i64 y=-n;y<=n;++y)
            if ((x-n)*(x-n)+y*y<=n*n) ++count;
    return count;
}

struct Result { i64 count,chord2; };

Result term(i64 n) {
    if (n==0) return {1,0};
    const auto ev=events(n);
    i64 current=count_at_zero(n),best=current,best_chord2=0;
    std::size_t i=0;
    while (i<ev.size()) {
        std::size_t j=i+1;
        while (j<ev.size() && same_center(ev[i],ev[j])) ++j;
        i64 enters=0,exits=0,touches=0,max_chord2=0;
        for (std::size_t k=i;k<j;++k) {
            enters += ev[k].kind==ENTER;
            exits += ev[k].kind==EXIT;
            touches += ev[k].kind==TOUCH;
            max_chord2=std::max(max_chord2,ev[k].s);
        }
        const bool at_start=std::fabs(ev[i].angle)<1e-18L;
        const i64 exact=at_start ? current : current+enters+touches;
        if (exact>best || (exact==best && max_chord2>best_chord2))
            best=exact,best_chord2=max_chord2;
        current = at_start ? current-exits-touches : current+enters-exits;
        i=j;
    }
    return {best,best_chord2};
}

int main(int argc,char** argv) {
    if (argc<2) { std::cerr<<"usage: a295344_sweep LAST [FIRST]\n"; return 2; }
    const i64 last=std::strtoll(argv[1],nullptr,10);
    const i64 first=argc>2 ? std::strtoll(argv[2],nullptr,10):0;
    for (i64 n=first;n<=last;++n) {
        const auto start=std::chrono::steady_clock::now();
        const Result r=term(n);
        const double seconds=std::chrono::duration<double>(
            std::chrono::steady_clock::now()-start).count();
        std::cout<<n<<' '<<r.count<<' '<<r.chord2<<' '<<seconds<<'\n';
    }
}
