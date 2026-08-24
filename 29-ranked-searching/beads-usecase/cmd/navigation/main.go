package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"

	"verifiedskiplist/beads-usecase/crawl"
	"verifiedskiplist/beads-usecase/model"
)

func main() {
	corpus := flag.String("corpus", "results/pilot-memories.json", "normalized Memory corpus JSON")
	out := flag.String("out", "results/navigation.json", "navigation report JSON")
	trials := flag.Int("trials", 128, "deterministic trials per source-target pair for non-perfect guidance")
	guidance := flag.String("guidance", "0,.25,.5,.75,1", "comma-separated directional-skill probabilities")
	budgets := flag.String("budgets", "3,5,10", "comma-separated body-read budgets")
	flag.Parse()
	var mem []model.Memory
	b, err := os.ReadFile(*corpus)
	must(err)
	must(json.Unmarshal(b, &mem))
	r := crawl.Analyze(mem, parseFloats(*guidance), parseInts(*budgets), *trials)
	b, err = json.MarshalIndent(r, "", "  ")
	must(err)
	must(os.MkdirAll(filepath.Dir(*out), 0755))
	must(os.WriteFile(*out, append(b, '\n'), 0644))
	fmt.Printf("nodes=%d edges=%d\n", r.Nodes, r.Edges)
	minBudget := parseInts(*budgets)[0]
	for _, x := range r.Budgets {
		if x.Budget != minBudget {
			continue
		}
		fmt.Printf("guidance=%.2f budget=%d", x.Guidance, x.Budget)
		for _, c := range x.Correlations {
			if c.Prior == "pagerank" || c.Prior == "reverse-pagerank" || c.Prior == "hits-hub" || c.Prior == "outdegree" {
				fmt.Printf(" %s=%+.3f", c.Prior, c.Spearman)
			}
		}
		fmt.Println()
	}
}

func parseFloats(s string) []float64 {
	var out []float64
	for _, x := range strings.Split(s, ",") {
		v, err := strconv.ParseFloat(strings.TrimSpace(x), 64)
		must(err)
		out = append(out, v)
	}
	return out
}
func parseInts(s string) []int {
	var out []int
	for _, x := range strings.Split(s, ",") {
		v, err := strconv.Atoi(strings.TrimSpace(x))
		must(err)
		out = append(out, v)
	}
	return out
}
func must(err error) {
	if err != nil {
		panic(err)
	}
}
