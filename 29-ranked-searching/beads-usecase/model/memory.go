package model

import "time"

// Memory is the PoC projection of the durable Memory Bead fields in #5877.
// Shared-history identifiers and attribution are represented as source metadata
// because this corpus is imported documentation, not a live Beads provider.
type Memory struct {
	ID          string      `json:"id"`
	ProjectID   string      `json:"project_id"`
	Title       string      `json:"title"`
	Body        string      `json:"body"`
	Key         string      `json:"key,omitempty"`
	Aliases     []string    `json:"aliases,omitempty"`
	ArchiveFrom *time.Time  `json:"archive_from,omitempty"`
	References  []Reference `json:"references,omitempty"`
	Provenance  Provenance  `json:"stored_provenance"`
}

type Reference struct {
	TargetID string `json:"target_id"`
	Kind     string `json:"kind"` // imported-doc-link, navigation, etc.
}

type Provenance struct {
	Kind       string `json:"kind"`
	SourcePath string `json:"source_path"`
	SourceURL  string `json:"source_url,omitempty"`
	SourceSHA  string `json:"source_sha,omitempty"`
	SourceType string `json:"source_type,omitempty"`
	SourceRepo string `json:"source_repo,omitempty"`
	SourceRef  string `json:"source_ref,omitempty"`
}

// Citation is the lossless edge-side record produced during ingestion.
//
// Every authored hyperlink occurrence is retained, not merely the unique graph
// edge. Resolved internal citations become Memory References; unresolved and
// external links remain here so graph statistics and audits do not silently
// discard evidence. AnchorText and SourceLine are especially important for the
// crawling benchmark: an agent may use visible link metadata to choose a branch
// without having seen the target body.
type Citation struct {
	SourceID     string `json:"source_id"`
	SourcePath   string `json:"source_path"`
	SourceLine   int    `json:"source_line,omitempty"`
	AnchorText   string `json:"anchor_text,omitempty"`
	RawTarget    string `json:"raw_target"`
	TargetID     string `json:"target_id,omitempty"`
	TargetPath   string `json:"target_path,omitempty"`
	Fragment     string `json:"fragment,omitempty"`
	Syntax       string `json:"syntax"` // markdown-inline, markdown-reference, html
	Class        string `json:"class"`  // internal-resolved, internal-unresolved, external, local-fragment
	Internal     bool   `json:"internal"`
	Resolved     bool   `json:"resolved"`
	ExternalHost string `json:"external_host,omitempty"`
}

// NavigationEdge is deliberately separate from Citation. Mintlify navigation
// is useful metadata, but treating the repeated site sidebar as authored
// citations would manufacture a dense fake graph and corrupt PageRank/HITS.
type NavigationEdge struct {
	FromPath string `json:"from_path"`
	ToPath   string `json:"to_path"`
	Kind     string `json:"kind"` // docs-navigation-next, docs-navigation-prev
}

// Summary is the compact discovery record used by the experiment. It does not
// contain Body, preserving #5877's discovery/recall separation.
type Summary struct {
	ID      string  `json:"id"`
	Title   string  `json:"title"`
	Key     string  `json:"key,omitempty"`
	Excerpt string  `json:"excerpt"`
	Rank    float64 `json:"rank,omitempty"`
	Why     string  `json:"match_provenance,omitempty"`
}
