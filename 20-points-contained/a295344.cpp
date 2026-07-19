#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <queue>
#include <string>
#include <vector>

using i64 = std::int64_t;
using i128 = __int128_t;

struct Circle {
    i64 n, a, b, s, m; // r=sqrt(m/s), c=((a-b*r)/2,(b+a*r)/2)

    bool inside(i64 x, i64 y) const {
        const i64 A = x*x + y*y - x*a - y*b;
        const i64 B = -x*b + y*a;
        if (B == 0) return A <= 0;
        if (A <= 0 && B >= 0) return true;
        if (A > 0 && B <= 0) return false;
        const i128 lhs = i128(A)*A*s;
        const i128 rhs = i128(B)*B*m;
        return B > 0 ? lhs <= rhs : lhs >= rhs;
    }

    bool cx_at_least(i64 x) const {
        // a-b*sqrt(m/s) >= 2*x; b is nonnegative.
        const i64 A = a-2*x;
        if (b == 0) return A >= 0;
        if (A < 0) return false;
        return i128(A)*A*s >= i128(b)*b*m;
    }

    i64 floor_cx() const {
        i64 lo = -n-1, hi = n+1;
        while (lo+1 < hi) {
            const i64 mid = lo+(hi-lo)/2;
            if (cx_at_least(mid)) lo=mid; else hi=mid;
        }
        return lo;
    }

    i64 count_rows() const {
        const i64 bound=2*n, x0=floor_cx();
        i64 total=0;
        for (i64 y=-bound; y<=bound; ++y) {
            i64 anchor;
            if (inside(x0,y)) anchor=x0;
            else if (inside(x0+1,y)) anchor=x0+1;
            else continue;

            i64 lo=-bound, hi=anchor;
            while (lo<hi) {
                const i64 mid=lo+(hi-lo)/2;
                if (inside(mid,y)) hi=mid; else lo=mid+1;
            }
            const i64 left=lo;

            lo=anchor; hi=bound;
            while (lo<hi) {
                const i64 mid=lo+(hi-lo+1)/2;
                if (inside(mid,y)) lo=mid; else hi=mid-1;
            }
            total += lo-left+1;
        }
        return total;
    }
};

struct FloodCounter {
    i64 bound, width;
    int generation=0;
    std::vector<int> seen;
    std::vector<std::pair<i64,i64>> queue;

    explicit FloodCounter(i64 n): bound(2*n), width(4*n+1),
        seen(width*width,0) { queue.reserve(width*width); }

    i64 count(const Circle& c) {
        ++generation;
        queue.clear();
        auto index=[&](i64 x,i64 y) { return (y+bound)*width+x+bound; };
        auto try_add=[&](i64 x,i64 y) {
            if (x < -bound || x > bound || y < -bound || y > bound) return;
            const i64 k=index(x,y);
            if (seen[k] == generation) return;
            seen[k]=generation;
            if (c.inside(x,y)) queue.push_back({x,y});
        };
        try_add(0,0);
        for (std::size_t head=0; head<queue.size(); ++head) {
            auto [x,y]=queue[head];
            try_add(x-1,y); try_add(x+1,y);
            try_add(x,y-1); try_add(x,y+1);
        }
        return (i64)queue.size();
    }
};

struct Result { i64 count=1, a=0, b=0; };

Result term(i64 n, bool flood) {
    Result best;
    FloodCounter fc(n);
    const i64 diameter2=4*n*n;
    for (i64 a=1; a<=2*n; ++a) {
        for (i64 b=0; b<=a; ++b) {
            const i64 s=a*a+b*b;
            if (s > diameter2) continue;
            Circle c{n,a,b,s,diameter2-s};
            const i64 count=flood ? fc.count(c) : c.count_rows();
            if (count > best.count) best={count,a,b};
        }
    }
    return best;
}

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "usage: a295344 row|flood LAST [FIRST]\n";
        return 2;
    }
    const std::string method=argv[1];
    if (method != "row" && method != "flood") return 2;
    const i64 last=std::strtoll(argv[2],nullptr,10);
    const i64 first=argc > 3 ? std::strtoll(argv[3],nullptr,10) : 0;
    for (i64 n=first; n<=last; ++n) {
        const auto start=std::chrono::steady_clock::now();
        const Result r=term(n,method=="flood");
        const double seconds=std::chrono::duration<double>(
            std::chrono::steady_clock::now()-start).count();
        std::cout << n << ' ' << r.count << ' ' << r.a << ' ' << r.b
                  << ' ' << seconds << '\n';
    }
}
