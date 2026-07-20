#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>

using i64=std::int64_t;
using i128=__int128_t;

struct Point { i64 x,y; };
struct SurdPoint { i64 px,qx,py,qy,d,den; };

int sign_surd(i128 p,i128 q,i128 d) {
    if (q==0 || d==0) return (p>0)-(p<0);
    if (p>=0 && q>0) return 1;
    if (p<=0 && q<0) return -1;
    const i128 pp=p*p, qq=q*q*d;
    if (pp==qq) return 0;
    if (p>0) return pp>qq ? 1 : -1;
    return qq>pp ? 1 : -1;
}

bool in_triangle(const SurdPoint& c) {
    // 0 <= y <= x <= 1/2.
    if (sign_surd(c.py,c.qy,c.d)<0) return false;
    if (sign_surd(c.px-c.py,c.qx-c.qy,c.d)<0) return false;
    return sign_surd(2*i128(c.px)-c.den,2*i128(c.qx),c.d)<=0;
}

bool inside_surd(const Point& z,const SurdPoint& c,i64 n) {
    const i128 nx=i128(z.x)*c.den-c.px;
    const i128 ny=i128(z.y)*c.den-c.py;
    const i128 r=nx*nx+i128(c.qx)*c.qx*c.d
                 +ny*ny+i128(c.qy)*c.qy*c.d
                 -i128(n)*n*c.den*c.den;
    const i128 q=-2*(nx*c.qx+ny*c.qy);
    return sign_surd(r,q,c.d)<=0;
}

bool inside_arc(i64 X,i64 Y,i64 a,i64 b,i64 s,i64 m,int sgn) {
    const i64 A=X*X+Y*Y-X*a-Y*b;
    const i64 B=i64(sgn)*(Y*a-X*b);
    if (B==0) return A<=0;
    if (A<=0 && B>=0) return true;
    if (A>0 && B<=0) return false;
    const i128 lhs=i128(A)*A*s, rhs=i128(B)*B*m;
    return B>0 ? lhs<=rhs : lhs>=rhs;
}

struct Classified { i64 core=0; std::vector<Point> volatile_points; };

Classified classify(i64 n) {
    Classified out;
    const i64 four_n2=4*n*n;
    for (i64 a=-n;a<=n;++a) for (i64 b=-n;b<=n;++b) {
        auto near2=[](i64 x) { return x<0 ? -2*x : (x>0 ? 2*x-1 : 0); };
        auto far2=[](i64 x) { return std::max(std::llabs(2*x),std::llabs(1-2*x)); };
        const i64 min4=near2(a)*near2(a)+near2(b)*near2(b);
        const i64 max4=far2(a)*far2(a)+far2(b)*far2(b);
        if (max4<=four_n2) ++out.core;
        else if (min4<=four_n2) out.volatile_points.push_back({a,b});
    }
    return out;
}

i64 depth_surd(const std::vector<Point>& v,const SurdPoint& c,i64 n,i64 best) {
    i64 depth=0;
    for (std::size_t k=0;k<v.size();++k) {
        if (inside_surd(v[k],c,n)) ++depth;
        if (depth+i64(v.size()-k-1)<best) return -1;
    }
    return depth;
}

i64 depth_arc(const std::vector<Point>& v,i64 a1,i64 b1,
              i64 a,i64 b,i64 s,i64 m,int sgn,i64 best) {
    i64 depth=0;
    for (std::size_t k=0;k<v.size();++k) {
        if (inside_arc(v[k].x-a1,v[k].y-b1,a,b,s,m,sgn)) ++depth;
        if (depth+i64(v.size()-k-1)<best) return -1;
    }
    return depth;
}

std::vector<SurdPoint> boundary_features(const std::vector<Point>& v,i64 n) {
    std::vector<SurdPoint> f={{0,0,0,0,1,1},{1,0,0,0,1,2},{1,0,1,0,1,2}};
    const i64 n2=n*n;
    for (const Point p:v) {
        // y=0: x=p.x +/- sqrt(n^2-p.y^2)
        i64 d=n2-p.y*p.y;
        if (d>=0) for (int q:{-1,1}) {
            SurdPoint c{p.x,q,0,0,d,1};
            if (in_triangle(c)) f.push_back(c);
        }
        // x=1/2: y=p.y +/- sqrt(n^2-(1/2-p.x)^2)
        d=4*n2-(1-2*p.x)*(1-2*p.x);
        if (d>=0) for (int q:{-1,1}) {
            SurdPoint c{1,0,2*p.y,q,d,2};
            if (in_triangle(c)) f.push_back(c);
        }
        // y=x: x=(p.x+p.y +/- sqrt(2n^2-(p.x-p.y)^2))/2
        d=2*n2-(p.x-p.y)*(p.x-p.y);
        if (d>=0) for (int q:{-1,1}) {
            SurdPoint c{p.x+p.y,q,p.x+p.y,q,d,2};
            if (in_triangle(c)) f.push_back(c);
        }
    }
    return f;
}

i64 term(i64 n) {
    if (n==0) return 1;
    const Classified cc=classify(n);
    const auto& v=cc.volatile_points;
    i64 best=0;
    for (const SurdPoint& c:boundary_features(v,n))
        best=std::max(best,depth_surd(v,c,n,best));

    const i64 seed=best, nn=i64(v.size()), four_n2=4*n*n;
#ifdef _OPENMP
#pragma omp parallel for schedule(dynamic) reduction(max:best)
#endif
    for (i64 i=0;i<nn-1;++i) {
        i64 localbest=seed;
        const i64 a1=v[i].x,b1=v[i].y;
        for (i64 j=i+1;j<nn;++j) {
            const i64 a=v[j].x-a1,b=v[j].y-b1,s=a*a+b*b,m=four_n2-s;
            if (m<0) continue;
            const i64 d=s*m, den=2*s;
            for (int sgn:{-1,1}) {
                SurdPoint c{s*(2*a1+a),-i64(sgn)*b,
                            s*(2*b1+b), i64(sgn)*a,d,den};
                if (!in_triangle(c)) continue;
                localbest=std::max(localbest,
                    depth_arc(v,a1,b1,a,b,s,m,sgn,localbest));
            }
        }
        best=std::max(best,localbest);
    }
    return cc.core+best;
}

int main(int argc,char** argv) {
    if (argc<2) { std::cerr<<"usage: a295344_regions LAST [FIRST]\n"; return 2; }
    const i64 last=std::strtoll(argv[1],nullptr,10);
    const i64 first=argc>2 ? std::strtoll(argv[2],nullptr,10) : 0;
    for (i64 n=first;n<=last;++n) {
        const auto start=std::chrono::steady_clock::now();
        const i64 answer=term(n);
        const double seconds=std::chrono::duration<double>(
            std::chrono::steady_clock::now()-start).count();
        std::cout<<n<<' '<<answer<<' '<<seconds<<'\n';
    }
}
