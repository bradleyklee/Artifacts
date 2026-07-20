#!/usr/bin/env julia
# Independent Julia re-verification of the A120593 quadtree certificate
# (Artifact 21 / a120593_quadtree_certificate_zine_spread).
#
# Pure Base Julia, exact rational/big-integer arithmetic throughout.
# No SymPy/Nemo/Symbolics dependency, so this runs on a stock Julia
# install with nothing extra to `Pkg.add`.
#
# What this does NOT do: parse the PDF itself or OCR the rendered pages.
# It takes the certificate's claimed formulas (transcribed by hand from
# payload/certificate.json, values given inline below) and independently
# recomputes every mathematical consequence from scratch. Cross-layer
# (surface-vs-payload LaTeX) checking was done separately in Python since
# it's a string/text-extraction task, not a numerical one; see the
# accompanying report for those results.
#
# Usage:  julia verify_A120593.jl

using Printf

# ---------------------------------------------------------------------
# Dense polynomial in one variable u, coefficients as Rational{BigInt},
# coeff[i] = coefficient of u^(i-1)  (1-indexed Julia arrays).
# ---------------------------------------------------------------------

const RB = Rational{BigInt}
const Poly = Vector{RB}

function ptrim(a::Poly)
    n = length(a)
    while n > 1 && a[n] == 0
        n -= 1
    end
    return a[1:n]
end

function padd(a::Poly, b::Poly)
    n = max(length(a), length(b))
    out = zeros(RB, n)
    @inbounds for i in 1:length(a); out[i] += a[i]; end
    @inbounds for i in 1:length(b); out[i] += b[i]; end
    return out
end

pneg(a::Poly) = RB[-x for x in a]
psub(a::Poly, b::Poly) = padd(a, pneg(b))
pscale(a::Poly, c) = RB[x*c for x in a]

function pmul(a::Poly, b::Poly)
    out = zeros(RB, length(a) + length(b) - 1)
    @inbounds for i in eachindex(a)
        ai = a[i]
        ai == 0 && continue
        for j in eachindex(b)
            out[i+j-1] += ai * b[j]
        end
    end
    return out
end

function ppow(a::Poly, k::Integer)
    out = Poly([RB(1)])
    for _ in 1:k
        out = pmul(out, a)
    end
    return out
end

# multiply by u^k (left-shift)
ushift(a::Poly, k::Integer) = k == 0 ? a : vcat(zeros(RB, k), a)

function pderiv(a::Poly)
    length(a) <= 1 && return Poly([RB(0)])
    return RB[a[i+1]*i for i in 1:length(a)-1]
end

is_zero_poly(a::Poly) = all(iszero, a)

function eval_poly(a::Poly, x)
    s = zero(x)
    for c in reverse(a)
        s = s*x + c
    end
    return s
end

# ---------------------------------------------------------------------
# The certificate's claimed data (transcribed from payload/certificate.json)
# ---------------------------------------------------------------------

# D(u) = 1 - 6u - 4u^2 - u^3
const Dpoly = Poly([RB(1), RB(-6), RB(-4), RB(-1)])

# N(n,u) coefficients, keyed by power of n, each a length-10 vector (u^0..u^9)
const N_by_n_degree = Dict(
    2 => RB[-491, 6396, 204, -8524, -5136, 2784, 4496, 2304, 576, 64],
    1 => RB[-491, 6648, -948, -11872, -6228, 5784, 7988, 4032, 1008, 112],
    0 => RB[0, 0, 40, -440, 640, 2960, 2960, 1440, 360, 40],
)

function Ppolys(n::Integer)
    P0 = -8*(4n+5)*(2n+1)*(4n-1)
    P1 = -64*(n+1)*(48n^2+96n+43)
    P2 = -6144*(2n+3)*(n+2)*(n+1)
    P3 = 491*(n+3)*(n+2)*(n+1)
    return (P0, P1, P2, P3)
end

function N_of_n(n::Integer)
    out = zeros(RB, 10)
    for (d, coeffs) in N_by_n_degree
        for (e, c) in enumerate(coeffs)   # e-1 is the u power
            out[e] += c * RB(n)^d
        end
    end
    return out
end

# ---------------------------------------------------------------------
# Check 1: multinomial closed form reproduces the claimed initial values
#   a(n) = sum_{i,j,k>=0, i+2j+3k=n-1} (n+i+j+k-1)! 6^i 4^j / (n! i! j! k!)
# ---------------------------------------------------------------------

function q_multinomial(n::Integer)
    n == 0 && return BigInt(1)
    total = BigInt(0)
    for i in 0:n+1, j in 0:n+1, k in 0:n+1
        if i + 2j + 3k == n - 1
            m = n + i + j + k
            total += factorial(BigInt(m-1)) * BigInt(6)^i * BigInt(4)^j ÷
                     (factorial(BigInt(n)) * factorial(BigInt(i)) * factorial(BigInt(j)) * factorial(BigInt(k)))
        end
    end
    return total
end

function check_multinomial()
    claimed = BigInt[1, 1, 6, 76, 1201, 21252]
    computed = [q_multinomial(n) for n in 0:5]
    ok = computed == claimed
    println("[check 1] multinomial closed form vs claimed q_0..q_5")
    println("          computed: ", computed)
    println("          claimed:  ", claimed)
    println("          PASS = ", ok)
    return ok, computed
end

# ---------------------------------------------------------------------
# Check 2: P-recurrence  sum_{r=0}^3 P_r(n) q_{n+r} = 0  holds exactly
# for many n, using the multinomial values (extended beyond n=5).
# ---------------------------------------------------------------------

function q_multinomial_range(nmax::Integer)
    return [q_multinomial(n) for n in 0:nmax]
end

function check_recurrence(nmax::Integer=14)
    q = q_multinomial_range(nmax)
    ok = true
    for n in 0:(nmax-3)
        P = Ppolys(n)
        lhs = sum(P[r+1]*q[n+r+1] for r in 0:3)
        if lhs != 0
            ok = false
            println("          FAIL at n=$n: residual = $lhs")
        end
    end
    println("[check 2] P-recurrence holds exactly for n = 0..$(nmax-3): PASS = ", ok)
    return ok
end

# ---------------------------------------------------------------------
# Check 3: algebraic generating equation  5A(x) = 4 + x + A(x)^4,
# A = 1+Q, via formal power series (fixed-point iteration on Q).
# ---------------------------------------------------------------------

# Power series as Poly, truncated to length `ordr` (coeff of x^0..x^(ordr-1)).
function series_trunc(a::Poly, ordr::Integer)
    n = min(length(a), ordr)
    out = zeros(RB, ordr)
    out[1:n] .= a[1:n]
    return out
end

function series_mul(a::Poly, b::Poly, ordr::Integer)
    return series_trunc(pmul(a,b), ordr)
end

function series_pow(a::Poly, k::Integer, ordr::Integer)
    out = series_trunc(Poly([RB(1)]), ordr)
    for _ in 1:k
        out = series_mul(out, a, ordr)
    end
    return out
end

function compute_Q_series(ordr::Integer)
    # Q = x + 6Q^2 + 4Q^3 + Q^4, solved by fixed-point iteration (each pass
    # gains at least one more correct order since the RHS's linear part in Q
    # beyond the seed x is higher order).
    Q = zeros(RB, ordr)
    for _ in 1:(ordr+2)
        Q2 = series_mul(Q, Q, ordr)
        Q3 = series_mul(Q2, Q, ordr)
        Q4 = series_mul(Q3, Q, ordr)
        x = zeros(RB, ordr); if ordr >= 2; x[2] = RB(1); end
        Q = series_trunc(padd(padd(x, pscale(Q2, RB(6))), padd(pscale(Q3, RB(4)), Q4)), ordr)
    end
    return Q
end

function check_algebraic(ordr::Integer=14)
    Q = compute_Q_series(ordr)
    A = padd(Q, Poly([RB(1)]))  # A = 1 + Q
    A = series_trunc(A, ordr)
    # 5A - 4 - x - A^4 should be the zero series
    A4 = series_pow(A, 4, ordr)
    x = zeros(RB, ordr); if ordr >= 2; x[2] = RB(1); end
    residual = series_trunc(psub(psub(pscale(A, RB(5)), padd(Poly([RB(4)]), x)), A4), ordr)
    ok = is_zero_poly(residual)
    # also cross-check against the multinomial values
    qvals = [Q[n+1] for n in 1:min(5, ordr-1)]
    claimed = RB[1, 6, 76, 1201, 21252][1:length(qvals)]
    ok2 = qvals == claimed
    println("[check 3] algebraic equation 5A = 4+x+A^4 holds as a power series to order $(ordr-1): PASS = ", ok)
    println("          Q coefficients vs multinomial values agree: PASS = ", ok2)
    return ok && ok2
end

# ---------------------------------------------------------------------
# Check 4: differential equation for A(x), verified against the same
# independently-derived power series (not assumed equivalent by fiat).
# ---------------------------------------------------------------------

function check_differential(ordr::Integer=16)
    Q = compute_Q_series(ordr)
    A = series_trunc(padd(Q, Poly([RB(1)])), ordr)
    dA  = pderiv(A)
    d2A = pderiv(dA)
    d3A = pderiv(d2A)
    x = zeros(RB, ordr); if ordr >= 2; x[2] = RB(1); end

    c3 = series_trunc(padd(padd(pscale(x,RB(0)), Poly([RB(-491)])), padd(pscale(x, RB(12288)), padd(pscale(pmul(x,x), RB(3072)), pscale(pmul(pmul(x,x),x), RB(256))))), ordr)
    c2 = series_trunc(padd(Poly([RB(18432)]), padd(pscale(x, RB(9216)), pscale(pmul(x,x), RB(1152)))), ordr)
    c1 = series_trunc(padd(Poly([RB(2752)]), pscale(x, RB(688))), ordr)

    lhs = padd(padd(series_mul(c3, d3A, ordr), series_mul(c2, d2A, ordr)),
               padd(series_mul(c1, dA, ordr), pscale(A, RB(-40))))
    residual = series_trunc(lhs, ordr - 4)  # last few orders are edge effects of finite differentiation window
    ok = is_zero_poly(residual)
    println("[check 4] differential operator holds against the independently-derived A(x) series to order $(ordr-5): PASS = ", ok)
    return ok
end

# ---------------------------------------------------------------------
# Check 5: creative-telescoping identity
#   sum_{r=0}^3 P_r(n) H_{n+r}(u) = d/du( R(n,u) H_n(u) )
# where H_m(u) = 1/(m u^m D(u)^m), verified as an EXACT rational-function
# identity in u (cross-multiplied to clear denominators; no numerical
# approximation) for each of several concrete integer n.
# ---------------------------------------------------------------------

function check_telescoping(nrange=1:8)
    ok_all = true
    for n in nrange
        P0,P1,P2,P3 = Ppolys(n)
        P = (P0,P1,P2,P3)

        # LHS * u^(n+3) D^(n+3) = sum_r [P_r/(n+r)] u^(3-r) D^(3-r)   (a polynomial)
        lhs_num = zeros(RB, 1)
        for r in 0:3
            term = pscale(pmul(ushift(Poly([RB(1)]), 3-r), ppow(Dpoly, 3-r)), RB(P[r+1], n+r))
            lhs_num = padd(lhs_num, term)
        end
        lhs_den = pmul(ushift(Poly([RB(1)]), n+3), ppow(Dpoly, n+3))

        # RHS = d/du(f/g),  f = N(n,u),  g = n u^(n+2) D(u)^(n+2)
        f = N_of_n(n)
        g = pscale(pmul(ushift(Poly([RB(1)]), n+2), ppow(Dpoly, n+2)), RB(n))
        fprime = pderiv(f)
        gprime = pderiv(g)
        rhs_num = psub(pmul(fprime, g), pmul(f, gprime))
        rhs_den = pmul(g, g)

        diff = psub(pmul(lhs_num, rhs_den), pmul(rhs_num, lhs_den))
        ok = is_zero_poly(ptrim(diff))
        ok_all &= ok
        @printf("          n=%d: identity holds exactly = %s\n", n, ok)
    end
    println("[check 5] creative-telescoping identity over Q(n,u), n in $(nrange): PASS = ", ok_all)
    return ok_all
end

# ---------------------------------------------------------------------

function main()
    println("Independent Julia verification of A120593 certificate (Artifact 21)")
    println("="^72)
    r1, _ = check_multinomial()
    r2 = check_recurrence()
    r3 = check_algebraic()
    r4 = check_differential()
    r5 = check_telescoping()
    println("="^72)
    allok = r1 && r2 && r3 && r4 && r5
    println("ALL CHECKS PASS: ", allok)
    return allok
end

main()
