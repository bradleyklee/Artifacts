package verification

import (
	"fmt"
	"os"
	"runtime"
	"sort"
	"strconv"
	"sync"
	"testing"

	sl "verifiedskiplist/implementation/skiplist"
)

const rankStep int64 = 1 << 50

func int64Order(a, b int64) int {
	switch {
	case a < b:
		return 1
	case a > b:
		return -1
	default:
		return 0
	}
}

func insertionValue(s *sl.List[int, int64], pos int) int64 {
	e := s.EntriesAt(1)
	switch {
	case len(e) == 0:
		return 0
	case pos == 0:
		return e[0].Value - rankStep
	case pos == len(e):
		return e[len(e)-1].Value + rankStep
	default:
		a, b := e[pos-1].Value, e[pos].Value
		if b-a <= 1 {
			panic("verification rank spacing exhausted")
		}
		return a + (b-a)/2
	}
}

func graphMaxN() int {
	n := 24
	if s := os.Getenv("SKIPLIST_GRAPH_MAX_N"); s != "" {
		if x, e := strconv.Atoi(s); e == nil && x >= 0 {
			n = x
		}
	}
	return n
}

func graphWorkers() int {
	n := runtime.GOMAXPROCS(0)
	if s := os.Getenv("SKIPLIST_GRAPH_WORKERS"); s != "" {
		if x, e := strconv.Atoi(s); e == nil && x > 0 {
			n = x
		}
	}
	if n < 1 {
		return 1
	}
	return n
}

type graphStat struct {
	N, States, MaxDepth, InsertOps, InsertEdges, DeleteOps, DeleteEdges, DeleteImage int
}

type insAccum struct {
	next     map[string]*sl.List[int, int64]
	edges    map[string]struct{}
	branches map[string]int
	err      error
}

type delAccum struct {
	image    map[string]struct{}
	edges    map[string]struct{}
	branches map[string]int
	ops      int
	maxDepth int
	err      error
}

func addCounts(dst, src map[string]int) {
	for k, v := range src {
		dst[k] += v
	}
}

func insertionPhase(level map[string]*sl.List[int, int64], n, workers int) (map[string]*sl.List[int, int64], map[string]struct{}, map[string]int, error) {
	type job struct {
		from string
		base *sl.List[int, int64]
	}
	jobs := make(chan job)
	out := make(chan insAccum, workers)
	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			a := insAccum{next: map[string]*sl.List[int, int64]{}, edges: map[string]struct{}{}, branches: map[string]int{}}
			for j := range jobs {
				for pos := 0; pos <= n; pos++ {
					x := j.base.CloneForVerification()
					x.SetVerificationTrace(func(ev string) { a.branches[ev]++ })
					v := insertionValue(j.base, pos)
					if !x.Insert(n, v) {
						a.err = fmt.Errorf("n=%d pos=%d replacement", n, pos)
						out <- a
						return
					}
					if err := x.Validate(); err != nil {
						a.err = fmt.Errorf("insert n=%d pos=%d: %w", n, pos, err)
						out <- a
						return
					}
					sig := x.ShapeSignature()
					if _, ok := a.next[sig]; !ok {
						x.SetVerificationTrace(nil)
						a.next[sig] = x
					}
					a.edges[j.from+"=>"+sig] = struct{}{}
				}
			}
			out <- a
		}()
	}
	go func() {
		for from, base := range level {
			jobs <- job{from, base}
		}
		close(jobs)
		wg.Wait()
		close(out)
	}()
	next := map[string]*sl.List[int, int64]{}
	edges := map[string]struct{}{}
	branches := map[string]int{}
	var firstErr error
	for a := range out {
		if firstErr == nil && a.err != nil {
			firstErr = a.err
		}
		for sig, rep := range a.next {
			if _, ok := next[sig]; !ok {
				next[sig] = rep
			}
		}
		for e := range a.edges {
			edges[e] = struct{}{}
		}
		addCounts(branches, a.branches)
	}
	return next, edges, branches, firstErr
}

func deletionPhase(level, previous map[string]*sl.List[int, int64], n, workers int) (map[string]struct{}, map[string]struct{}, map[string]int, int, int, error) {
	type job struct {
		from string
		base *sl.List[int, int64]
	}
	jobs := make(chan job)
	out := make(chan delAccum, workers)
	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			a := delAccum{image: map[string]struct{}{}, edges: map[string]struct{}{}, branches: map[string]int{}}
			for j := range jobs {
				if j.base.Depth() > a.maxDepth {
					a.maxDepth = j.base.Depth()
				}
				entries := j.base.EntriesAt(1)
				for pos := range entries {
					x := j.base.CloneForVerification()
					x.SetVerificationTrace(func(ev string) { a.branches[ev]++ })
					if !x.Delete(entries[pos].Key) {
						a.err = fmt.Errorf("delete n=%d pos=%d missing", n, pos)
						out <- a
						return
					}
					a.ops++
					if err := x.Validate(); err != nil {
						a.err = fmt.Errorf("delete n=%d pos=%d: %w", n, pos, err)
						out <- a
						return
					}
					sig := x.ShapeSignature()
					if _, ok := previous[sig]; !ok {
						a.err = fmt.Errorf("closure %d->%d unknown shape %s", n, n-1, sig)
						out <- a
						return
					}
					a.image[sig] = struct{}{}
					a.edges[j.from+"=>"+sig] = struct{}{}
				}
			}
			out <- a
		}()
	}
	go func() {
		for from, base := range level {
			jobs <- job{from, base}
		}
		close(jobs)
		wg.Wait()
		close(out)
	}()
	image := map[string]struct{}{}
	edges := map[string]struct{}{}
	branches := map[string]int{}
	ops := 0
	maxDepth := 0
	var firstErr error
	for a := range out {
		if firstErr == nil && a.err != nil {
			firstErr = a.err
		}
		for s := range a.image {
			image[s] = struct{}{}
		}
		for e := range a.edges {
			edges[e] = struct{}{}
		}
		addCounts(branches, a.branches)
		ops += a.ops
		if a.maxDepth > maxDepth {
			maxDepth = a.maxDepth
		}
	}
	return image, edges, branches, ops, maxDepth, firstErr
}

func buildGradedGraph(t *testing.T, maxN int) []graphStat {
	t.Helper()
	workers := graphWorkers()
	levels := make([]map[string]*sl.List[int, int64], maxN+1)
	empty := sl.New[int, int64](int64Order)
	levels[0] = map[string]*sl.List[int, int64]{empty.ShapeSignature(): empty}
	stats := []graphStat{{N: 0, States: 1}}
	branches := map[string]int{}
	t.Logf("graded graph workers=%d", workers)
	for n := 0; n < maxN; n++ {
		next, insEdges, ib, err := insertionPhase(levels[n], n, workers)
		if err != nil {
			t.Fatal(err)
		}
		addCounts(branches, ib)
		levels[n+1] = next
		image, delEdges, db, delOps, maxDepth, err := deletionPhase(next, levels[n], n+1, workers)
		if err != nil {
			t.Fatal(err)
		}
		addCounts(branches, db)
		if len(image) != len(levels[n]) {
			missing := []string{}
			for sig := range levels[n] {
				if _, ok := image[sig]; !ok {
					missing = append(missing, sig)
				}
			}
			sort.Strings(missing)
			t.Fatalf("delete image %d->%d %d/%d missing=%v", n+1, n, len(image), len(levels[n]), missing)
		}
		st := graphStat{N: n + 1, States: len(next), MaxDepth: maxDepth, InsertOps: len(levels[n]) * (n + 1), InsertEdges: len(insEdges), DeleteOps: delOps, DeleteEdges: len(delEdges), DeleteImage: len(image)}
		stats = append(stats, st)
		t.Logf("n=%d states=%d depth<=%d insert_ops=%d insert_edges=%d delete_ops=%d delete_edges=%d delete_image=%d/%d PASS", st.N, st.States, st.MaxDepth, st.InsertOps, st.InsertEdges, st.DeleteOps, st.DeleteEdges, st.DeleteImage, len(levels[n]))
	}
	for _, name := range []string{"D1_RECURSE", "D1_MERGE", "D2_TOP", "D2_MERGE_RIGHT", "D2_MERGE_LEFT", "D2_RECURSE_RIGHT", "D2_RECURSE_LEFT", "D3_SHIFT_RIGHT", "D4_LOCAL", "D5_LOCAL"} {
		if branches[name] == 0 {
			t.Fatalf("closure branch not exercised: %s", name)
		}
	}
	t.Logf("closure branches=%v", branches)
	return stats
}

func TestGradedTransitionGraph(t *testing.T) { buildGradedGraph(t, graphMaxN()) }

func TestShapeSignatureIgnoresKeyNames(t *testing.T) {
	a := sl.New[int, int](intOrder)
	b := sl.New[int, int](intOrder)
	for i, v := range []int{30, 10, 20, 40} {
		a.Insert(i, v)
	}
	for i, v := range []int{30, 10, 20, 40} {
		b.Insert(100+i, v)
	}
	if a.ShapeSignature() != b.ShapeSignature() {
		t.Fatalf("shape depends on keys: %s vs %s", a.ShapeSignature(), b.ShapeSignature())
	}
}
