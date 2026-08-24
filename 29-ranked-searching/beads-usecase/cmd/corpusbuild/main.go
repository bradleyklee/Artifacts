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
	"verifiedskiplist/beads-usecase/model"
)

func main() {
	repo := flag.String("repo", ".", "pinned gastownhall/beads checkout")
	ref := flag.String("source-ref", "", "immutable source commit SHA (required for benchmark artifacts)")
	scope := flag.String("scope", "published-human", "published-human|published-all|docs|repo")
	out := flag.String("out", "results/corpus-v1", "output directory")
	flag.Parse()
	if *ref == "" {
		fatal("-source-ref is required; benchmark corpora must be pinned")
	}

	var (
		mem       []model.Memory
		cites     []model.Citation
		nav       []model.NavigationEdge
		generated bool
		err       error
	)
	switch *scope {
	case "published-human":
		var pub corpus.PublishedDocs
		mem, cites, pub, err = corpus.IngestPublishedDocsAt(*repo, false, *ref)
		nav = pub.Navigation
	case "published-all":
		var pub corpus.PublishedDocs
		mem, cites, pub, err = corpus.IngestPublishedDocsAt(*repo, true, *ref)
		nav = pub.Navigation
		generated = true
	case "docs":
		mem, cites, err = corpus.IngestDocsGraphAt(filepath.Join(*repo, "docs"), *ref)
		generated = true
	case "repo":
		mem, cites, err = corpus.IngestRepoAt(*repo, *ref)
		generated = true
	default:
		fatal("unknown -scope %q", *scope)
	}
	if err != nil {
		fatal("ingest: %v", err)
	}

	stats := graphstats.Analyze(mem, cites)
	manifest := corpus.BuildManifest(mem, cites, nav, *ref, *scope, generated)
	must(os.MkdirAll(*out, 0755))
	writeJSON(filepath.Join(*out, "manifest.json"), manifest)
	writeJSON(filepath.Join(*out, "memories.json"), mem)
	writeJSON(filepath.Join(*out, "citations.json"), cites)
	writeJSON(filepath.Join(*out, "navigation.json"), nav)
	writeJSON(filepath.Join(*out, "graph-stats.json"), stats)
	must(writeCCDF(filepath.Join(*out, "degree-ccdf.csv"), stats))
	fmt.Printf("scope=%s ref=%s nodes=%d edges=%d citations=%d unresolved=%d external=%d isolates=%d max-in=%d max-out=%d\n",
		*scope, *ref, stats.Nodes, stats.UniqueInternalEdges, stats.RawCitationMentions,
		stats.UnresolvedInternalLinks, stats.ExternalLinks, stats.Isolates, stats.MaxIn, stats.MaxOut)
	fmt.Printf("corpus=%s graph=%s citations=%s\n", manifest.CorpusSHA256, manifest.GraphSHA256, manifest.CitationTableSHA256)
}

func writeJSON(path string, v any) {
	b, err := json.MarshalIndent(v, "", "  ")
	must(err)
	must(os.WriteFile(path, append(b, '\n'), 0644))
}
func writeCCDF(path string, s graphstats.Stats) error {
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
	}{{"in", s.InHistogram}, {"out", s.OutHistogram}} {
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
func fatal(f string, a ...any) { fmt.Fprintf(os.Stderr, "corpusbuild: "+f+"\n", a...); os.Exit(2) }
