// Exact exhaustive enumerator for square-lattice polyominoes that are exactly
// the lattice sites of a translated axis-aligned ellipse.
//
// An ellipse is represented by
//   Q(x,y) = A x^2 + B y^2 + C x + D y + E <= 0, with A,B > 0.
// We normalize A+B=1.  A candidate P is accepted when an exact rational LP
// finds epsilon>0 such that all occupied hull vertices satisfy Q<=0 and all
// immediate exterior lattice sites satisfy Q>=epsilon, with A,B>=epsilon.
//
// The LP is solved by an exact simplex using boost::multiprecision::cpp_rational.
// No floating point participates in acceptance or rejection.

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

#include <boost/multiprecision/cpp_int.hpp>

using i64 = std::int64_t;
using i128 = __int128_t;
using Rat = boost::multiprecision::cpp_rational;

struct Point {
    i64 x = 0;
    i64 y = 0;
    friend bool operator==(const Point& a, const Point& b) {
        return a.x == b.x && a.y == b.y;
    }
    friend bool operator<(const Point& a, const Point& b) {
        return std::tie(a.x, a.y) < std::tie(b.x, b.y);
    }
};

using Poly = std::vector<Point>;
using PolySet = std::set<Poly>;
using Vec = std::vector<Rat>;
using Mat = std::vector<Vec>;

static constexpr std::array<Point, 4> kDirections{{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}};

[[nodiscard]] Poly normalize(Poly cells) {
    if (cells.empty()) return cells;
    i64 min_x = cells.front().x;
    i64 min_y = cells.front().y;
    for (const Point& p : cells) {
        min_x = std::min(min_x, p.x);
        min_y = std::min(min_y, p.y);
    }
    for (Point& p : cells) {
        p.x -= min_x;
        p.y -= min_y;
    }
    std::sort(cells.begin(), cells.end());
    return cells;
}

[[nodiscard]] Point transform_point(const Point& p, int t) {
    switch (t) {
        case 0: return { p.x,  p.y};
        case 1: return { p.x, -p.y};
        case 2: return {-p.x,  p.y};
        case 3: return {-p.x, -p.y};
        case 4: return { p.y,  p.x};
        case 5: return { p.y, -p.x};
        case 6: return {-p.y,  p.x};
        case 7: return {-p.y, -p.x};
        default: throw std::logic_error("bad D4 transform");
    }
}

[[nodiscard]] Poly canonical(const Poly& cells) {
    Poly best;
    bool have_best = false;
    for (int t = 0; t < 8; ++t) {
        Poly image;
        image.reserve(cells.size());
        for (const Point& p : cells) image.push_back(transform_point(p, t));
        image = normalize(std::move(image));
        if (!have_best || image < best) {
            best = std::move(image);
            have_best = true;
        }
    }
    return best;
}

[[nodiscard]] i128 cross(const Point& o, const Point& a, const Point& b) {
    return static_cast<i128>(a.x - o.x) * (b.y - o.y)
         - static_cast<i128>(a.y - o.y) * (b.x - o.x);
}

[[nodiscard]] std::vector<Point> convex_hull(const Poly& points) {
    std::vector<Point> pts = points;
    std::sort(pts.begin(), pts.end());
    pts.erase(std::unique(pts.begin(), pts.end()), pts.end());
    if (pts.size() <= 1) return pts;
    std::vector<Point> lower;
    for (const Point& p : pts) {
        while (lower.size() >= 2 && cross(lower[lower.size()-2], lower.back(), p) <= 0) lower.pop_back();
        lower.push_back(p);
    }
    std::vector<Point> upper;
    for (auto it = pts.rbegin(); it != pts.rend(); ++it) {
        while (upper.size() >= 2 && cross(upper[upper.size()-2], upper.back(), *it) <= 0) upper.pop_back();
        upper.push_back(*it);
    }
    lower.pop_back();
    upper.pop_back();
    lower.insert(lower.end(), upper.begin(), upper.end());
    return lower;
}

[[nodiscard]] i64 abs_i64(i64 value) { return value < 0 ? -value : value; }

[[nodiscard]] i128 hull_lattice_point_count(const std::vector<Point>& hull) {
    if (hull.empty()) return 0;
    if (hull.size() == 1) return 1;
    if (hull.size() == 2) {
        return std::gcd(abs_i64(hull[1].x - hull[0].x), abs_i64(hull[1].y - hull[0].y)) + 1;
    }
    i128 twice_area = 0;
    i128 boundary = 0;
    for (std::size_t i = 0; i < hull.size(); ++i) {
        const Point& a = hull[i];
        const Point& b = hull[(i + 1) % hull.size()];
        twice_area += static_cast<i128>(a.x)*b.y - static_cast<i128>(a.y)*b.x;
        boundary += std::gcd(abs_i64(b.x-a.x), abs_i64(b.y-a.y));
    }
    if (twice_area < 0) twice_area = -twice_area;
    return (twice_area + boundary + 2) / 2;
}

[[nodiscard]] bool lattice_convex(const Poly& poly) {
    return hull_lattice_point_count(convex_hull(poly)) == static_cast<i128>(poly.size());
}

[[nodiscard]] std::vector<Point> immediate_exterior(const Poly& poly) {
    const std::set<Point> cells(poly.begin(), poly.end());
    std::set<Point> exterior;
    for (const Point& p : poly) {
        for (const Point& d : kDirections) {
            const Point q{p.x+d.x, p.y+d.y};
            if (!cells.contains(q)) exterior.insert(q);
        }
    }
    return {exterior.begin(), exterior.end()};
}

// Exact two-phase simplex.  This is the standard tableau construction, but
// every tableau entry is a GMP-backed rational number.  It maximizes c*x
// subject to A*x <= b and x >= 0.
class ExactSimplex {
public:
    enum class Status { kOptimal, kInfeasible, kUnbounded };

    ExactSimplex(const Mat& A, const Vec& b, const Vec& c)
        : m_(static_cast<int>(b.size())), n_(static_cast<int>(c.size())),
          B_(m_), N_(n_+1), D_(m_+2, Vec(n_+2, Rat(0))) {
        for (int i = 0; i < m_; ++i) {
            for (int j = 0; j < n_; ++j) D_[i][j] = A[i][j];
            B_[i] = n_ + i;
            D_[i][n_] = -1;
            D_[i][n_+1] = b[i];
        }
        for (int j = 0; j < n_; ++j) {
            N_[j] = j;
            D_[m_][j] = -c[j];
        }
        N_[n_] = -1;
        D_[m_+1][n_] = 1;
    }

    [[nodiscard]] Status solve(Vec& x, Rat& value) {
        int r = 0;
        for (int i = 1; i < m_; ++i) {
            if (D_[i][n_+1] < D_[r][n_+1]) r = i;
        }
        if (D_[r][n_+1] < 0) {
            pivot(r, n_);
            if (!simplex(1) || D_[m_+1][n_+1] < 0) return Status::kInfeasible;
            // Exact arithmetic: a nonzero phase-I objective means infeasible.
            if (D_[m_+1][n_+1] != 0) return Status::kInfeasible;
            for (int i = 0; i < m_; ++i) {
                if (B_[i] == -1) {
                    int s = -1;
                    for (int j = 0; j <= n_; ++j) {
                        if (s == -1 || D_[i][j] < D_[i][s] ||
                            (D_[i][j] == D_[i][s] && N_[j] < N_[s])) s = j;
                    }
                    pivot(i, s);
                }
            }
        }
        if (!simplex(2)) return Status::kUnbounded;
        x.assign(n_, Rat(0));
        for (int i = 0; i < m_; ++i) {
            if (B_[i] >= 0 && B_[i] < n_) x[B_[i]] = D_[i][n_+1];
        }
        value = D_[m_][n_+1];
        return Status::kOptimal;
    }

private:
    int m_;
    int n_;
    std::vector<int> B_, N_;
    Mat D_;

    void pivot(int r, int s) {
        const Rat inv = Rat(1) / D_[r][s];
        for (int i = 0; i < m_+2; ++i) {
            if (i == r) continue;
            for (int j = 0; j < n_+2; ++j) {
                if (j == s) continue;
                D_[i][j] -= D_[r][j] * D_[i][s] * inv;
            }
        }
        for (int j = 0; j < n_+2; ++j) if (j != s) D_[r][j] *= inv;
        for (int i = 0; i < m_+2; ++i) if (i != r) D_[i][s] *= -inv;
        D_[r][s] = inv;
        std::swap(B_[r], N_[s]);
    }

    [[nodiscard]] bool simplex(int phase) {
        const int x = (phase == 1 ? m_+1 : m_);
        while (true) {
            int s = -1;
            for (int j = 0; j <= n_; ++j) {
                if (phase == 2 && N_[j] == -1) continue;
                if (s == -1 || D_[x][j] < D_[x][s] ||
                    (D_[x][j] == D_[x][s] && N_[j] < N_[s])) s = j;
            }
            if (D_[x][s] >= 0) return true;
            int r = -1;
            for (int i = 0; i < m_; ++i) {
                if (D_[i][s] <= 0) continue;
                if (r == -1) {
                    r = i;
                    continue;
                }
                const Rat lhs = D_[i][n_+1] / D_[i][s];
                const Rat rhs = D_[r][n_+1] / D_[r][s];
                if (lhs < rhs || (lhs == rhs && B_[i] < B_[r])) r = i;
            }
            if (r == -1) return false;
            pivot(r, s);
        }
    }
};

struct EllipseWitness {
    Rat a;       // normalized x^2 coefficient A
    Rat b;       // normalized y^2 coefficient 1-A
    Rat c;
    Rat d;
    Rat e;
    Rat epsilon;
};

[[nodiscard]] Rat as_rat(i64 x) { return Rat(x); }

[[nodiscard]] bool axis_aligned_ellipse_accepts(const Poly& poly, EllipseWitness* witness = nullptr) {
    // A lattice-convex P is all lattice points of conv(P).  Since Q<=0 is
    // convex when A,B>0, it is enough to constrain hull vertices on the inside.
    const std::vector<Point> hull = convex_hull(poly);
    const std::vector<Point> exterior = immediate_exterior(poly);

    // Variables: [A, Cplus, Cminus, Dplus, Dminus, Eplus, Eminus, epsilon].
    // C=Cplus-Cminus etc.; all variables are nonnegative.
    constexpr int kVars = 8;
    Mat constraints;
    Vec rhs;
    auto add = [&](const std::array<i64,kVars>& coeff, i64 bound) {
        Vec row;
        row.reserve(kVars);
        for (i64 value : coeff) row.push_back(as_rat(value));
        constraints.push_back(std::move(row));
        rhs.push_back(as_rat(bound));
    };

    // epsilon <= A and epsilon <= B=1-A.
    add({-1,0,0,0,0,0,0, 1}, 0);
    add({ 1,0,0,0,0,0,0, 1}, 1);

    for (const Point& p : hull) {
        const i64 delta = p.x*p.x - p.y*p.y;
        // Q(p) = A*delta + C*x + D*y + E + y^2 <= 0.
        add({delta, p.x, -p.x, p.y, -p.y, 1, -1, 0}, -p.y*p.y);
    }
    for (const Point& q : exterior) {
        const i64 delta = q.x*q.x - q.y*q.y;
        // Q(q) >= epsilon.
        add({-delta, -q.x, q.x, -q.y, q.y, -1, 1, 1}, q.y*q.y);
    }

    Vec objective(kVars, Rat(0));
    objective[7] = 1;
    ExactSimplex lp(constraints, rhs, objective);
    Vec solution;
    Rat optimum;
    const ExactSimplex::Status status = lp.solve(solution, optimum);
    if (status != ExactSimplex::Status::kOptimal || optimum <= 0) return false;

    if (witness) {
        witness->a = solution[0];
        witness->b = 1 - solution[0];
        witness->c = solution[1] - solution[2];
        witness->d = solution[3] - solution[4];
        witness->e = solution[5] - solution[6];
        witness->epsilon = solution[7];
    }
    return true;
}

void add_one_square(const PolySet& parents, PolySet& children) {
    for (const Poly& poly : parents) {
        const std::set<Point> cells(poly.begin(), poly.end());
        for (const Point& p : poly) {
            for (const Point& d : kDirections) {
                const Point q{p.x+d.x, p.y+d.y};
                if (cells.contains(q)) continue;
                Poly child = poly;
                child.push_back(q);
                children.insert(canonical(child));
            }
        }
    }
}

[[nodiscard]] PolySet one_square_extensions(const PolySet& parents) {
    PolySet children;
    add_one_square(parents, children);
    return children;
}


struct Row {
    int n = 1;
    std::string mode;
    std::size_t source_candidates = 0;
    std::size_t lattice_convex = 0;
    std::size_t ellipses = 0;
    double seconds = 0.0;
};

struct Options {
    int max_n = 10;
    int exhaustive_through = -1;  // -1 means exhaustive at every requested order.
    int depth = 1;
    std::string csv_path;
    bool dump_witnesses = false;
};

[[nodiscard]] Options parse_options(int argc, char** argv) {
    Options options;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        auto require_value = [&](const char* flag) -> std::string {
            if (i+1 >= argc) throw std::runtime_error(std::string("missing value after ") + flag);
            return argv[++i];
        };
        if (arg == "--max-n") options.max_n = std::stoi(require_value("--max-n"));
        else if (arg == "--exhaustive-through") options.exhaustive_through = std::stoi(require_value("--exhaustive-through"));
        else if (arg == "--depth") options.depth = std::stoi(require_value("--depth"));
        else if (arg == "--csv") options.csv_path = require_value("--csv");
        else if (arg == "--dump-witnesses") options.dump_witnesses = true;
        else if (arg == "--help" || arg == "-h") {
            std::cout
                << "Usage: ellipse_polyomino [--max-n N] [--exhaustive-through N] [--depth 1|2] [--csv FILE] [--dump-witnesses]\n\n"
                << "Without --exhaustive-through, enumerate every free polyomino through N.\n"
                << "With --exhaustive-through K<N, enumerate freely through K, then continue by\n"
                << "one-square accepted-successor growth; depth 2 also includes two-square\n"
                << "extensions from the accepted level two orders earlier.\n";
            std::exit(0);
        } else throw std::runtime_error("unknown option: " + arg);
    }
    if (options.max_n < 1) throw std::runtime_error("--max-n must be positive");
    if (options.exhaustive_through == -1) options.exhaustive_through = options.max_n;
    if (options.exhaustive_through < 1 || options.exhaustive_through > options.max_n) {
        throw std::runtime_error("--exhaustive-through must lie in 1..--max-n");
    }
    if (options.depth != 1 && options.depth != 2) throw std::runtime_error("--depth must be 1 or 2");
    return options;
}

void write_csv_header(std::ostream& out) {
    out << "n,mode,source_candidates,lattice_convex,axis_aligned_ellipses,seconds\n";
}
void write_csv_row(std::ostream& out, const Row& r) {
    out << r.n << ',' << r.mode << ',' << r.source_candidates << ',' << r.lattice_convex << ',' << r.ellipses << ',' << r.seconds << '\n';
}

[[nodiscard]] PolySet classify_candidates(
    const PolySet& candidates,
    int n,
    std::size_t& convex_count,
    bool dump_witnesses
) {
    PolySet accepted;
    convex_count = 0;
    for (const Poly& poly : candidates) {
        if (!lattice_convex(poly)) continue;
        ++convex_count;
        EllipseWitness witness;
        if (axis_aligned_ellipse_accepts(poly, dump_witnesses ? &witness : nullptr)) {
            accepted.insert(poly);
            if (dump_witnesses) {
                std::cout << "  witness n=" << n << " P=";
                for (const Point& p : poly) std::cout << '(' << p.x << ',' << p.y << ')';
                std::cout << " A=" << witness.a << " B=" << witness.b
                          << " C=" << witness.c << " D=" << witness.d
                          << " E=" << witness.e << " eps=" << witness.epsilon << '\n';
            }
        }
    }
    return accepted;
}

int main(int argc, char** argv) {
    try {
        const Options options = parse_options(argc, argv);
        std::ofstream csv;
        if (!options.csv_path.empty()) {
            csv.open(options.csv_path);
            if (!csv) throw std::runtime_error("cannot open CSV output: " + options.csv_path);
            write_csv_header(csv);
        }

        PolySet free_level{{Poly{{0,0}}}};
        PolySet accepted_prev1;
        PolySet accepted_prev2;
        std::cout << "n  mode        source-candidates  lattice-convex  axis-aligned-ellipses  seconds\n";

        for (int n = 1; n <= options.max_n; ++n) {
            const auto started = std::chrono::steady_clock::now();
            const bool exhaustive = n <= options.exhaustive_through;
            PolySet candidates;
            std::string mode;
            if (exhaustive) {
                candidates = free_level;
                mode = "free";
            } else {
                candidates = one_square_extensions(accepted_prev1);
                if (options.depth == 2 && n >= 3) {
                    const PolySet plus2 = [&] {
                        PolySet once;
                        add_one_square(accepted_prev2, once);
                        PolySet twice;
                        add_one_square(once, twice);
                        return twice;
                    }();
                    candidates.insert(plus2.begin(), plus2.end());
                    mode = "grow+2";
                } else {
                    mode = "grow+1";
                }
            }

            std::size_t convex_count = 0;
            PolySet accepted = classify_candidates(candidates, n, convex_count, options.dump_witnesses);
            const double seconds = std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count();
            const Row row{n, mode, candidates.size(), convex_count, accepted.size(), seconds};
            std::cout << std::setw(2) << row.n << "  " << std::setw(8) << row.mode
                      << std::setw(21) << row.source_candidates
                      << std::setw(17) << row.lattice_convex
                      << std::setw(24) << row.ellipses
                      << std::fixed << std::setprecision(4) << std::setw(10) << row.seconds << '\n';
            if (csv) write_csv_row(csv, row);

            accepted_prev2 = std::move(accepted_prev1);
            accepted_prev1 = std::move(accepted);
            if (n < options.exhaustive_through) {
                PolySet next;
                add_one_square(free_level, next);
                free_level = std::move(next);
            }
        }
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 2;
    }
    return 0;
}
