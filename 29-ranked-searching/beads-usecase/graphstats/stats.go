package graphstats

import (
	"math"
	"sort"

	"verifiedskiplist/beads-usecase/model"
	"verifiedskiplist/beads-usecase/rank"
)

type DegreeCount struct {
	Degree int `json:"degree"`
	Count  int `json:"count"`
}

type NodeDegree struct {
	ID        string `json:"id"`
	Title     string `json:"title"`
	InDegree  int    `json:"in_degree"`
	OutDegree int    `json:"out_degree"`
}

type TailFit struct {
	N     int     `json:"n"`
	XMin  int     `json:"xmin"`
	Alpha float64 `json:"alpha"`
	KS    float64 `json:"ks"`
	Note  string  `json:"note"`
}

type Stats struct {
	Nodes                    int           `json:"nodes"`
	UniqueInternalEdges      int           `json:"unique_internal_edges"`
	RawCitationMentions      int           `json:"raw_citation_mentions"`
	ResolvedInternalMentions int           `json:"resolved_internal_mentions"`
	UnresolvedInternalLinks  int           `json:"unresolved_internal_links"`
	LocalFragmentLinks       int           `json:"local_fragment_links"`
	ExternalLinks            int           `json:"external_links"`
	Isolates                 int           `json:"isolates"`
	ZeroIn                   int           `json:"zero_in_degree"`
	ZeroOut                  int           `json:"zero_out_degree"`
	MaxIn                    int           `json:"max_in_degree"`
	MaxOut                   int           `json:"max_out_degree"`
	MeanIn                   float64       `json:"mean_in_degree"`
	MeanOut                  float64       `json:"mean_out_degree"`
	MedianIn                 float64       `json:"median_in_degree"`
	MedianOut                float64       `json:"median_out_degree"`
	P95In                    int           `json:"p95_in_degree"`
	P95Out                   int           `json:"p95_out_degree"`
	InGini                   float64       `json:"in_degree_gini"`
	OutGini                  float64       `json:"out_degree_gini"`
	Top1InShare              float64       `json:"top1_in_degree_share"`
	Top5InShare              float64       `json:"top5_in_degree_share"`
	Top10InShare             float64       `json:"top10_in_degree_share"`
	Top1OutShare             float64       `json:"top1_out_degree_share"`
	Top5OutShare             float64       `json:"top5_out_degree_share"`
	Top10OutShare            float64       `json:"top10_out_degree_share"`
	WeakComponents           int           `json:"weak_components"`
	LargestWeakComponent     int           `json:"largest_weak_component"`
	StrongComponents         int           `json:"strong_components"`
	LargestStrongComponent   int           `json:"largest_strong_component"`
	ReciprocatedEdges        int           `json:"reciprocated_directed_edges"`
	Reciprocity              float64       `json:"reciprocity"`
	InHistogram              []DegreeCount `json:"in_degree_histogram"`
	OutHistogram             []DegreeCount `json:"out_degree_histogram"`
	InTail                   TailFit       `json:"in_degree_powerlaw_diagnostic"`
	OutTail                  TailFit       `json:"out_degree_powerlaw_diagnostic"`
	TopByIn                  []NodeDegree  `json:"top_by_in_degree"`
	TopByOut                 []NodeDegree  `json:"top_by_out_degree"`
}

func Analyze(mem []model.Memory, citations []model.Citation) Stats {
	g := rank.BuildGraph(mem)
	s := Stats{Nodes: len(mem), RawCitationMentions: len(citations)}
	indeg := make([]int, len(mem))
	outdeg := make([]int, len(mem))
	byID := make(map[string]model.Memory, len(mem))
	for _, m := range mem {
		byID[m.ID] = m
	}
	for i := range mem {
		indeg[i], outdeg[i] = len(g.In[i]), len(g.Out[i])
		s.UniqueInternalEdges += outdeg[i]
		if indeg[i] == 0 {
			s.ZeroIn++
		}
		if outdeg[i] == 0 {
			s.ZeroOut++
		}
		if indeg[i] == 0 && outdeg[i] == 0 {
			s.Isolates++
		}
		if indeg[i] > s.MaxIn {
			s.MaxIn = indeg[i]
		}
		if outdeg[i] > s.MaxOut {
			s.MaxOut = outdeg[i]
		}
	}
	for _, c := range citations {
		switch c.Class {
		case "internal-resolved":
			s.ResolvedInternalMentions++
		case "internal-unresolved":
			s.UnresolvedInternalLinks++
		case "local-fragment":
			s.LocalFragmentLinks++
		case "external":
			s.ExternalLinks++
		default:
			// Backward-compatible fallback for older citation fixtures.
			if c.Internal && c.Resolved {
				s.ResolvedInternalMentions++
			} else if c.Internal {
				s.UnresolvedInternalLinks++
			} else {
				s.ExternalLinks++
			}
		}
	}
	if len(mem) > 0 {
		s.MeanIn = float64(s.UniqueInternalEdges) / float64(len(mem))
		s.MeanOut = s.MeanIn
	}
	s.MedianIn, s.MedianOut = median(indeg), median(outdeg)
	s.P95In, s.P95Out = percentile(indeg, .95), percentile(outdeg, .95)
	s.InGini, s.OutGini = gini(indeg), gini(outdeg)
	s.Top1InShare, s.Top5InShare, s.Top10InShare = topShare(indeg, 1), topShare(indeg, 5), topShare(indeg, 10)
	s.Top1OutShare, s.Top5OutShare, s.Top10OutShare = topShare(outdeg, 1), topShare(outdeg, 5), topShare(outdeg, 10)
	s.WeakComponents, s.LargestWeakComponent = weakComponents(g)
	s.StrongComponents, s.LargestStrongComponent = strongComponents(g)
	s.ReciprocatedEdges = reciprocatedEdges(g)
	if s.UniqueInternalEdges > 0 {
		s.Reciprocity = float64(s.ReciprocatedEdges) / float64(s.UniqueInternalEdges)
	}
	s.InHistogram, s.OutHistogram = histogram(indeg), histogram(outdeg)
	s.InTail, s.OutTail = fitTail(indeg), fitTail(outdeg)

	all := make([]NodeDegree, len(mem))
	for i, id := range g.IDs {
		all[i] = NodeDegree{ID: id, Title: byID[id].Title, InDegree: indeg[i], OutDegree: outdeg[i]}
	}
	s.TopByIn = top(all, func(a, b NodeDegree) bool {
		if a.InDegree != b.InDegree {
			return a.InDegree > b.InDegree
		}
		if a.OutDegree != b.OutDegree {
			return a.OutDegree > b.OutDegree
		}
		return a.ID < b.ID
	})
	s.TopByOut = top(all, func(a, b NodeDegree) bool {
		if a.OutDegree != b.OutDegree {
			return a.OutDegree > b.OutDegree
		}
		if a.InDegree != b.InDegree {
			return a.InDegree > b.InDegree
		}
		return a.ID < b.ID
	})
	return s
}

func top(in []NodeDegree, less func(a, b NodeDegree) bool) []NodeDegree {
	x := append([]NodeDegree(nil), in...)
	sort.Slice(x, func(i, j int) bool { return less(x[i], x[j]) })
	if len(x) > 20 {
		x = x[:20]
	}
	return x
}

func median(xs []int) float64 {
	if len(xs) == 0 {
		return 0
	}
	x := append([]int(nil), xs...)
	sort.Ints(x)
	m := len(x) / 2
	if len(x)%2 == 1 {
		return float64(x[m])
	}
	return float64(x[m-1]+x[m]) / 2
}

func percentile(xs []int, p float64) int {
	if len(xs) == 0 {
		return 0
	}
	x := append([]int(nil), xs...)
	sort.Ints(x)
	if p <= 0 {
		return x[0]
	}
	if p >= 1 {
		return x[len(x)-1]
	}
	i := int(math.Ceil(p*float64(len(x)))) - 1
	if i < 0 {
		i = 0
	}
	if i >= len(x) {
		i = len(x) - 1
	}
	return x[i]
}

func topShare(xs []int, k int) float64 {
	if len(xs) == 0 || k <= 0 {
		return 0
	}
	x := append([]int(nil), xs...)
	sort.Sort(sort.Reverse(sort.IntSlice(x)))
	total := 0
	for _, v := range x {
		total += v
	}
	if total == 0 {
		return 0
	}
	if k > len(x) {
		k = len(x)
	}
	top := 0
	for _, v := range x[:k] {
		top += v
	}
	return float64(top) / float64(total)
}

func weakComponents(g rank.Graph) (count, largest int) {
	seen := make([]bool, len(g.IDs))
	for start := range g.IDs {
		if seen[start] {
			continue
		}
		count++
		size := 0
		q := []int{start}
		seen[start] = true
		for len(q) > 0 {
			v := q[0]
			q = q[1:]
			size++
			for _, n := range g.Out[v] {
				if !seen[n] {
					seen[n] = true
					q = append(q, n)
				}
			}
			for _, n := range g.In[v] {
				if !seen[n] {
					seen[n] = true
					q = append(q, n)
				}
			}
		}
		if size > largest {
			largest = size
		}
	}
	return
}

func strongComponents(g rank.Graph) (count, largest int) {
	n := len(g.IDs)
	seen := make([]bool, n)
	order := make([]int, 0, n)
	var dfs1 func(int)
	dfs1 = func(v int) {
		seen[v] = true
		for _, w := range g.Out[v] {
			if !seen[w] {
				dfs1(w)
			}
		}
		order = append(order, v)
	}
	for v := 0; v < n; v++ {
		if !seen[v] {
			dfs1(v)
		}
	}
	for i := range seen {
		seen[i] = false
	}
	var dfs2 func(int) int
	dfs2 = func(v int) int {
		seen[v] = true
		size := 1
		for _, w := range g.In[v] {
			if !seen[w] {
				size += dfs2(w)
			}
		}
		return size
	}
	for i := len(order) - 1; i >= 0; i-- {
		v := order[i]
		if seen[v] {
			continue
		}
		count++
		size := dfs2(v)
		if size > largest {
			largest = size
		}
	}
	return
}

func reciprocatedEdges(g rank.Graph) int {
	edges := make(map[[2]int]bool)
	for i := range g.Out {
		for _, j := range g.Out[i] {
			edges[[2]int{i, j}] = true
		}
	}
	n := 0
	for e := range edges {
		if edges[[2]int{e[1], e[0]}] {
			n++
		}
	}
	return n
}

func histogram(xs []int) []DegreeCount {
	m := map[int]int{}
	for _, x := range xs {
		m[x]++
	}
	ks := make([]int, 0, len(m))
	for k := range m {
		ks = append(ks, k)
	}
	sort.Ints(ks)
	out := make([]DegreeCount, len(ks))
	for i, k := range ks {
		out[i] = DegreeCount{Degree: k, Count: m[k]}
	}
	return out
}

func gini(xs []int) float64 {
	if len(xs) == 0 {
		return 0
	}
	x := append([]int(nil), xs...)
	sort.Ints(x)
	sum := 0.0
	weighted := 0.0
	for i, v := range x {
		sum += float64(v)
		weighted += float64(i+1) * float64(v)
	}
	if sum == 0 {
		return 0
	}
	n := float64(len(x))
	return 2*weighted/(n*sum) - (n+1)/n
}

// fitTail is a diagnostic, not a claim of a power law. It searches xmin and
// applies the standard continuous-with-discrete-correction MLE
// alpha = 1 + n/sum(log(k/(xmin-0.5))). The chosen xmin minimizes a KS
// distance over the empirical tail. A publication-grade analysis should compare
// discrete power law, lognormal, and exponential alternatives explicitly.
func fitTail(xs []int) TailFit {
	positive := make([]int, 0, len(xs))
	max := 0
	for _, x := range xs {
		if x > 0 {
			positive = append(positive, x)
		}
		if x > max {
			max = x
		}
	}
	best := TailFit{KS: math.Inf(1), Note: "diagnostic continuous-corrected MLE; compare alternatives before claiming power law"}
	if len(positive) < 10 || max < 2 {
		best.KS = 0
		best.Note = "insufficient positive-degree tail for power-law diagnostic"
		return best
	}
	for xmin := 1; xmin <= max; xmin++ {
		var tail []int
		den := 0.0
		for _, x := range positive {
			if x >= xmin {
				tail = append(tail, x)
				den += math.Log(float64(x) / (float64(xmin) - 0.5))
			}
		}
		if len(tail) < 10 || den <= 0 {
			continue
		}
		alpha := 1 + float64(len(tail))/den
		sort.Ints(tail)
		ks := 0.0
		for i, x := range tail {
			emp := float64(i+1) / float64(len(tail))
			modelCDF := 1 - math.Pow(float64(x)/(float64(xmin)-0.5), 1-alpha)
			d := math.Abs(emp - modelCDF)
			if d > ks {
				ks = d
			}
		}
		if ks < best.KS {
			best.N, best.XMin, best.Alpha, best.KS = len(tail), xmin, alpha, ks
		}
	}
	if math.IsInf(best.KS, 1) {
		best.KS = 0
		best.Note = "insufficient tail after xmin search"
	}
	return best
}
