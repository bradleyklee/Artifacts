package main

import (
	"encoding/csv"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"

	"verifiedskiplist/beads-usecase/benchmark"
	"verifiedskiplist/beads-usecase/model"
)

func main() {
	corpusPath := flag.String("corpus", "results/pilot-memories-v2.json", "normalized Memory corpus")
	specPath := flag.String("spec", "benchmark/spec/tasks.json", "frozen benchmark task spec")
	outDir := flag.String("out", "results/benchmark0", "output directory")
	flag.Parse()
	var mem []model.Memory
	readJSON(*corpusPath, &mem)
	var tasks []benchmark.Task
	readJSON(*specPath, &tasks)
	must(benchmark.ValidateTasks(tasks))
	rankers := []string{"alphabetical", "id", "random-fixed", "indegree", "outdegree", "pagerank", "reverse-pagerank", "hits-authority", "hits-hub"}
	policies := []string{"flat", "dfs", "bfs", "shallow-guided", "guided-dfs", "guided-bfs"}
	graphSHA, edges := benchmark.GraphDigest(mem)
	manifest := benchmark.Manifest{CorpusSHA256: benchmark.SHA256JSON(mem), GraphSHA256: graphSHA, SpecSHA256: benchmark.SHA256JSON(tasks), CorpusNodes: len(mem), GraphEdges: edges, Rankers: rankers, Policies: policies, Matcher: "case-insensitive binary substring over key, aliases, title, body", ReturnMode: "all lexical matches; no pagination", AgentContext: benchmark.AgentInstructions}
	must(os.MkdirAll(filepath.Join(*outDir, "trajectories"), 0755))
	writeJSON(filepath.Join(*outDir, "manifest.json"), manifest)
	var trials []benchmark.Trial
	for _, t := range tasks {
		for _, r := range rankers {
			for _, p := range policies {
				tr := benchmark.Run(t, mem, r, p)
				trials = append(trials, tr)
				writeText(filepath.Join(*outDir, "trajectories", safe(t.ID)+"__"+safe(r)+"__"+safe(p)+".txt"), render(t, tr))
			}
		}
	}
	writeJSON(filepath.Join(*outDir, "trials.json"), trials)
	writeSummary(filepath.Join(*outDir, "summary.csv"), trials)
	writeAnswer(filepath.Join(*outDir, "answer.md"), manifest, tasks, trials)
	printAnswer(trials)
}
func render(t benchmark.Task, tr benchmark.Trial) string {
	var b strings.Builder
	fmt.Fprintf(&b, "TASK: %s\nPROMPT: %s\nQUERY: %q\nORDERING: %s\nPOLICY: %s\nMATCHES: %v\n\n", t.ID, t.Prompt, t.Search, tr.Ordering, tr.Policy, tr.MatchedIDs)
	for _, e := range tr.Events {
		fmt.Fprintf(&b, "STEP %d %-16s", e.Step, e.Action)
		if e.MemoryID != "" {
			fmt.Fprintf(&b, " memory=%s", e.MemoryID)
		}
		if e.ToID != "" {
			fmt.Fprintf(&b, " %s -> %s depth=%d guide=%d", e.FromID, e.ToID, e.Depth, e.GuideScore)
		}
		fmt.Fprintf(&b, " knowledge=%0.0f%%", e.KnowledgePct)
		if len(e.NewlyResolved) > 0 {
			fmt.Fprintf(&b, " +%v", e.NewlyResolved)
		}
		if e.Note != "" {
			fmt.Fprintf(&b, " // %s", e.Note)
		}
		b.WriteByte('\n')
	}
	fmt.Fprintf(&b, "\nRESULT success=%v bodies=%d edges=%d summaries=%d summary_bytes=%d no_gain_recalls=%d\n", tr.Success, tr.BodiesRecalled, tr.EdgesTraversed, tr.Summaries, tr.SummaryBytes, tr.NoGainRecalls)
	return b.String()
}
func writeSummary(p string, ts []benchmark.Trial) {
	f, e := os.Create(p)
	must(e)
	defer f.Close()
	w := csv.NewWriter(f)
	defer w.Flush()
	_ = w.Write([]string{"ordering", "policy", "trials", "successes", "mean_bodies_success", "mean_edges_success", "mean_no_gain_recalls_success"})
	type k struct{ r, p string }
	m := map[k][]benchmark.Trial{}
	for _, t := range ts {
		m[k{t.Ordering, t.Policy}] = append(m[k{t.Ordering, t.Policy}], t)
	}
	var ks []k
	for x := range m {
		ks = append(ks, x)
	}
	sort.Slice(ks, func(i, j int) bool {
		if ks[i].p != ks[j].p {
			return ks[i].p < ks[j].p
		}
		return ks[i].r < ks[j].r
	})
	for _, x := range ks {
		a := m[x]
		succ := 0
		sb, se, sn := 0, 0, 0
		for _, t := range a {
			if t.Success {
				succ++
				sb += t.BodiesRecalled
				se += t.EdgesTraversed
				sn += t.NoGainRecalls
			}
		}
		mb, me, mn := 0.0, 0.0, 0.0
		if succ > 0 {
			mb = float64(sb) / float64(succ)
			me = float64(se) / float64(succ)
			mn = float64(sn) / float64(succ)
		}
		_ = w.Write([]string{x.r, x.p, strconv.Itoa(len(a)), strconv.Itoa(succ), fmt.Sprintf("%.3f", mb), fmt.Sprintf("%.3f", me), fmt.Sprintf("%.3f", mn)})
	}
}
func writeAnswer(p string, m benchmark.Manifest, tasks []benchmark.Task, ts []benchmark.Trial) {
	type agg struct{ n, s, b, e int }
	a := map[string]*agg{}
	for _, t := range ts {
		k := t.Policy + "|" + t.Ordering
		if a[k] == nil {
			a[k] = &agg{}
		}
		x := a[k]
		x.n++
		if t.Success {
			x.s++
			x.b += t.BodiesRecalled
			x.e += t.EdgesTraversed
		}
	}
	var b strings.Builder
	fmt.Fprintf(&b, "# Benchmark 0: authority vs navigation prior\n\nCorpus: %d nodes / %d edges. Tasks: %d. No pagination.\n\n", m.CorpusNodes, m.GraphEdges, len(tasks))
	for _, pcy := range m.Policies {
		fmt.Fprintf(&b, "## %s\n\n| ordering | success | mean bodies | mean edges |\n|---|---:|---:|---:|\n", pcy)
		type row struct {
			name   string
			succ   int
			bodies float64
			edges  float64
		}
		var rows []row
		for _, r := range m.Rankers {
			x := a[pcy+"|"+r]
			mb, me := 0.0, 0.0
			if x.s > 0 {
				mb = float64(x.b) / float64(x.s)
				me = float64(x.e) / float64(x.s)
			}
			rows = append(rows, row{r, x.s, mb, me})
		}
		sort.SliceStable(rows, func(i, j int) bool {
			if rows[i].succ != rows[j].succ {
				return rows[i].succ > rows[j].succ
			}
			if rows[i].bodies != rows[j].bodies {
				return rows[i].bodies < rows[j].bodies
			}
			return rows[i].name < rows[j].name
		})
		for _, r := range rows {
			fmt.Fprintf(&b, "| %s | %d/%d | %.2f | %.2f |\n", r.name, r.succ, len(tasks), r.bodies, r.edges)
		}
		b.WriteByte('\n')
	}
	writeText(p, b.String())
}
func printAnswer(ts []benchmark.Trial) {
	fmt.Println("benchmark0 complete")
	for _, p := range []string{"flat", "dfs", "guided-dfs"} {
		fmt.Println("\npolicy", p)
		type a struct{ n, s, b int }
		m := map[string]*a{}
		for _, t := range ts {
			if t.Policy != p {
				continue
			}
			if m[t.Ordering] == nil {
				m[t.Ordering] = &a{}
			}
			x := m[t.Ordering]
			x.n++
			if t.Success {
				x.s++
				x.b += t.BodiesRecalled
			}
		}
		var names []string
		for n := range m {
			names = append(names, n)
		}
		sort.Slice(names, func(i, j int) bool {
			ai, aj := m[names[i]], m[names[j]]
			if ai.s != aj.s {
				return ai.s > aj.s
			}
			bi, bj := 999.0, 999.0
			if ai.s > 0 {
				bi = float64(ai.b) / float64(ai.s)
			}
			if aj.s > 0 {
				bj = float64(aj.b) / float64(aj.s)
			}
			if bi != bj {
				return bi < bj
			}
			return names[i] < names[j]
		})
		for _, n := range names {
			x := m[n]
			mb := 0.0
			if x.s > 0 {
				mb = float64(x.b) / float64(x.s)
			}
			fmt.Printf("  %-18s success=%d/%d mean-bodies=%.2f\n", n, x.s, x.n, mb)
		}
	}
}
func safe(s string) string     { return strings.NewReplacer("/", "_", " ", "_").Replace(s) }
func readJSON(p string, v any) { b, e := os.ReadFile(p); must(e); must(json.Unmarshal(b, v)) }
func writeJSON(p string, v any) {
	b, e := json.MarshalIndent(v, "", "  ")
	must(e)
	must(os.WriteFile(p, append(b, '\n'), 0644))
}
func writeText(p, s string) { must(os.WriteFile(p, []byte(s), 0644)) }
func must(e error) {
	if e != nil {
		panic(e)
	}
}
