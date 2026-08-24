package main

import (
    "fmt"
    "time"
)

func benchMixedSkip(n, q, page, trials int) time.Duration {
    samples := make([]time.Duration, trials)
    for t := 0; t < trials; t++ {
        s := buildSkip(n)
        start := time.Now()
        for qn := 0; qn < q; qn++ {
            id := qn % n
            sc := scoreFor(id, qn+1000)
            s.mem[id] = Memory{ID:id, Score:sc}
            s.idx.Insert(id, Rank{Score:sc, ID:id})
        }
        k:=page; if k>n { k=n }
        for j:=0;j<k;j++ { r,_:=s.idx.PopFirst(); delete(s.mem,r.ID) }
        samples[t]=time.Since(start)
    }
    return median(samples)
}
func benchMixedMap(n, q, page, trials int) time.Duration {
    samples := make([]time.Duration, trials)
    for t := 0; t < trials; t++ {
        m:=buildMap(n)
        start:=time.Now()
        for qn:=0; qn<q; qn++ { id:=qn%n; m[id]=Memory{ID:id,Score:scoreFor(id,qn+1000)} }
        ranks:=sortedRanks(m)
        k:=page; if k>n { k=n }
        for _,r:=range ranks[:k] { delete(m,r.ID) }
        samples[t]=time.Since(start)
    }
    return median(samples)
}
func init(){ _ = fmt.Sprintf }
