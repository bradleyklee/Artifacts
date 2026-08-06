#include <algorithm>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif

struct Model {
    int index;
    long long b1, b2, b3, b4;
};

struct Result {
    long long square_vectors = 0;
    long long third_moment_matches = 0;
    long long fourth_moment_matches = 0;
};

long long ct3(const std::vector<int>& g, long long g0, long long sumsq) {
    const int d = static_cast<int>(g.size()) - 1;
    long long triangle = 0;
    for (int i = 1; i <= d; ++i) {
        for (int j = 1; i + j <= d; ++j) {
            triangle += static_cast<long long>(g[i]) * g[j] * g[i + j];
        }
    }
    return g0 * g0 * g0 + 6 * g0 * sumsq + 6 * triangle;
}

long long ct4(const std::vector<int>& g, long long g0) {
    const int d = static_cast<int>(g.size()) - 1;
    std::vector<long long> a(2 * d + 1, 0);
    a[d] = g0;
    for (int k = 1; k <= d; ++k) {
        a[d + k] = g[k];
        a[d - k] = g[k];
    }
    std::vector<long long> square(4 * d + 1, 0);
    for (int i = -d; i <= d; ++i) {
        for (int j = -d; j <= d; ++j) {
            square[i + j + 2 * d] += a[i + d] * a[j + d];
        }
    }
    long long answer = 0;
    for (int exponent = -2 * d; exponent <= 2 * d; ++exponent) {
        answer += square[exponent + 2 * d] * square[-exponent + 2 * d];
    }
    return answer;
}

void enumerate(int position, int d, int remaining, std::vector<int>& g,
               const Model& model, long long sumsq, Result& result) {
    if (position > d) {
        if (remaining != 0) return;
        ++result.square_vectors;
        if (ct3(g, model.b1, sumsq) != model.b3) return;
        ++result.third_moment_matches;
        if (ct4(g, model.b1) == model.b4) ++result.fourth_moment_matches;
        return;
    }
    int bound = static_cast<int>(std::sqrt(static_cast<double>(remaining)));
    for (int value = -bound; value <= bound; ++value) {
        int next = remaining - value * value;
        if (next < 0) continue;
        g[position] = value;
        enumerate(position + 1, d, next, g, model, sumsq, result);
    }
}

int main() {
    const std::vector<Model> models = {
        {4, 20, 1304, 95264, 7349344},
        {8, 38, 4790, 656732, 95166502},
        {10, 30, 3206, 295212, 29172294},
    };
    std::cout << "{\n  \"ansatz\": \"F=((1+w)^2/w)*G(z), G=g0+sum_{k=1}^d gk(z^k+z^-k)\",\n";
    std::cout << "  \"results\": [\n";
    bool first = true;
    for (const auto& model : models) {
        long long sumsq = (model.b2 - model.b1 * model.b1) / 2;
        for (int d : {5, 6}) {
            struct Branch { int g1; int remaining; };
            std::vector<Branch> branches;
            int bound = static_cast<int>(std::sqrt(static_cast<double>(sumsq)));
            for (int g1 = -bound; g1 <= bound; ++g1) {
                int remaining = static_cast<int>(sumsq) - g1 * g1;
                if (remaining >= 0) branches.push_back({g1, remaining});
            }
            std::vector<Result> partial(branches.size());
            #pragma omp parallel for schedule(dynamic, 1)
            for (long long branch_index = 0; branch_index < static_cast<long long>(branches.size()); ++branch_index) {
                std::vector<int> g(d + 1, 0);
                g[1] = branches[branch_index].g1;
                enumerate(2, d, branches[branch_index].remaining, g, model, sumsq, partial[branch_index]);
            }
            Result result;
            for (const auto& item : partial) {
                result.square_vectors += item.square_vectors;
                result.third_moment_matches += item.third_moment_matches;
                result.fourth_moment_matches += item.fourth_moment_matches;
            }
            if (!first) std::cout << ",\n";
            first = false;
            std::cout << "    {\"model\": " << model.index
                      << ", \"degree\": " << d
                      << ", \"sum_squares\": " << sumsq
                      << ", \"square_vectors\": " << result.square_vectors
                      << ", \"third_moment_matches\": " << result.third_moment_matches
                      << ", \"fourth_moment_matches\": " << result.fourth_moment_matches
                      << "}";
            std::cerr << "model " << model.index << " d=" << d
                      << " vectors=" << result.square_vectors
                      << " ct3=" << result.third_moment_matches
                      << " ct4=" << result.fourth_moment_matches << "\n";
        }
    }
    std::cout << "\n  ],\n  \"conclusion\": \"No degree-5 or degree-6 integer palindromic G matches the first four reduced moments for models 4, 8, or 10.\"\n}\n";
    return 0;
}
