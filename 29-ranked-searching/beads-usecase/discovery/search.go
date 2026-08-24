package discovery

import (
	"strings"

	"verifiedskiplist/beads-usecase/model"
)

// Match implements the deliberately binary discovery predicate: a
// case-insensitive substring over key, aliases, title, or body. It intentionally
// produces no relevance score; pre-ordering and lexical membership are separate.
func Match(m model.Memory, search string) (bool, string) {
	if search == "" {
		return true, "all"
	}
	needle := strings.ToLower(search)
	if strings.Contains(strings.ToLower(m.Key), needle) {
		return true, "key"
	}
	for _, a := range m.Aliases {
		if strings.Contains(strings.ToLower(a), needle) {
			return true, "alias"
		}
	}
	if strings.Contains(strings.ToLower(m.Title), needle) {
		return true, "title"
	}
	if strings.Contains(strings.ToLower(m.Body), needle) {
		return true, "body"
	}
	return false, ""
}

type Continuation struct {
	Query    string `json:"query"`
	Ordering string `json:"ordering"`
	Cursor   int    `json:"cursor"`
}

type Page struct {
	Summaries    []model.Summary `json:"summaries"`
	Scanned      int             `json:"scanned"`
	Complete     bool            `json:"complete"`
	Continuation *Continuation   `json:"continuation,omitempty"`
}

// SearchPage walks a corpus already placed in its persistent prior order,
// applies Match, and stops only after limit lexical matches or end-of-corpus.
func SearchPage(ordered []model.Memory, query, ordering string, cursor, limit int) Page {
	if cursor < 0 || cursor > len(ordered) {
		panic("discovery: invalid cursor")
	}
	if limit <= 0 {
		panic("discovery: page size must be positive")
	}
	p := Page{}
	i := cursor
	for ; i < len(ordered) && len(p.Summaries) < limit; i++ {
		p.Scanned++
		m := ordered[i]
		ok, why := Match(m, query)
		if !ok {
			continue
		}
		p.Summaries = append(p.Summaries, model.Summary{
			ID: m.ID, Title: m.Title, Key: m.Key,
			Excerpt: excerpt(m.Body, query, 180), Why: why,
		})
	}
	p.Complete = i >= len(ordered)
	if !p.Complete {
		p.Continuation = &Continuation{Query: query, Ordering: ordering, Cursor: i}
	}
	return p
}

func excerpt(body, query string, max int) string {
	body = strings.TrimSpace(body)
	if len(body) <= max {
		return body
	}
	if query != "" {
		lo := strings.ToLower(body)
		if i := strings.Index(lo, strings.ToLower(query)); i >= 0 {
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
	}
	return body[:max]
}
