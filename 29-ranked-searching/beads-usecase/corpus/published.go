package corpus

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"verifiedskiplist/beads-usecase/model"
)

// PublishedDocs describes the Mintlify-published documentation set without
// conflating site navigation with authored hyperlinks.
type PublishedDocs struct {
	Pages      []string               `json:"pages"`
	Navigation []model.NavigationEdge `json:"navigation_edges"`
	Redirects  map[string]string      `json:"redirects"`
}

type docsConfig struct {
	Redirects []struct {
		Source      string `json:"source"`
		Destination string `json:"destination"`
	} `json:"redirects"`
	Navigation struct {
		Groups []navGroup `json:"groups"`
	} `json:"navigation"`
}

type navGroup struct {
	Group string            `json:"group"`
	Pages []json.RawMessage `json:"pages"`
}

// ReadPublishedDocs parses docs/docs.json and returns the exact published page
// set in navigation order. Nested CLI groups are handled recursively. The
// navigation order is retained only as a separate metadata layer; it is never
// added to Memory.References and therefore never influences citation centrality
// unless an experiment explicitly chooses to do so.
func ReadPublishedDocs(repoRoot string) (PublishedDocs, error) {
	b, err := os.ReadFile(filepath.Join(repoRoot, "docs", "docs.json"))
	if err != nil {
		return PublishedDocs{}, err
	}
	var cfg docsConfig
	if err := json.Unmarshal(b, &cfg); err != nil {
		return PublishedDocs{}, fmt.Errorf("parse docs/docs.json: %w", err)
	}
	var ids []string
	for _, g := range cfg.Navigation.Groups {
		if err := collectNavPages(g.Pages, &ids); err != nil {
			return PublishedDocs{}, err
		}
	}
	seen := map[string]bool{}
	pages := make([]string, 0, len(ids))
	for _, id := range ids {
		p, err := publishedPath(repoRoot, id)
		if err != nil {
			return PublishedDocs{}, err
		}
		if !seen[p] {
			seen[p] = true
			pages = append(pages, p)
		}
	}
	var nav []model.NavigationEdge
	for i := 0; i+1 < len(pages); i++ {
		nav = append(nav,
			model.NavigationEdge{FromPath: pages[i], ToPath: pages[i+1], Kind: "docs-navigation-next"},
			model.NavigationEdge{FromPath: pages[i+1], ToPath: pages[i], Kind: "docs-navigation-prev"},
		)
	}
	redirects := make(map[string]string, len(cfg.Redirects))
	for _, r := range cfg.Redirects {
		if strings.TrimSpace(r.Source) != "" && strings.TrimSpace(r.Destination) != "" {
			redirects[strings.TrimSpace(r.Source)] = strings.TrimSpace(r.Destination)
		}
	}
	return PublishedDocs{Pages: pages, Navigation: nav, Redirects: redirects}, nil
}

func collectNavPages(raw []json.RawMessage, out *[]string) error {
	for _, item := range raw {
		var s string
		if err := json.Unmarshal(item, &s); err == nil {
			*out = append(*out, s)
			continue
		}
		var g navGroup
		if err := json.Unmarshal(item, &g); err != nil {
			return fmt.Errorf("parse nested docs navigation item: %w", err)
		}
		if err := collectNavPages(g.Pages, out); err != nil {
			return err
		}
	}
	return nil
}

func publishedPath(repoRoot, id string) (string, error) {
	id = strings.TrimPrefix(strings.TrimSpace(id), "/")
	candidates := []string{
		filepath.Join("docs", filepath.FromSlash(id)+".md"),
		filepath.Join("docs", filepath.FromSlash(id)+".mdx"),
		filepath.Join("docs", filepath.FromSlash(id)+".markdown"),
	}
	for _, rel := range candidates {
		if st, err := os.Stat(filepath.Join(repoRoot, rel)); err == nil && !st.IsDir() {
			return filepath.ToSlash(rel), nil
		}
	}
	return "", fmt.Errorf("published documentation page %q not found in checkout", id)
}

// IngestPublishedDocs imports exactly the pages published by docs/docs.json.
// Generated CLI pages may be excluded to provide a human-authored/conceptual
// robustness corpus. Hyperlinks are still extracted from each selected source
// file against the complete selected node set.
func IngestPublishedDocs(repoRoot string, includeGeneratedCLI bool) ([]model.Memory, []model.Citation, PublishedDocs, error) {
	return IngestPublishedDocsAt(repoRoot, includeGeneratedCLI, "")
}

// IngestPublishedDocsAt is the reproducible variant used by benchmark corpus
// builds. sourceRef should be the immutable repository commit that the checkout
// represents; it is copied into every imported Memory's provenance.
func IngestPublishedDocsAt(repoRoot string, includeGeneratedCLI bool, sourceRef string) ([]model.Memory, []model.Citation, PublishedDocs, error) {
	pub, err := ReadPublishedDocs(repoRoot)
	if err != nil {
		return nil, nil, PublishedDocs{}, err
	}
	pages := append([]string(nil), pub.Pages...)
	if !includeGeneratedCLI {
		pages = pages[:0]
		for _, p := range pub.Pages {
			if strings.HasPrefix(filepath.ToSlash(p), "docs/cli-reference/") {
				continue
			}
			pages = append(pages, p)
		}
	}
	abs := make([]string, 0, len(pages))
	for _, p := range pages {
		abs = append(abs, filepath.Join(repoRoot, filepath.FromSlash(p)))
	}
	// Selection is deterministic independently of navigation ordering. Keep
	// presentation navigation only when both endpoints are in this scope.
	selected := make(map[string]bool, len(pages))
	for _, p := range pages {
		selected[p] = true
	}
	selectedPub := pub
	selectedPub.Pages = append([]string(nil), pages...)
	selectedPub.Navigation = selectedPub.Navigation[:0]
	for _, e := range pub.Navigation {
		if selected[e.FromPath] && selected[e.ToPath] {
			selectedPub.Navigation = append(selectedPub.Navigation, e)
		}
	}
	sort.Strings(abs)
	mem, cites, err := ingestPaths(abs, repoRoot, IngestOptions{ProjectID: "beads-published-docs", SourceRef: sourceRef, Redirects: pub.Redirects})
	return mem, cites, selectedPub, err
}
