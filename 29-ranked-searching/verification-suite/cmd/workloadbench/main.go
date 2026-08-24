package main

import (
    "fmt"
    "runtime"
    "sort"
    "time"

    sl "verifiedskiplist/implementation/skiplist"
)

type Memory struct {
    ID    int
    Score int64
}

type Rank struct {
    Score int64
    ID    int
}

func rankOrder(a, b Rank) int {
    switch {
    case a.Score > b.Score:
        return 1
    case a.Score < b.Score:
        return -1
    case a.ID < b.ID:
        return 1
    case a.ID > b.ID:
        return -1
    default:
        return 0
    }
}

func scoreFor(id, salt int) int64 {
    // Deterministic, cheap, well-mixed enough to avoid sorted insertion order.
    x := uint64(id+1)*0x9e3779b97f4a7c15 + uint64(salt)*0xbf58476d1ce4e5b9
    x ^= x >> 30
    x *= 0xbf58476d1ce4e5b9
    x ^= x >> 27
    x *= 0x94d049bb133111eb
    x ^= x >> 31
    return int64(x & 0x7fffffffffffffff)
}

type skipStore struct {
    mem map[int]Memory
    idx *sl.List[int, Rank]
}

func buildSkip(n int) *skipStore {
    s := &skipStore{mem: make(map[int]Memory, n), idx: sl.New[int, Rank](rankOrder)}
    for id := 0; id < n; id++ {
        sc := scoreFor(id, 0)
        s.mem[id] = Memory{ID: id, Score: sc}
        s.idx.Insert(id, Rank{Score: sc, ID: id})
    }
    return s
}

func buildMap(n int) map[int]Memory {
    m := make(map[int]Memory, n)
    for id := 0; id < n; id++ {
        sc := scoreFor(id, 0)
        m[id] = Memory{ID: id, Score: sc}
    }
    return m
}

func median(ds []time.Duration) time.Duration {
    sort.Slice(ds, func(i, j int) bool { return ds[i] < ds[j] })
    return ds[len(ds)/2]
}

func benchInsertSkip(n, trials, batches, batch int) time.Duration {
    samples := make([]time.Duration, trials)
    for t := 0; t < trials; t++ {
        s := buildSkip(n)
        var total time.Duration
        next := n
        for r := 0; r < batches; r++ {
            start := time.Now()
            for j := 0; j < batch; j++ {
                id := next + j
                sc := scoreFor(id, r+1)
                s.mem[id] = Memory{ID: id, Score: sc}
                s.idx.Insert(id, Rank{Score: sc, ID: id})
            }
            total += time.Since(start)
            for j := 0; j < batch; j++ {
                id := next + j
                delete(s.mem, id)
                s.idx.Delete(id)
            }
            next += batch
        }
        samples[t] = total / time.Duration(batches*batch)
    }
    return median(samples)
}

func benchInsertMap(n, trials, batches, batch int) time.Duration {
    samples := make([]time.Duration, trials)
    for t := 0; t < trials; t++ {
        m := buildMap(n)
        var total time.Duration
        next := n
        for r := 0; r < batches; r++ {
            start := time.Now()
            for j := 0; j < batch; j++ {
                id := next + j
                m[id] = Memory{ID: id, Score: scoreFor(id, r+1)}
            }
            total += time.Since(start)
            for j := 0; j < batch; j++ { delete(m, next+j) }
            next += batch
        }
        samples[t] = total / time.Duration(batches*batch)
    }
    return median(samples)
}

func benchUpdateSkip(n, trials, q int) time.Duration {
    samples := make([]time.Duration, trials)
    for t := 0; t < trials; t++ {
        s := buildSkip(n)
        start := time.Now()
        for qn := 0; qn < q; qn++ {
            id := qn % n
            sc := scoreFor(id, qn+1)
            s.mem[id] = Memory{ID: id, Score: sc}
            s.idx.Insert(id, Rank{Score: sc, ID: id})
        }
        samples[t] = time.Since(start) / time.Duration(q)
    }
    return median(samples)
}

func benchUpdateMap(n, trials, q int) time.Duration {
    samples := make([]time.Duration, trials)
    for t := 0; t < trials; t++ {
        m := buildMap(n)
        start := time.Now()
        for qn := 0; qn < q; qn++ {
            id := qn % n
            m[id] = Memory{ID: id, Score: scoreFor(id, qn+1)}
        }
        samples[t] = time.Since(start) / time.Duration(q)
    }
    return median(samples)
}

func sortedRanks(m map[int]Memory) []Rank {
    a := make([]Rank, 0, len(m))
    for id, mem := range m { a = append(a, Rank{Score: mem.Score, ID: id}) }
    sort.Slice(a, func(i, j int) bool {
        if a[i].Score != a[j].Score { return a[i].Score > a[j].Score }
        return a[i].ID < a[j].ID
    })
    return a
}

func benchPopSkip(n, trials, page int) time.Duration {
    samples := make([]time.Duration, trials)
    for t := 0; t < trials; t++ {
        s := buildSkip(n)
        start := time.Now()
        for s.idx.Len() > 0 {
            k := page
            if s.idx.Len() < k { k = s.idx.Len() }
            for j := 0; j < k; j++ {
                r, ok := s.idx.PopFirst()
                if !ok { panic("skip pop failed") }
                delete(s.mem, r.ID)
            }
        }
        samples[t] = time.Since(start)
    }
    return median(samples)
}

func benchPopMapSnapshot(n, trials, page int) time.Duration {
    samples := make([]time.Duration, trials)
    for t := 0; t < trials; t++ {
        m := buildMap(n)
        start := time.Now()
        ranks := sortedRanks(m)
        for i := 0; i < len(ranks); i += page {
            end := i + page
            if end > len(ranks) { end = len(ranks) }
            for _, r := range ranks[i:end] { delete(m, r.ID) }
        }
        samples[t] = time.Since(start)
    }
    return median(samples)
}

func benchPopMapResort(n, trials, page int) time.Duration {
    samples := make([]time.Duration, trials)
    for t := 0; t < trials; t++ {
        m := buildMap(n)
        start := time.Now()
        for len(m) > 0 {
            ranks := sortedRanks(m)
            k := page
            if len(ranks) < k { k = len(ranks) }
            for _, r := range ranks[:k] { delete(m, r.ID) }
        }
        samples[t] = time.Since(start)
    }
    return median(samples)
}

func benchOnePageSkip(n, trials, page int) time.Duration {
    samples := make([]time.Duration, trials)
    for t := 0; t < trials; t++ {
        s := buildSkip(n)
        start := time.Now()
        k := page
        if k > n { k = n }
        for j := 0; j < k; j++ {
            r, ok := s.idx.PopFirst()
            if !ok { panic("skip page pop failed") }
            delete(s.mem, r.ID)
        }
        samples[t] = time.Since(start)
        if err := s.idx.Validate(); err != nil { panic(err) }
    }
    return median(samples)
}

func benchOnePageMap(n, trials, page int) time.Duration {
    samples := make([]time.Duration, trials)
    for t := 0; t < trials; t++ {
        m := buildMap(n)
        start := time.Now()
        ranks := sortedRanks(m)
        k := page
        if k > len(ranks) { k = len(ranks) }
        for _, r := range ranks[:k] { delete(m, r.ID) }
        samples[t] = time.Since(start)
    }
    return median(samples)
}

func main() {
    fmt.Printf("go=%s cpu=%d\n", runtime.Version(), runtime.NumCPU())
    fmt.Println("times are medians; insert/update are ns per operation; pop is total drain and ns/item")
    fmt.Println()
    fmt.Printf("%-7s %-12s %-12s %-8s %-12s %-12s %-8s\n", "N", "insert_map", "insert_skip", "x", "update_map", "update_skip", "x")
    for _, n := range []int{10,100,1000,10000} {
        batch := 8
        if n >= 100 { batch = 16 }
        im := benchInsertMap(n, 7, 300, batch)
        is := benchInsertSkip(n, 7, 300, batch)
        q := 30000
        if n == 10000 { q = 20000 }
        um := benchUpdateMap(n, 7, q)
        us := benchUpdateSkip(n, 7, q)
        fmt.Printf("%-7d %-12s %-12s %-8.1f %-12s %-12s %-8.1f\n", n, im, is, float64(is)/float64(im), um, us, float64(us)/float64(um))
    }
    fmt.Println()
    fmt.Println("single top-page request: skip list pops K directly; map collects+sorts then pops K")
    for _, page := range []int{1,10,100} {
        fmt.Printf("page=%d\n", page)
        fmt.Printf("%-7s %-16s %-16s %-10s\n", "N", "skip_page", "map_sort_page", "map/skip")
        for _, n := range []int{10,100,1000,10000} {
            if page > n { continue }
            trials := 31
            if n >= 1000 { trials = 17 }
            if n == 10000 { trials = 9 }
            sp := benchOnePageSkip(n, trials, page)
            mp := benchOnePageMap(n, trials, page)
            fmt.Printf("%-7d %-16s %-16s %-10.1f\n", n, sp, mp, float64(mp)/float64(sp))
        }
        fmt.Println()
    }

    fmt.Println("mixed workload: Q rank updates, then pop top 10")
    fmt.Printf("%-7s %-7s %-16s %-16s %-10s\n", "N", "Q", "skip", "map+sort", "map/skip")
    for _, n := range []int{100,1000,10000} {
        for _, q := range []int{0,1,10,100,1000} {
            if q > n*2 { continue }
            trials := 21
            if n==10000 { trials=7 }
            ss:=benchMixedSkip(n,q,10,trials)
            mm:=benchMixedMap(n,q,10,trials)
            fmt.Printf("%-7d %-7d %-16s %-16s %-10.2f\n",n,q,ss,mm,float64(mm)/float64(ss))
        }
    }
    fmt.Println()

    fmt.Println("full drain / continuation policies")
    for _, page := range []int{1,10,100} {
        fmt.Printf("page=%d\n", page)
        fmt.Printf("%-7s %-16s %-16s %-16s %-10s %-10s\n", "N", "skip_drain", "map_snapshot", "map_resort", "skip/item", "snap/item")
        for _, n := range []int{10,100,1000,10000} {
            if page > n { continue }
            trials := 7
            if n == 10000 { trials = 5 }
            sd := benchPopSkip(n, trials, page)
            ms := benchPopMapSnapshot(n, trials, page)
            var mr time.Duration
            // Re-sorting every 1-item page at N=10000 is deliberately omitted;
            // it measures an obviously quadratic-ish serving policy rather than the structure.
            if !(n == 10000 && page == 1) {
                rt := trials
                if n >= 1000 { rt = 3 }
                mr = benchPopMapResort(n, rt, page)
            }
            mrstr := mr.String()
            if mr == 0 { mrstr = "(omitted)" }
            fmt.Printf("%-7d %-16s %-16s %-16s %-10s %-10s\n", n, sd, ms, mrstr, sd/time.Duration(n), ms/time.Duration(n))
        }
        fmt.Println()
    }
}
