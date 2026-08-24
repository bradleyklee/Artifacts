package benchmark

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"sort"
	"strings"
	"unicode"

	"verifiedskiplist/beads-usecase/discovery"
	"verifiedskiplist/beads-usecase/model"
	"verifiedskiplist/beads-usecase/rank"
)

const AgentInstructions = "You have a task and a memory search interface. Search returns compact summaries only. You may explicitly recall a memory body and may inspect/follow its outgoing references. Do not assume a referenced body until you recall it."

type Checkpoint struct {
	ID          string   `json:"id"`
	Description string   `json:"description"`
	EvidenceAny []string `json:"evidence_any"`
}

type Task struct {
	ID          string       `json:"id"`
	Difficulty  string       `json:"difficulty"`
	Prompt      string       `json:"prompt"`
	Search      string       `json:"search"`
	Checkpoints []Checkpoint `json:"checkpoints"`
}

type Event struct {
	Step          int      `json:"step"`
	Action        string   `json:"action"`
	MemoryID      string   `json:"memory_id,omitempty"`
	FromID        string   `json:"from_id,omitempty"`
	ToID          string   `json:"to_id,omitempty"`
	Depth         int      `json:"depth,omitempty"`
	GuideScore    int      `json:"guide_score,omitempty"`
	Note          string   `json:"note,omitempty"`
	NewlyResolved []string `json:"newly_resolved,omitempty"`
	Resolved      []string `json:"resolved,omitempty"`
	KnowledgePct  float64  `json:"knowledge_pct"`
}

type Trial struct {
	TaskID           string   `json:"task_id"`
	Ordering         string   `json:"ordering"`
	Policy           string   `json:"policy"`
	Search           string   `json:"search"`
	MatchedIDs       []string `json:"matched_ids"`
	Success          bool     `json:"success"`
	BodiesRecalled   int      `json:"bodies_recalled"`
	EdgesTraversed   int      `json:"edges_traversed"`
	Summaries        int      `json:"summaries_returned"`
	SummaryBytes     int      `json:"summary_bytes"`
	FirstSuccessStep int      `json:"first_success_step,omitempty"`
	NoGainRecalls    int      `json:"no_gain_recalls"`
	Events           []Event  `json:"events"`
}

type Manifest struct {
	CorpusSHA256 string   `json:"corpus_sha256"`
	GraphSHA256  string   `json:"graph_sha256"`
	SpecSHA256   string   `json:"spec_sha256"`
	CorpusNodes  int      `json:"corpus_nodes"`
	GraphEdges   int      `json:"graph_edges"`
	Rankers      []string `json:"rankers"`
	Policies     []string `json:"policies"`
	Matcher      string   `json:"matcher"`
	ReturnMode   string   `json:"return_mode"`
	AgentContext string   `json:"agent_context"`
}

func ValidateTasks(tasks []Task) error {
	if len(tasks) == 0 {
		return fmt.Errorf("benchmark: no tasks")
	}
	seen := map[string]bool{}
	base := strings.ToLower(AgentInstructions)
	for _, t := range tasks {
		if t.ID == "" || seen[t.ID] {
			return fmt.Errorf("benchmark: invalid/duplicate task id %q", t.ID)
		}
		seen[t.ID] = true
		if strings.TrimSpace(t.Search) == "" {
			return fmt.Errorf("benchmark: task %s has empty search", t.ID)
		}
		if len(t.Checkpoints) == 0 {
			return fmt.Errorf("benchmark: task %s has no checkpoints", t.ID)
		}
		initial := strings.ToLower(t.Prompt + "\n" + t.Search + "\n" + base)
		cpSeen := map[string]bool{}
		for _, cp := range t.Checkpoints {
			if cp.ID == "" || cpSeen[cp.ID] {
				return fmt.Errorf("benchmark: task %s invalid checkpoint %q", t.ID, cp.ID)
			}
			cpSeen[cp.ID] = true
			if len(cp.EvidenceAny) == 0 {
				return fmt.Errorf("benchmark: task %s checkpoint %s has no evidence", t.ID, cp.ID)
			}
			for _, e := range cp.EvidenceAny {
				e = strings.TrimSpace(e)
				if e == "" {
					return fmt.Errorf("benchmark: task %s checkpoint %s has empty evidence", t.ID, cp.ID)
				}
				if strings.Contains(initial, strings.ToLower(e)) {
					return fmt.Errorf("benchmark: task %s leaks checkpoint %s evidence %q into initial context", t.ID, cp.ID, e)
				}
			}
		}
	}
	return nil
}

func SearchAll(ordered []model.Memory, query string) ([]model.Summary, []string, int) {
	var summaries []model.Summary
	var ids []string
	bytes := 0
	for _, m := range ordered {
		ok, why := discovery.Match(m, query)
		if !ok {
			continue
		}
		s := model.Summary{ID: m.ID, Title: m.Title, Key: m.Key, Excerpt: excerpt(m.Body, query, 180), Why: why}
		summaries = append(summaries, s)
		ids = append(ids, m.ID)
		bytes += len(s.ID) + len(s.Title) + len(s.Key) + len(s.Excerpt) + len(s.Why)
	}
	return summaries, ids, bytes
}

func Run(task Task, mem []model.Memory, ordering, policy string) Trial {
	ordered := rank.Ordered(mem, ordering)
	summaries, matched, summaryBytes := SearchAll(ordered, task.Search)
	byID := make(map[string]model.Memory, len(mem))
	for _, m := range mem {
		byID[m.ID] = m
	}
	tr := Trial{TaskID: task.ID, Ordering: ordering, Policy: policy, Search: task.Search, MatchedIDs: matched, Summaries: len(summaries), SummaryBytes: summaryBytes}
	resolved := map[string]bool{}
	tr.Events = append(tr.Events, Event{Step: 0, Action: "initial", Note: "task + benchmark search instructions only", KnowledgePct: 0})
	if len(matched) == 0 {
		return tr
	}

	visited := map[string]bool{}
	step := 0
	recall := func(id string, depth int, note string) bool {
		if visited[id] {
			return false
		}
		m, ok := byID[id]
		if !ok {
			return false
		}
		visited[id] = true
		tr.BodiesRecalled++
		step++
		newly := resolve(m.Body, task.Checkpoints, resolved)
		if len(newly) == 0 {
			tr.NoGainRecalls++
		}
		rids := resolvedIDs(task.Checkpoints, resolved)
		pct := 100 * float64(len(rids)) / float64(len(task.Checkpoints))
		tr.Events = append(tr.Events, Event{Step: step, Action: "recall", MemoryID: id, Depth: depth, Note: note, NewlyResolved: newly, Resolved: rids, KnowledgePct: pct})
		if len(rids) == len(task.Checkpoints) && !tr.Success {
			tr.Success = true
			tr.FirstSuccessStep = step
			step++
			tr.Events = append(tr.Events, Event{Step: step, Action: "unblocked", MemoryID: id, Note: "all pre-registered knowledge checkpoints resolved", Resolved: rids, KnowledgePct: 100})
		}
		return true
	}
	follow := func(from, to string, depth, score int) {
		tr.EdgesTraversed++
		step++
		tr.Events = append(tr.Events, Event{Step: step, Action: "follow-reference", FromID: from, ToID: to, Depth: depth, GuideScore: score, Resolved: resolvedIDs(task.Checkpoints, resolved), KnowledgePct: 100 * float64(len(resolved)) / float64(len(task.Checkpoints))})
	}

	switch policy {
	case "flat":
		for _, id := range matched {
			if recall(id, 0, "next lexical match in static order") && tr.Success {
				break
			}
		}
	case "dfs", "guided-dfs", "shallow-guided":
		maxDepth := -1
		guided := policy != "dfs"
		if policy == "shallow-guided" {
			maxDepth = 1
		}
		var walk func(string, int)
		walk = func(id string, depth int) {
			if tr.Success || visited[id] {
				return
			}
			if !recall(id, depth, seedNote(depth)) || tr.Success {
				return
			}
			if maxDepth >= 0 && depth >= maxDepth {
				return
			}
			m := byID[id]
			refs := orderedRefs(m, byID, task, guided)
			for _, r := range refs {
				if tr.Success {
					return
				}
				if visited[r.id] {
					continue
				}
				follow(id, r.id, depth+1, r.score)
				walk(r.id, depth+1)
			}
		}
		for _, id := range matched {
			if tr.Success {
				break
			}
			walk(id, 0)
		}
	case "bfs", "guided-bfs":
		guided := policy == "guided-bfs"
		for _, seed := range matched {
			if tr.Success {
				break
			}
			if visited[seed] {
				continue
			}
			type qitem struct {
				id, from     string
				depth, score int
			}
			q := []qitem{{id: seed}}
			enqueued := map[string]bool{seed: true}
			for len(q) > 0 && !tr.Success {
				x := q[0]
				q = q[1:]
				if x.from != "" {
					follow(x.from, x.id, x.depth, x.score)
				}
				if visited[x.id] {
					continue
				}
				recall(x.id, x.depth, seedNote(x.depth))
				if tr.Success {
					break
				}
				refs := orderedRefs(byID[x.id], byID, task, guided)
				for _, r := range refs {
					if !visited[r.id] && !enqueued[r.id] {
						enqueued[r.id] = true
						q = append(q, qitem{id: r.id, from: x.id, depth: x.depth + 1, score: r.score})
					}
				}
			}
		}
	default:
		panic("benchmark: unknown policy " + policy)
	}
	return tr
}

type refScore struct {
	id    string
	score int
	pos   int
}

func orderedRefs(m model.Memory, byID map[string]model.Memory, task Task, guided bool) []refScore {
	xs := make([]refScore, 0, len(m.References))
	for i, r := range m.References {
		if t, ok := byID[r.TargetID]; ok {
			s := 0
			if guided {
				s = guideScore(task, t)
			}
			xs = append(xs, refScore{id: r.TargetID, score: s, pos: i})
		}
	}
	if guided {
		sort.SliceStable(xs, func(i, j int) bool {
			if xs[i].score != xs[j].score {
				return xs[i].score > xs[j].score
			}
			return xs[i].pos < xs[j].pos
		})
	}
	return xs
}
func guideScore(task Task, m model.Memory) int {
	q := tokenSet(task.Prompt + " " + task.Search)
	s := tokenSet(m.Title + " " + m.Key)
	n := 0
	for t := range q {
		if s[t] {
			n++
		}
	}
	if strings.Contains(strings.ToLower(m.Title), strings.ToLower(task.Search)) {
		n += 3
	}
	if strings.Contains(strings.ToLower(m.Key), strings.ToLower(task.Search)) {
		n += 2
	}
	return n
}
func tokenSet(s string) map[string]bool {
	stop := map[string]bool{"the": true, "and": true, "for": true, "with": true, "from": true, "that": true, "this": true, "into": true, "without": true, "what": true, "how": true, "should": true, "work": true, "agent": true, "beads": true}
	out := map[string]bool{}
	var b strings.Builder
	flush := func() {
		if b.Len() >= 3 {
			t := strings.ToLower(b.String())
			if !stop[t] {
				out[t] = true
			}
		}
		b.Reset()
	}
	for _, r := range s {
		if unicode.IsLetter(r) || unicode.IsDigit(r) || r == '-' {
			b.WriteRune(unicode.ToLower(r))
		} else {
			flush()
		}
	}
	flush()
	return out
}
func resolve(body string, cps []Checkpoint, resolved map[string]bool) []string {
	lo := strings.ToLower(body)
	var newly []string
	for _, cp := range cps {
		if resolved[cp.ID] {
			continue
		}
		for _, e := range cp.EvidenceAny {
			if strings.Contains(lo, strings.ToLower(e)) {
				resolved[cp.ID] = true
				newly = append(newly, cp.ID)
				break
			}
		}
	}
	return newly
}
func resolvedIDs(cps []Checkpoint, m map[string]bool) []string {
	var out []string
	for _, cp := range cps {
		if m[cp.ID] {
			out = append(out, cp.ID)
		}
	}
	return out
}
func seedNote(depth int) string {
	if depth == 0 {
		return "lexical-match seed"
	}
	return "reference-crawl body"
}
func excerpt(body, q string, max int) string {
	body = strings.TrimSpace(body)
	if len(body) <= max {
		return body
	}
	lo := strings.ToLower(body)
	if i := strings.Index(lo, strings.ToLower(q)); i >= 0 {
		start := i - max/3
		if start < 0 {
			start = 0
		}
		end := start + max
		if end > len(body) {
			end = len(body)
			start = end - max
			if start < 0 {
				start = 0
			}
		}
		return body[start:end]
	}
	return body[:max]
}

func SHA256JSON(v any) string {
	b, _ := json.Marshal(v)
	h := sha256.Sum256(b)
	return hex.EncodeToString(h[:])
}
func GraphDigest(mem []model.Memory) (string, int) {
	type edge struct{ A, B string }
	var e []edge
	for _, m := range mem {
		for _, r := range m.References {
			e = append(e, edge{m.ID, r.TargetID})
		}
	}
	sort.Slice(e, func(i, j int) bool {
		if e[i].A != e[j].A {
			return e[i].A < e[j].A
		}
		return e[i].B < e[j].B
	})
	return SHA256JSON(e), len(e)
}
