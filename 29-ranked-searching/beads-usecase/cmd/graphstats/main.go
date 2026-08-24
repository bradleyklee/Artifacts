package main

import (
	"encoding/csv"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strconv"

	"verifiedskiplist/beads-usecase/corpus"
	"verifiedskiplist/beads-usecase/graphstats"
)

func main() {
	root := flag.String("repo", ".", "Beads repository checkout (all Markdown is ingested)")
	out := flag.String("out", "results/graph-stats.json", "JSON statistics output")
	ccdf := flag.String("ccdf", "results/degree-ccdf.csv", "degree CCDF output")
	memOut := flag.String("memories", "results/repo-memories.json", "canonical Memory corpus output")
	citeOut := flag.String("citations", "results/citations.json", "raw citation table output")
	flag.Parse()

	mem, cites, err := corpus.IngestRepo(*root)
	must(err)
	stats := graphstats.Analyze(mem, cites)
	writeJSON(*memOut, mem)
	writeJSON(*citeOut, cites)
	writeJSON(*out, stats)
	must(writeCCDF(*ccdf, stats))
	fmt.Printf("nodes=%d edges=%d raw-citations=%d isolates=%d max-in=%d max-out=%d in-gini=%.3f out-gini=%.3f\n",
		stats.Nodes, stats.UniqueInternalEdges, stats.RawCitationMentions, stats.Isolates,
		stats.MaxIn, stats.MaxOut, stats.InGini, stats.OutGini)
	fmt.Printf("in-tail: n=%d xmin=%d alpha=%.3f KS=%.3f (%s)\n",
		stats.InTail.N, stats.InTail.XMin, stats.InTail.Alpha, stats.InTail.KS, stats.InTail.Note)
}

func writeJSON(path string, v any) {
	b, err := json.MarshalIndent(v, "", "  ")
	must(err)
	must(os.MkdirAll(filepath.Dir(path), 0755))
	must(os.WriteFile(path, append(b, '\n'), 0644))
}

func writeCCDF(path string, s graphstats.Stats) error {
	if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil {
		return err
	}
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	w := csv.NewWriter(f)
	defer w.Flush()
	if err := w.Write([]string{"direction", "degree", "count", "ccdf_count"}); err != nil {
		return err
	}
	for _, item := range []struct {
		name string
		h    []graphstats.DegreeCount
	}{
		{"in", s.InHistogram}, {"out", s.OutHistogram},
	} {
		total := 0
		for _, d := range item.h {
			total += d.Count
		}
		remaining := total
		for _, d := range item.h {
			if err := w.Write([]string{item.name, strconv.Itoa(d.Degree), strconv.Itoa(d.Count), strconv.Itoa(remaining)}); err != nil {
				return err
			}
			remaining -= d.Count
		}
	}
	return w.Error()
}

func must(err error) {
	if err != nil {
		panic(err)
	}
}
