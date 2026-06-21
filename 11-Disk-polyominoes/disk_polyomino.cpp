// Exact hereditary enumerator for square-lattice disk polyominoes.
//
// A polyomino is accepted when some Euclidean circle contains exactly its
// lattice sites.  For each pair A,B of exposed occupied boundary sites, the
// program tests the entire pencil of circles through A and B using exact
// rational interval arithmetic.  The immediate exterior lattice boundary is
// the separate strict-exclusion fence.
//
// --depth 1: level n comes from one-square extensions of accepted level n-1.
// --depth 2: also add all two-square extensions of accepted level n-2.  The
//            intermediate n-1 polyomino need not itself be accepted.
//
// Build: make
// Run:   ./disk_polyomino --max-n 50 --depth 2 --csv run.csv

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <limits>
#include <numeric>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

using i64 = std::int64_t;
using i128 = __int128_t;

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

static constexpr std::array<Point, 4> kDirections{{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}};
static constexpr std::array<int, 21> kOeis1To21{{
    1, 1, 1, 2, 2, 2, 1, 2, 2, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 4, 5
}};

[[nodiscard]] Poly normalize(Poly cells) {
    if (cells.empty()) {
        return cells;
    }
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

[[nodiscard]] Point transform_point(const Point& p, int transform) {
    switch (transform) {
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
    for (int transform = 0; transform < 8; ++transform) {
        Poly image;
        image.reserve(cells.size());
        for (const Point& p : cells) {
            image.push_back(transform_point(p, transform));
        }
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
    if (pts.size() <= 1) {
        return pts;
    }
    std::vector<Point> lower;
    for (const Point& p : pts) {
        while (lower.size() >= 2 && cross(lower[lower.size() - 2], lower.back(), p) <= 0) {
            lower.pop_back();
        }
        lower.push_back(p);
    }
    std::vector<Point> upper;
    for (auto it = pts.rbegin(); it != pts.rend(); ++it) {
        while (upper.size() >= 2 && cross(upper[upper.size() - 2], upper.back(), *it) <= 0) {
            upper.pop_back();
        }
        upper.push_back(*it);
    }
    lower.pop_back();
    upper.pop_back();
    lower.insert(lower.end(), upper.begin(), upper.end());
    return lower;
}

[[nodiscard]] i64 abs_i64(i64 x) {
    return x < 0 ? -x : x;
}

[[nodiscard]] i128 hull_lattice_point_count(const std::vector<Point>& hull) {
    if (hull.empty()) {
        return 0;
    }
    if (hull.size() == 1) {
        return 1;
    }
    if (hull.size() == 2) {
        const i64 dx = hull[1].x - hull[0].x;
        const i64 dy = hull[1].y - hull[0].y;
        return std::gcd(abs_i64(dx), abs_i64(dy)) + 1;
    }
    i128 twice_area = 0;
    i128 boundary = 0;
    for (std::size_t i = 0; i < hull.size(); ++i) {
        const Point& a = hull[i];
        const Point& b = hull[(i + 1) % hull.size()];
        twice_area += static_cast<i128>(a.x) * b.y - static_cast<i128>(a.y) * b.x;
        boundary += std::gcd(abs_i64(b.x - a.x), abs_i64(b.y - a.y));
    }
    if (twice_area < 0) {
        twice_area = -twice_area;
    }
    return (twice_area + boundary + 2) / 2;
}

[[nodiscard]] bool lattice_convex(const Poly& poly) {
    const std::vector<Point> hull = convex_hull(poly);
    return hull_lattice_point_count(hull) == static_cast<i128>(poly.size());
}

[[nodiscard]] std::vector<Point> immediate_exterior(const Poly& poly) {
    const std::set<Point> cells(poly.begin(), poly.end());
    std::set<Point> exterior;
    for (const Point& p : poly) {
        for (const Point& d : kDirections) {
            const Point q{p.x + d.x, p.y + d.y};
            if (!cells.contains(q)) {
                exterior.insert(q);
            }
        }
    }
    return {exterior.begin(), exterior.end()};
}

// An occupied lattice site is exposed when at least one of its four
// edge-neighbors is absent.  These are the lattice sites on the polyomino's
// exposed boundary; only they may be used as the two anchor contacts A,B.
[[nodiscard]] std::vector<Point> exposed_boundary_sites(const Poly& poly) {
    const std::set<Point> cells(poly.begin(), poly.end());
    std::vector<Point> boundary;
    boundary.reserve(poly.size());
    for (const Point& p : poly) {
        for (const Point& d : kDirections) {
            const Point q{p.x + d.x, p.y + d.y};
            if (!cells.contains(q)) {
                boundary.push_back(p);
                break;
            }
        }
    }
    return boundary;
}

// Rational numbers are used only as parameter bounds for one pencil.  We keep
// them unreduced: exact cross multiplication is faster than repeated gcd calls.
struct Rational {
    i128 num = 0;
    i128 den = 1;  // always positive

    Rational() = default;
    Rational(i128 numerator, i128 denominator) : num(numerator), den(denominator) {
        if (den == 0) {
            throw std::logic_error("zero rational denominator");
        }
        if (den < 0) {
            num = -num;
            den = -den;
        }
    }
};

[[nodiscard]] bool rational_less(const Rational& a, const Rational& b) {
    return a.num * b.den < b.num * a.den;
}

[[nodiscard]] bool rational_equal(const Rational& a, const Rational& b) {
    return a.num * b.den == b.num * a.den;
}

struct Interval {
    std::optional<Rational> lower;
    std::optional<Rational> upper;
    bool lower_strict = false;
    bool upper_strict = false;

    void strengthen_lower(const Rational& value, bool strict) {
        if (!lower || rational_less(*lower, value)) {
            lower = value;
            lower_strict = strict;
        } else if (rational_equal(*lower, value)) {
            lower_strict = lower_strict || strict;
        }
    }

    void strengthen_upper(const Rational& value, bool strict) {
        if (!upper || rational_less(value, *upper)) {
            upper = value;
            upper_strict = strict;
        } else if (rational_equal(*upper, value)) {
            upper_strict = upper_strict || strict;
        }
    }

    [[nodiscard]] bool feasible() const {
        if (!lower || !upper) {
            return true;
        }
        if (rational_less(*upper, *lower)) {
            return false;
        }
        return !rational_equal(*lower, *upper) || (!lower_strict && !upper_strict);
    }
};

struct Difference {
    i128 alpha_num;  // alpha = alpha_num / 4
    i128 beta;
};

[[nodiscard]] Difference distance_difference(const Point& a, const Point& b, const Point& x) {
    // Centers are c(t) = (A+B)/2 + t * (-(b_y-a_y), b_x-a_x).
    // Returns |X-c(t)|^2 - |A-c(t)|^2 = alpha_num/4 + beta*t.
    const i128 ux = static_cast<i128>(2) * x.x - a.x - b.x;
    const i128 uy = static_cast<i128>(2) * x.y - a.y - b.y;
    const i128 dx = static_cast<i128>(a.x) - b.x;
    const i128 dy = static_cast<i128>(a.y) - b.y;
    const i128 alpha_num = ux * ux + uy * uy - dx * dx - dy * dy;
    const i128 nx = -static_cast<i128>(b.y - a.y);
    const i128 ny =  static_cast<i128>(b.x - a.x);
    const i128 beta = -2 * (nx * (x.x - a.x) + ny * (x.y - a.y));
    return {alpha_num, beta};
}

[[nodiscard]] Rational event_parameter(const Difference& d) {
    // alpha_num/4 + beta*t = 0.
    return Rational(-d.alpha_num, static_cast<i128>(4) * d.beta);
}

[[nodiscard]] bool pair_pencil_accepts(
    const Poly& poly,
    const std::vector<Point>& exterior,
    const Point& a,
    const Point& b
) {
    Interval allowed;

    // Selected points must remain inside or on the circle.
    for (const Point& x : poly) {
        const Difference d = distance_difference(a, b, x);
        if (d.beta > 0) {
            allowed.strengthen_upper(event_parameter(d), false);
        } else if (d.beta < 0) {
            allowed.strengthen_lower(event_parameter(d), false);
        } else if (d.alpha_num > 0) {
            return false;
        }
    }

    // Immediate exterior points must remain strictly outside.
    for (const Point& x : exterior) {
        const Difference d = distance_difference(a, b, x);
        if (d.beta > 0) {
            allowed.strengthen_lower(event_parameter(d), true);
        } else if (d.beta < 0) {
            allowed.strengthen_upper(event_parameter(d), true);
        } else if (d.alpha_num <= 0) {
            return false;
        }
    }
    return allowed.feasible();
}

[[nodiscard]] bool accepts_by_boundary_pairs(const Poly& poly) {
    if (!lattice_convex(poly)) {
        return false;
    }
    if (poly.size() <= 1) {
        return true;
    }
    const std::vector<Point> exterior = immediate_exterior(poly);
    const std::vector<Point> boundary = exposed_boundary_sites(poly);
    for (std::size_t i = 0; i < boundary.size(); ++i) {
        for (std::size_t j = i + 1; j < boundary.size(); ++j) {
            if (pair_pencil_accepts(poly, exterior, boundary[i], boundary[j])) {
                return true;
            }
        }
    }
    return false;
}

void add_one_square(const PolySet& parents, PolySet& children) {
    for (const Poly& poly : parents) {
        const std::set<Point> cells(poly.begin(), poly.end());
        for (const Point& p : poly) {
            for (const Point& d : kDirections) {
                const Point q{p.x + d.x, p.y + d.y};
                if (cells.contains(q)) {
                    continue;
                }
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

[[nodiscard]] PolySet two_square_extensions(const PolySet& grandparents) {
    const PolySet intermediate = one_square_extensions(grandparents);
    return one_square_extensions(intermediate);
}

struct Row {
    int n = 1;
    std::size_t accepted_prev = 0;
    std::size_t accepted_prev2 = 0;
    std::size_t one_step = 0;
    std::size_t two_step = 0;
    std::size_t candidates = 0;
    std::size_t lattice_convex = 0;
    std::size_t accepted = 0;
    double seconds = 0.0;
};

struct Options {
    int max_n = 21;
    int depth = 1;
    bool verify_oeis = false;
    std::string csv_path;
};

[[nodiscard]] Options parse_options(int argc, char** argv) {
    Options options;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        auto require_value = [&](const char* flag) -> std::string {
            if (i + 1 >= argc) {
                throw std::runtime_error(std::string("missing value after ") + flag);
            }
            return argv[++i];
        };
        if (arg == "--max-n") {
            options.max_n = std::stoi(require_value("--max-n"));
        } else if (arg == "--depth") {
            options.depth = std::stoi(require_value("--depth"));
        } else if (arg == "--csv") {
            options.csv_path = require_value("--csv");
        } else if (arg == "--verify-oeis") {
            options.verify_oeis = true;
        } else if (arg == "--help" || arg == "-h") {
            std::cout
                << "Usage: disk_polyomino [--max-n N] [--depth 1|2] [--csv FILE] [--verify-oeis]\n\n"
                << "depth 1: +1 square from accepted level n-1\n"
                << "depth 2: union of +1 from accepted n-1 and +2 from accepted n-2\n";
            std::exit(0);
        } else {
            throw std::runtime_error("unknown option: " + arg);
        }
    }
    if (options.max_n < 1) {
        throw std::runtime_error("--max-n must be positive");
    }
    if (options.depth != 1 && options.depth != 2) {
        throw std::runtime_error("--depth must be 1 or 2");
    }
    return options;
}

void write_header(std::ostream& out) {
    out << "n,accepted_prev,accepted_prev2,plus1_candidates,plus2_candidates,"
           "candidate_union,lattice_convex,accepted,seconds\n";
}

void write_row_csv(std::ostream& out, const Row& row) {
    out << row.n << ',' << row.accepted_prev << ',' << row.accepted_prev2 << ','
        << row.one_step << ',' << row.two_step << ',' << row.candidates << ','
        << row.lattice_convex << ',' << row.accepted << ',' << row.seconds << '\n';
}

int main(int argc, char** argv) {
    try {
        const Options options = parse_options(argc, argv);
        std::ofstream csv;
        if (!options.csv_path.empty()) {
            csv.open(options.csv_path);
            if (!csv) {
                throw std::runtime_error("cannot open CSV output: " + options.csv_path);
            }
            write_header(csv);
        }

        PolySet prev2;
        PolySet prev1{{Poly{{0, 0}}}};
        std::vector<std::size_t> counts{0, 1};  // index 0 is unused.

        std::cout << "n  prev  prev2  +1-candidates  +2-candidates  union  convex  accepted  seconds\n";
        const Row first{1, 0, 0, 1, 0, 1, 1, 1, 0.0};
        std::cout << " 1     0      0              1              0      1       1         1   0.0000\n";
        if (csv) {
            write_row_csv(csv, first);
        }

        for (int n = 2; n <= options.max_n; ++n) {
            const auto started = std::chrono::steady_clock::now();
            PolySet candidates = one_square_extensions(prev1);
            const std::size_t plus1_count = candidates.size();
            std::size_t plus2_count = 0;
            if (options.depth == 2 && n >= 3) {
                const PolySet plus2 = two_square_extensions(prev2);
                plus2_count = plus2.size();
                candidates.insert(plus2.begin(), plus2.end());
            }

            PolySet accepted;
            std::size_t convex_count = 0;
            for (const Poly& candidate : candidates) {
                if (!lattice_convex(candidate)) {
                    continue;
                }
                ++convex_count;
                if (accepts_by_boundary_pairs(candidate)) {
                    accepted.insert(candidate);
                }
            }

            const double seconds = std::chrono::duration<double>(
                std::chrono::steady_clock::now() - started
            ).count();
            const Row row{
                n,
                prev1.size(),
                prev2.size(),
                plus1_count,
                plus2_count,
                candidates.size(),
                convex_count,
                accepted.size(),
                seconds
            };
            std::cout << std::setw(2) << row.n
                      << std::setw(6) << row.accepted_prev
                      << std::setw(7) << row.accepted_prev2
                      << std::setw(15) << row.one_step
                      << std::setw(15) << row.two_step
                      << std::setw(7) << row.candidates
                      << std::setw(8) << row.lattice_convex
                      << std::setw(10) << row.accepted
                      << std::fixed << std::setprecision(4) << std::setw(9) << row.seconds
                      << '\n';
            if (csv) {
                write_row_csv(csv, row);
            }

            prev2 = std::move(prev1);
            prev1 = std::move(accepted);
            counts.push_back(prev1.size());
        }

        if (options.verify_oeis) {
            if (options.max_n > 21) {
                throw std::runtime_error("OEIS verification is available only through n=21");
            }
            for (int n = 1; n <= options.max_n; ++n) {
                const std::size_t expected = static_cast<std::size_t>(kOeis1To21[n - 1]);
                if (counts[n] != expected) {
                    std::ostringstream message;
                    message << "OEIS mismatch at n=" << n << ": got " << counts[n]
                            << ", expected " << expected;
                    throw std::runtime_error(message.str());
                }
            }
            std::cout << "OEIS A147680 prefix verified through n=" << options.max_n
                      << " (depth " << options.depth << ").\n";
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 2;
    }
}
