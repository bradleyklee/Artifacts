# Wide-regime benchmark pseudocode

```text
GENERATE_GRID:
    FOR c3 in {1/2,1,2}:
        FOR c4 in {1/8,1/4,1/2}:
            emit 2H = p^2+q^2+c3*Re(q+i p)^3+c4*Re(q+i p)^4
    FOR c4 in {1/8,1/4,1/2}:
        emit pure-square controls
    FOR c6 in {1/8,1/4,1/2}:
        emit pure-hexagon controls

BENCHMARK_CASE(case):
    run Lairez-style port in a fresh process with a hard timeout
    record discovered order, normalized operator, map ranks, and wall time

    run bare Klee exact-image solver in a fresh process
    start with the degree/symmetry support policy, not a candidate operator
    record closure/failure, support bound, matrix dimensions, primitive terms,
           exact residual, and wall time

    IF both close:
        compare normalized operator coefficient lists exactly
    ELSE:
        record the bounded failure or timeout without extrapolation

    checkpoint JSON after every case

REFINE_SUPPORT(case, failed_bound, successful_bound):
    test the midpoint bound
    retain the smallest tested successful bound and largest tested failure
    do not call the threshold a theorem until every intermediate bound or a
    monotonicity argument has been checked
```

The harness is sequential by default. Parallel symbolic runs would contaminate
wall-time comparisons through CPU and memory contention.
