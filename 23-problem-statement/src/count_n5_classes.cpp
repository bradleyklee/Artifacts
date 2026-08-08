#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <memory>
#include <numeric>
#include <string>
#include <unordered_set>
#include <vector>

struct Node {
    bool leaf = false;
    std::array<std::shared_ptr<Node>,4> ch{};
};
using P = std::shared_ptr<Node>;

static std::array<std::vector<P>, 6> memo;
static std::array<bool, 6> built{};

std::vector<std::array<int,4>> comps4(int n) {
    std::vector<std::array<int,4>> out;
    for (int a=0;a<=n;++a) for(int b=0;b<=n-a;++b)
      for(int c=0;c<=n-a-b;++c) {
        int d=n-a-b-c;
        out.push_back({a,b,c,d});
      }
    return out;
}

const std::vector<P>& trees(int n) {
    if (built[n]) return memo[n];
    built[n]=true;
    if (n==1) {
        auto x=std::make_shared<Node>(); x->leaf=true; memo[n].push_back(x); return memo[n];
    }
    for (auto cnt: comps4(n)) {
        int nz=0; for(int c:cnt) nz += c>0;
        if(nz<2) continue;
        std::array<const std::vector<P>*,4> choices{};
        std::array<std::vector<P>,4> nullvec;
        for(int i=0;i<4;++i) {
            if(cnt[i]==0) { nullvec[i].push_back(nullptr); choices[i]=&nullvec[i]; }
            else choices[i]=&trees(cnt[i]);
        }
        for(auto a:*choices[0]) for(auto b:*choices[1]) for(auto c:*choices[2]) for(auto d:*choices[3]) {
            auto x=std::make_shared<Node>(); x->ch={a,b,c,d}; memo[n].push_back(x);
        }
    }
    return memo[n];
}

int depth(const P& x) {
    if(x->leaf) return 0;
    int m=0; for(auto& c:x->ch) if(c) m=std::max(m,depth(c));
    return 1+m;
}

void fill_grid(const P& x, int x0, int y0, int size, std::vector<uint8_t>& g, int W, int& next) {
    if(x->leaf) {
        uint8_t id=(uint8_t)next++;
        for(int y=y0;y<y0+size;++y) for(int xx=x0;xx<x0+size;++xx) g[y*W+xx]=id;
        return;
    }
    int h=size/2;
    // Python QUADRANTS: NW, SW, SE, NE
    static const int qx[4]={0,0,1,1};
    static const int qy[4]={0,1,1,0};
    for(int i=0;i<4;++i) if(x->ch[i]) fill_grid(x->ch[i],x0+qx[i]*h,y0+qy[i]*h,h,g,W,next);
}

std::vector<std::array<int,5>> cyclic_orders5() {
    std::vector<std::array<int,5>> out;
    std::array<int,4> r={1,2,3,4};
    do {
        std::array<int,4> rev={r[3],r[2],r[1],r[0]};
        if(r<=rev) out.push_back({0,r[0],r[1],r[2],r[3]});
    } while(std::next_permutation(r.begin(),r.end()));
    return out;
}

std::pair<int,int> transform_xy(int x,int y,int W,int t) {
    // 8 elements: 4 rotations, optionally mirror x after rotation.
    int a=x,b=y;
    int k=t/2;
    for(int i=0;i<k;++i) { int na=W-1-b, nb=a; a=na; b=nb; }
    if(t%2) a=W-1-a;
    return {a,b};
}

std::string canonical(const std::vector<uint8_t>& labels, int W) {
    std::string best;
    bool first=true;
    std::vector<uint8_t> img(W*W);
    for(int t=0;t<8;++t) {
        std::fill(img.begin(),img.end(),0);
        for(int y=0;y<W;++y) for(int x=0;x<W;++x) {
            auto [a,b]=transform_xy(x,y,W,t);
            img[b*W+a]=labels[y*W+x];
        }
        for(int sign: {1,-1}) for(int shift=0;shift<5;++shift) {
            std::string key; key.resize(1+W*W); key[0]=(char)W;
            for(int i=0;i<W*W;++i) {
                int v=img[i];
                if(v>0) {
                    int z=v-1;
                    int q=(sign*z+shift)%5; if(q<0)q+=5;
                    v=q+1;
                }
                key[1+i]=(char)v;
            }
            if(first || key<best) {best=std::move(key); first=false;}
        }
    }
    return best;
}

int main() {
    auto start=std::chrono::steady_clock::now();
    const auto& ts=trees(5);
    auto orders=cyclic_orders5();
    std::array<std::unordered_set<std::string>,5> bydepth;
    std::unordered_set<std::string> all;
    size_t raw=0;
    for(size_t ti=0;ti<ts.size();++ti) {
        int d=depth(ts[ti]); int W=1<<d;
        std::vector<uint8_t> leafgrid(W*W,255); int next=0;
        fill_grid(ts[ti],0,0,W,leafgrid,W,next);
        if(next!=5) { std::cerr<<"bad leaves\n"; return 2; }
        for(auto ord:orders) {
            uint8_t map[5];
            for(int label=1;label<=5;++label) map[ord[label-1]]=label;
            std::vector<uint8_t> lab(W*W,0);
            for(int i=0;i<W*W;++i) if(leafgrid[i]!=255) lab[i]=map[leafgrid[i]];
            auto key=canonical(lab,W);
            bydepth[d].insert(key); all.insert(std::move(key)); ++raw;
        }
        if((ti+1)%2000==0) std::cerr<<"trees "<<(ti+1)<<"/"<<ts.size()<<" unique="<<all.size()<<"\n";
    }
    auto sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
    std::cout<<"trees="<<ts.size()<<"\norders="<<orders.size()<<"\nraw="<<raw<<"\nclasses="<<all.size()<<"\n";
    for(int d=1;d<=4;++d) std::cout<<"depth"<<d<<"="<<bydepth[d].size()<<"\n";
    std::cout<<"seconds="<<sec<<"\n";
}
