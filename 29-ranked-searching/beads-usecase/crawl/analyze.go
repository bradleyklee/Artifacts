// Package crawl measures how useful a Memory's outgoing-reference position is
// as a navigation entry point.  It is deliberately independent of discovery:
// no task text or lexical score enters these structural measurements.
package crawl

import (
	"hash/fnv"
	"math"
	"sort"

	"verifiedskiplist/beads-usecase/model"
	"verifiedskiplist/beads-usecase/rank"
)

type Node struct {
	ID            string  `json:"id"`
	Title         string  `json:"title"`
	InDegree      int     `json:"in_degree"`
	OutDegree     int     `json:"out_degree"`
	Reachable     int     `json:"reachable_nodes"`
	Reachability  float64 `json:"reachability_fraction"`
	MeanDistance  float64 `json:"mean_shortest_distance,omitempty"`
	PageRank      float64 `json:"pagerank"`
	ReversePR     float64 `json:"reverse_pagerank"`
	HITSHub       float64 `json:"hits_hub"`
	HITSAuthority float64 `json:"hits_authority"`
}

type Correlation struct {
	Prior    string  `json:"prior"`
	Metric   string  `json:"metric"`
	Spearman float64 `json:"spearman"`
}

type BudgetResult struct {
	Guidance      float64       `json:"guidance"`
	Budget        int           `json:"body_read_budget"`
	TrialsPerPair int           `json:"trials_per_pair"`
	Correlations  []Correlation `json:"correlations"`
}

type DegreeBand struct {
	OutDegree        int     `json:"out_degree"`
	Nodes            int     `json:"nodes"`
	MeanReachability float64 `json:"mean_reachability"`
	UnguidedSuccess3 float64 `json:"unguided_success_budget_3"`
	GuidedSuccess3   float64 `json:"guided_success_budget_3"`
}

type Report struct {
	Nodes       int            `json:"nodes"`
	Edges       int            `json:"edges"`
	Structural  []Correlation  `json:"structural_correlations"`
	NodeMetrics []Node         `json:"node_metrics"`
	Budgets     []BudgetResult `json:"budget_results"`
	DegreeBands []DegreeBand   `json:"degree_bands"`
	Note        string         `json:"note"`
}

// Analyze runs an all-pairs structural navigation census. Guidance is an
// abstract directional-skill parameter, not an LLM score: at each recalled
// node, with probability guidance the crawler explores the outgoing edge lying
// on a shortest path to the target first; otherwise it explores outgoing edges
// in a deterministic pseudo-random order.  This brackets the cost of branching
// between an unguided crawler and one that knows where to dive.
func Analyze(mem []model.Memory, guidances []float64, budgets []int, trials int) Report {
	g := rank.BuildGraph(mem)
	n := len(g.IDs)
	if trials < 1 {
		trials = 1
	}
	for _, p := range guidances {
		if p < 0 || p > 1 {
			panic("crawl: guidance outside [0,1]")
		}
	}
	byID := make(map[string]model.Memory, n)
	for _, m := range mem {
		byID[m.ID] = m
	}

	pr := rank.PageRank(mem, .85, 100)
	rpr := rank.ReversePageRank(mem, .85, 100)
	auth, hub := rank.HITS(mem, 100)

	// dist[target][source] = shortest directed distance source -> target.
	dist := make([][]int, n)
	for t := 0; t < n; t++ {
		dist[t] = reverseDistances(g, t)
	}

	nodes := make([]Node, n)
	edges := 0
	for s := 0; s < n; s++ {
		edges += len(g.Out[s])
		reach, sumD := 0, 0
		for t := 0; t < n; t++ {
			if s != t && dist[t][s] >= 0 {
				reach++
				sumD += dist[t][s]
			}
		}
		mean := 0.0
		if reach > 0 {
			mean = float64(sumD) / float64(reach)
		}
		den := n - 1
		rf := 0.0
		if den > 0 {
			rf = float64(reach) / float64(den)
		}
		id := g.IDs[s]
		nodes[s] = Node{
			ID: id, Title: byID[id].Title, InDegree: len(g.In[s]), OutDegree: len(g.Out[s]),
			Reachable: reach, Reachability: rf, MeanDistance: mean,
			PageRank: pr[id], ReversePR: rpr[id], HITSHub: hub[id], HITSAuthority: auth[id],
		}
	}

	var out []BudgetResult
	// Per-node success is the probability of reaching a uniformly selected
	// other node within the body-read budget; unreachable targets count as
	// failures. This combines navigation coverage and branch-search cost.
	type key struct {
		p float64
		b int
	}
	successBy := make(map[key][]float64)
	for _, p := range guidances {
		perBudget := make(map[int][]float64, len(budgets))
		for _, b := range budgets {
			perBudget[b] = make([]float64, n)
		}
		for s := 0; s < n; s++ {
			for t := 0; t < n; t++ {
				if s == t {
					continue
				}
				reps := trials
				if p == 1 {
					reps = 1
				}
				for r := 0; r < reps; r++ {
					seed := pairSeed(g.IDs[s], g.IDs[t], r)
					cost := crawlCost(g, dist[t], s, t, p, seed)
					for _, b := range budgets {
						if cost > 0 && cost <= b {
							perBudget[b][s] += 1 / float64(reps)
						}
					}
				}
			}
			if n > 1 {
				for _, b := range budgets {
					perBudget[b][s] /= float64(n - 1)
				}
			}
		}
		for _, b := range budgets {
			succ := perBudget[b]
			successBy[key{p, b}] = append([]float64(nil), succ...)
			out = append(out, BudgetResult{Guidance: p, Budget: b, TrialsPerPair: trials, Correlations: []Correlation{
				{Prior: "pagerank", Metric: "success_probability", Spearman: spearman(nodeValues(nodes, func(x Node) float64 { return x.PageRank }), succ)},
				{Prior: "reverse-pagerank", Metric: "success_probability", Spearman: spearman(nodeValues(nodes, func(x Node) float64 { return x.ReversePR }), succ)},
				{Prior: "hits-hub", Metric: "success_probability", Spearman: spearman(nodeValues(nodes, func(x Node) float64 { return x.HITSHub }), succ)},
				{Prior: "outdegree", Metric: "success_probability", Spearman: spearman(nodeValues(nodes, func(x Node) float64 { return float64(x.OutDegree) }), succ)},
				{Prior: "indegree", Metric: "success_probability", Spearman: spearman(nodeValues(nodes, func(x Node) float64 { return float64(x.InDegree) }), succ)},
			}})
		}
	}

	bands := degreeBands(nodes, successBy[key{0, 3}], successBy[key{1, 3}])
	reach := nodeValues(nodes, func(x Node) float64 { return x.Reachability })
	structural := []Correlation{
		{Prior: "pagerank", Metric: "downstream_reachability", Spearman: spearman(nodeValues(nodes, func(x Node) float64 { return x.PageRank }), reach)},
		{Prior: "reverse-pagerank", Metric: "downstream_reachability", Spearman: spearman(nodeValues(nodes, func(x Node) float64 { return x.ReversePR }), reach)},
		{Prior: "hits-hub", Metric: "downstream_reachability", Spearman: spearman(nodeValues(nodes, func(x Node) float64 { return x.HITSHub }), reach)},
		{Prior: "outdegree", Metric: "downstream_reachability", Spearman: spearman(nodeValues(nodes, func(x Node) float64 { return float64(x.OutDegree) }), reach)},
		{Prior: "indegree", Metric: "downstream_reachability", Spearman: spearman(nodeValues(nodes, func(x Node) float64 { return float64(x.InDegree) }), reach)},
	}
	return Report{
		Nodes: n, Edges: edges, Structural: structural, NodeMetrics: nodes, Budgets: out, DegreeBands: bands,
		Note: "guidance is an abstract shortest-path edge-choice skill parameter; it brackets branching cost and is not presented as an LLM measurement",
	}
}

func reverseDistances(g rank.Graph, target int) []int {
	d := make([]int, len(g.IDs))
	for i := range d {
		d[i] = -1
	}
	d[target] = 0
	q := []int{target}
	for len(q) > 0 {
		v := q[0]
		q = q[1:]
		for _, src := range g.In[v] {
			if d[src] < 0 {
				d[src] = d[v] + 1
				q = append(q, src)
			}
		}
	}
	return d
}

func crawlCost(g rank.Graph, distToTarget []int, source, target int, guidance float64, seed uint64) int {
	rng := xorshift{state: seed | 1}
	visited := make([]bool, len(g.IDs))
	stack := []int{source}
	reads := 0
	for len(stack) > 0 {
		v := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		if visited[v] {
			continue
		}
		visited[v] = true
		reads++
		if v == target {
			return reads
		}
		nbr := make([]int, 0, len(g.Out[v]))
		for _, u := range g.Out[v] {
			if !visited[u] {
				nbr = append(nbr, u)
			}
		}
		shuffle(nbr, &rng)
		if len(nbr) > 1 && rng.float64() < guidance {
			// Stable sort after shuffling gives random tie-breaking while always
			// preferring an edge on the best currently visible route.
			sort.SliceStable(nbr, func(i, j int) bool {
				di, dj := distToTarget[nbr[i]], distToTarget[nbr[j]]
				if di < 0 {
					di = math.MaxInt
				}
				if dj < 0 {
					dj = math.MaxInt
				}
				return di < dj
			})
		}
		// DFS visits the first neighbour first, hence reverse push order.
		for i := len(nbr) - 1; i >= 0; i-- {
			stack = append(stack, nbr[i])
		}
	}
	return -1
}

type xorshift struct{ state uint64 }

func (x *xorshift) next() uint64 {
	x.state ^= x.state << 13
	x.state ^= x.state >> 7
	x.state ^= x.state << 17
	return x.state
}
func (x *xorshift) float64() float64 { return float64(x.next()>>11) / float64(uint64(1)<<53) }
func shuffle(x []int, r *xorshift) {
	for i := len(x) - 1; i > 0; i-- {
		j := int(r.next() % uint64(i+1))
		x[i], x[j] = x[j], x[i]
	}
}

func pairSeed(a, b string, rep int) uint64 {
	h := fnv.New64a()
	_, _ = h.Write([]byte(a))
	_, _ = h.Write([]byte{0})
	_, _ = h.Write([]byte(b))
	_, _ = h.Write([]byte{0})
	// Guidance variants deliberately share the same seed so their random
	// branch ordering is paired; only the probability of using directional
	// information changes between variants.
	_, _ = h.Write([]byte{byte(rep), byte(rep >> 8), byte(rep >> 16), byte(rep >> 24)})
	return h.Sum64()
}

func nodeValues(xs []Node, f func(Node) float64) []float64 {
	out := make([]float64, len(xs))
	for i, x := range xs {
		out[i] = f(x)
	}
	return out
}

func spearman(a, b []float64) float64 {
	if len(a) != len(b) || len(a) < 2 {
		return 0
	}
	ra, rb := ranks(a), ranks(b)
	ma, mb := mean(ra), mean(rb)
	num, da, db := 0.0, 0.0, 0.0
	for i := range ra {
		x, y := ra[i]-ma, rb[i]-mb
		num += x * y
		da += x * x
		db += y * y
	}
	if da == 0 || db == 0 {
		return 0
	}
	return num / math.Sqrt(da*db)
}

func ranks(x []float64) []float64 {
	idx := make([]int, len(x))
	for i := range idx {
		idx[i] = i
	}
	sort.SliceStable(idx, func(i, j int) bool { return x[idx[i]] < x[idx[j]] })
	r := make([]float64, len(x))
	for i := 0; i < len(idx); {
		j := i + 1
		for j < len(idx) && almostEqual(x[idx[i]], x[idx[j]]) {
			j++
		}
		avg := (float64(i+1) + float64(j)) / 2
		for k := i; k < j; k++ {
			r[idx[k]] = avg
		}
		i = j
	}
	return r
}
func almostEqual(a, b float64) bool {
	return math.Abs(a-b) <= 1e-14*math.Max(1, math.Max(math.Abs(a), math.Abs(b)))
}
func mean(x []float64) float64 {
	s := 0.0
	for _, v := range x {
		s += v
	}
	if len(x) == 0 {
		return 0
	}
	return s / float64(len(x))
}

func degreeBands(nodes []Node, unguided, guided []float64) []DegreeBand {
	type acc struct {
		n           int
		reach, u, g float64
	}
	m := map[int]*acc{}
	for i, n := range nodes {
		a := m[n.OutDegree]
		if a == nil {
			a = &acc{}
			m[n.OutDegree] = a
		}
		a.n++
		a.reach += n.Reachability
		if i < len(unguided) {
			a.u += unguided[i]
		}
		if i < len(guided) {
			a.g += guided[i]
		}
	}
	ks := make([]int, 0, len(m))
	for k := range m {
		ks = append(ks, k)
	}
	sort.Ints(ks)
	out := make([]DegreeBand, 0, len(ks))
	for _, k := range ks {
		a := m[k]
		d := float64(a.n)
		out = append(out, DegreeBand{OutDegree: k, Nodes: a.n, MeanReachability: a.reach / d, UnguidedSuccess3: a.u / d, GuidedSuccess3: a.g / d})
	}
	return out
}
