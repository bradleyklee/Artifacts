package corpus

import (
	"crypto/sha256"
	"encoding/hex"
	"sort"
	"strings"

	"verifiedskiplist/beads-usecase/model"
)

const CorpusManifestSchema = "beads-memory-corpus-v1"

type Manifest struct {
	SchemaVersion        string `json:"schema_version"`
	SourceRepo           string `json:"source_repo"`
	SourceRef            string `json:"source_ref"`
	Scope                string `json:"scope"`
	Nodes                int    `json:"nodes"`
	UniqueInternalEdges  int    `json:"unique_internal_edges"`
	CitationOccurrences  int    `json:"citation_occurrences"`
	NavigationEdges      int    `json:"navigation_edges"`
	GeneratedCLIIncluded bool   `json:"generated_cli_included"`
	CorpusSHA256         string `json:"corpus_sha256"`
	GraphSHA256          string `json:"graph_sha256"`
	CitationTableSHA256  string `json:"citation_table_sha256"`
}

// BuildManifest hashes content, graph, and raw citation occurrences separately.
// This lets a benchmark prove that rankers saw the same graph and agents saw
// the same bodies even when an application chooses a different presentation.
func BuildManifest(mem []model.Memory, citations []model.Citation, navigation []model.NavigationEdge, sourceRef, scope string, generatedCLI bool) Manifest {
	return Manifest{
		SchemaVersion:        CorpusManifestSchema,
		SourceRepo:           sourceRepo,
		SourceRef:            sourceRef,
		Scope:                scope,
		Nodes:                len(mem),
		UniqueInternalEdges:  uniqueEdgeCount(mem),
		CitationOccurrences:  len(citations),
		NavigationEdges:      len(navigation),
		GeneratedCLIIncluded: generatedCLI,
		CorpusSHA256:         corpusHash(mem),
		GraphSHA256:          graphHash(mem),
		CitationTableSHA256:  citationHash(citations),
	}
}

func uniqueEdgeCount(mem []model.Memory) int {
	n := 0
	for _, m := range mem {
		seen := map[string]bool{}
		for _, r := range m.References {
			if r.TargetID == "" || r.TargetID == m.ID || seen[r.TargetID] {
				continue
			}
			seen[r.TargetID] = true
			n++
		}
	}
	return n
}

func corpusHash(mem []model.Memory) string {
	x := append([]model.Memory(nil), mem...)
	sort.Slice(x, func(i, j int) bool { return x[i].ID < x[j].ID })
	h := sha256.New()
	for _, m := range x {
		writeHashFields(h, m.ID, m.ProjectID, m.Title, m.Key, strings.Join(m.Aliases, "\x1f"), m.Body,
			m.Provenance.SourcePath, m.Provenance.SourceSHA, m.Provenance.SourceRef)
	}
	return hex.EncodeToString(h.Sum(nil))
}

func graphHash(mem []model.Memory) string {
	var edges []string
	for _, m := range mem {
		seen := map[string]bool{}
		for _, r := range m.References {
			if r.TargetID == "" || r.TargetID == m.ID || seen[r.TargetID] {
				continue
			}
			seen[r.TargetID] = true
			edges = append(edges, m.ID+"\x00"+r.TargetID)
		}
	}
	sort.Strings(edges)
	h := sha256.New()
	for _, e := range edges {
		writeHashFields(h, e)
	}
	return hex.EncodeToString(h.Sum(nil))
}

func citationHash(c []model.Citation) string {
	x := append([]model.Citation(nil), c...)
	sort.SliceStable(x, func(i, j int) bool {
		a, b := x[i], x[j]
		if a.SourceID != b.SourceID {
			return a.SourceID < b.SourceID
		}
		if a.SourceLine != b.SourceLine {
			return a.SourceLine < b.SourceLine
		}
		if a.RawTarget != b.RawTarget {
			return a.RawTarget < b.RawTarget
		}
		if a.AnchorText != b.AnchorText {
			return a.AnchorText < b.AnchorText
		}
		return a.Syntax < b.Syntax
	})
	h := sha256.New()
	for _, c := range x {
		writeHashFields(h, c.SourceID, c.SourcePath, c.AnchorText, c.RawTarget, c.TargetID, c.TargetPath,
			c.Fragment, c.Syntax, c.Class, c.ExternalHost)
	}
	return hex.EncodeToString(h.Sum(nil))
}

type hashWriter interface{ Write([]byte) (int, error) }

func writeHashFields(h hashWriter, fields ...string) {
	for _, s := range fields {
		_, _ = h.Write([]byte(s))
		_, _ = h.Write([]byte{0})
	}
	_, _ = h.Write([]byte{0xff})
}
