package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"sort"

	"verifiedskiplist/beads-usecase/corpus"
	"verifiedskiplist/beads-usecase/discovery"
	"verifiedskiplist/beads-usecase/model"
	"verifiedskiplist/beads-usecase/rank"
)

func main() {
	docs := flag.String("docs", "corpus/testdata/docs", "Beads docs root")
	tasksPath := flag.String("tasks", "tasks/tasks.json", "task definitions")
	outPath := flag.String("out", "results/trials.json", "result path")
	corpusPath := flag.String("emit-corpus", "results/memories.json", "normalized corpus path")
	pageSize := flag.Int("page-size", 5, "maximum lexical matches returned per page")
	flag.Parse()

	mem, err := corpus.IngestDocs(*docs)
	must(err)
	writeJSON(*corpusPath, mem)
	var tasks []model.Task
	readJSON(*tasksPath, &tasks)

	strategies := []string{"alphabetical", "id", "random-fixed", "indegree", "outdegree", "pagerank", "reverse-pagerank", "hits-authority", "hits-hub"}
	var results []model.TrialResult
	for _, t := range tasks {
		if t.Search == "" {
			panic("memtrial: deterministic task " + t.ID + " has no binary search predicate")
		}
		for _, st := range strategies {
			ordered := rank.Ordered(mem, st)
			results = append(results, evaluate(t, st, ordered, *pageSize))
		}
	}
	writeJSON(*outPath, results)
	printSummary(tasks, results)
}

func evaluate(t model.Task, strategy string, order []model.Memory, pageSize int) model.TrialResult {
	required := make(map[string]bool, len(t.RequiredAll))
	for _, id := range t.RequiredAll {
		required[id] = true
	}
	found := map[string]bool{}
	var ranks []int
	var matched []string
	cursor, pages, scanned, bytes, matches := 0, 0, 0, 0, 0
	first := 0
	for cursor < len(order) {
		p := discovery.SearchPage(order, t.Search, strategy, cursor, pageSize)
		pages++
		scanned += p.Scanned
		for _, s := range p.Summaries {
			matches++
			matched = append(matched, s.ID)
			bytes += len(s.ID) + len(s.Title) + len(s.Key) + len(s.Excerpt) + len(s.Why)
			if required[s.ID] && !found[s.ID] {
				found[s.ID] = true
				ranks = append(ranks, matches)
				if first == 0 {
					first = matches
				}
			}
		}
		if len(found) == len(required) {
			sort.Ints(ranks)
			return model.TrialResult{TaskID: t.ID, Ordering: strategy, PageSize: pageSize,
				SuccessAtMatch: matches, SuccessPage: pages, FirstEssential: first,
				EssentialMatchRank: ranks, RecordsScanned: scanned, MatchesReturned: matches,
				BytesBeforeDone: bytes, MatchedIDs: matched}
		}
		if p.Complete || p.Continuation == nil {
			break
		}
		cursor = p.Continuation.Cursor
	}
	sort.Ints(ranks)
	return model.TrialResult{TaskID: t.ID, Ordering: strategy, PageSize: pageSize,
		SuccessAtMatch: 0, SuccessPage: 0, FirstEssential: first, EssentialMatchRank: ranks,
		RecordsScanned: scanned, MatchesReturned: matches, BytesBeforeDone: bytes, MatchedIDs: matched}
}

func printSummary(tasks []model.Task, results []model.TrialResult) {
	fmt.Printf("binary lexical pagination trial: %d tasks\n", len(tasks))
	for _, t := range tasks {
		fmt.Printf("\n%s (%s) search=%q\n", t.ID, t.Difficulty, t.Search)
		for _, r := range results {
			if r.TaskID == t.ID {
				fmt.Printf("  %-18s page=%-2d success-match=%-3d first=%-3d scanned=%-3d ranks=%v\n",
					r.Ordering, r.SuccessPage, r.SuccessAtMatch, r.FirstEssential, r.RecordsScanned, r.EssentialMatchRank)
			}
		}
	}
}

func readJSON(p string, v any) { b, e := os.ReadFile(p); must(e); must(json.Unmarshal(b, v)) }
func writeJSON(p string, v any) {
	b, e := json.MarshalIndent(v, "", "  ")
	must(e)
	must(os.MkdirAll(filepath.Dir(p), 0755))
	must(os.WriteFile(p, append(b, '\n'), 0644))
}
func must(e error) {
	if e != nil {
		panic(e)
	}
}
