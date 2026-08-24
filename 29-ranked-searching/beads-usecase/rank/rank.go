package rank

import (
	"hash/fnv"
	"math"
	"sort"
	"strings"

	"verifiedskiplist/beads-usecase/model"
)

type Graph struct {
	IDs []string
	Idx map[string]int
	Out [][]int
	In  [][]int
}

func BuildGraph(mem []model.Memory) Graph {
	g := Graph{IDs: make([]string, len(mem)), Idx: make(map[string]int, len(mem)), Out: make([][]int, len(mem)), In: make([][]int, len(mem))}
	for i := range mem {
		g.IDs[i] = mem[i].ID
		g.Idx[mem[i].ID] = i
	}
	for i := range mem {
		seen := map[int]bool{}
		for _, r := range mem[i].References {
			j, ok := g.Idx[r.TargetID]
			if !ok || j == i || seen[j] {
				continue
			}
			seen[j] = true
			g.Out[i] = append(g.Out[i], j)
			g.In[j] = append(g.In[j], i)
		}
	}
	return g
}

func PageRank(mem []model.Memory, damping float64, iterations int) map[string]float64 {
	return pageRankGraph(BuildGraph(mem), damping, iterations, "forward")
}

func ReversePageRank(mem []model.Memory, damping float64, iterations int) map[string]float64 {
	return pageRankGraph(BuildGraph(mem), damping, iterations, "reverse")
}

func UndirectedPageRank(mem []model.Memory, damping float64, iterations int) map[string]float64 {
	return pageRankGraph(BuildGraph(mem), damping, iterations, "undirected")
}

func pageRankGraph(g Graph, damping float64, iterations int, mode string) map[string]float64 {
	n := len(g.IDs)
	out := make(map[string]float64, n)
	if n == 0 {
		return out
	}
	edges := make([][]int, n)
	for i := 0; i < n; i++ {
		switch mode {
		case "forward":
			edges[i] = append(edges[i], g.Out[i]...)
		case "reverse":
			edges[i] = append(edges[i], g.In[i]...)
		case "undirected":
			seen := map[int]bool{}
			for _, j := range append(append([]int(nil), g.Out[i]...), g.In[i]...) {
				if j != i && !seen[j] {
					seen[j] = true
					edges[i] = append(edges[i], j)
				}
			}
		default:
			panic("rank: bad PageRank mode")
		}
	}
	p := make([]float64, n)
	for i := range p {
		p[i] = 1 / float64(n)
	}
	for it := 0; it < iterations; it++ {
		next := make([]float64, n)
		base := (1 - damping) / float64(n)
		for i := range next {
			next[i] = base
		}
		for i := range p {
			if len(edges[i]) == 0 {
				share := damping * p[i] / float64(n)
				for j := range next {
					next[j] += share
				}
				continue
			}
			share := damping * p[i] / float64(len(edges[i]))
			for _, j := range edges[i] {
				next[j] += share
			}
		}
		p = next
	}
	for i, id := range g.IDs {
		out[id] = p[i]
	}
	return out
}

func InDegree(mem []model.Memory) map[string]float64 {
	g := BuildGraph(mem)
	out := make(map[string]float64, len(mem))
	for i, id := range g.IDs {
		out[id] = float64(len(g.In[i]))
	}
	return out
}

func OutDegree(mem []model.Memory) map[string]float64 {
	g := BuildGraph(mem)
	out := make(map[string]float64, len(mem))
	for i, id := range g.IDs {
		out[id] = float64(len(g.Out[i]))
	}
	return out
}

// HITS returns GLOBAL authority and hub scores over the complete frozen corpus
// graph. This is intentionally not Kleinberg's query-time HITS retrieval
// pipeline: there is no query-selected root/base set here. The mutual update
// equations are the same, but the graph is fixed before any query arrives.
// It is useful here as a deliberately directional citation control: authorities
// are cited by strong hubs, while hubs cite strong authorities.
func HITS(mem []model.Memory, iterations int) (authority, hub map[string]float64) {
	g := BuildGraph(mem)
	n := len(g.IDs)
	a := make([]float64, n)
	h := make([]float64, n)
	for i := range a {
		a[i], h[i] = 1, 1
	}
	for it := 0; it < iterations; it++ {
		na, nh := make([]float64, n), make([]float64, n)
		for i := 0; i < n; i++ {
			for _, src := range g.In[i] {
				na[i] += h[src]
			}
			for _, dst := range g.Out[i] {
				nh[i] += a[dst]
			}
		}
		normalizeL2(na)
		normalizeL2(nh)
		a, h = na, nh
	}
	authority = make(map[string]float64, n)
	hub = make(map[string]float64, n)
	for i, id := range g.IDs {
		authority[id], hub[id] = a[i], h[i]
	}
	return authority, hub
}

func normalizeL2(x []float64) {
	s := 0.0
	for _, v := range x {
		s += v * v
	}
	if s == 0 {
		return
	}
	n := math.Sqrt(s)
	for i := range x {
		x[i] /= n
	}
}

// Scores computes only corpus-level priors. No query text enters any strategy.
func Scores(mem []model.Memory, strategy string) map[string]float64 {
	switch strategy {
	case "pagerank":
		return PageRank(mem, 0.85, 100)
	case "reverse-pagerank":
		return ReversePageRank(mem, 0.85, 100)
	case "undirected-pagerank":
		return UndirectedPageRank(mem, 0.85, 100)
	case "indegree":
		return InDegree(mem)
	case "outdegree":
		return OutDegree(mem)
	case "global-hits-authority", "hits-authority":
		a, _ := HITS(mem, 100)
		return a
	case "global-hits-hub", "hits-hub":
		_, h := HITS(mem, 100)
		return h
	default:
		return nil
	}
}

func Ordered(mem []model.Memory, strategy string) []model.Memory {
	out := append([]model.Memory(nil), mem...)
	switch strategy {
	case "alphabetical":
		sort.SliceStable(out, func(i, j int) bool {
			a, b := strings.ToLower(out[i].Title), strings.ToLower(out[j].Title)
			if a != b {
				return a < b
			}
			return out[i].ID < out[j].ID
		})
		return out
	case "id":
		sort.SliceStable(out, func(i, j int) bool { return out[i].ID < out[j].ID })
		return out
	case "source":
		sort.SliceStable(out, func(i, j int) bool { return out[i].Provenance.SourcePath < out[j].Provenance.SourcePath })
		return out
	case "random-fixed":
		sort.SliceStable(out, func(i, j int) bool {
			a, b := stableRandom(out[i].ID), stableRandom(out[j].ID)
			if a != b {
				return a < b
			}
			return out[i].ID < out[j].ID
		})
		return out
	}

	scores := Scores(mem, strategy)
	if scores == nil {
		panic("rank: unknown strategy " + strategy)
	}
	idx := NewIndex()
	byID := make(map[string]model.Memory, len(mem))
	for _, m := range mem {
		idx.Upsert(m.ID, scores[m.ID])
		byID[m.ID] = m
	}
	if err := idx.Validate(); err != nil {
		panic(err)
	}
	ids := idx.IDs()
	out = out[:0]
	for _, id := range ids {
		out = append(out, byID[id])
	}
	return out
}

func stableRandom(id string) uint64 {
	h := fnv.New64a()
	_, _ = h.Write([]byte("beads-ranked-memory-null-v1\x00" + id))
	return h.Sum64()
}
