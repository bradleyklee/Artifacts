package corpus

import (
	"os"
	"path/filepath"
	"testing"

	"verifiedskiplist/beads-usecase/model"
)

func TestFixtureCorpusIngestsAndLinks(t *testing.T) {
	m, err := IngestDocs("testdata/docs")
	if err != nil {
		t.Fatal(err)
	}
	if len(m) < 15 {
		t.Fatalf("fixture too small: %d", len(m))
	}
	seen := map[string]bool{}
	edges := 0
	for _, x := range m {
		if seen[x.ID] {
			t.Fatalf("duplicate %s", x.ID)
		}
		seen[x.ID] = true
		edges += len(x.References)
		if x.Title == "" || x.Body == "" {
			t.Fatalf("empty imported memory %#v", x)
		}
	}
	if edges < 20 {
		t.Fatalf("fixture graph too sparse: %d edges", edges)
	}
}

func TestReferencesPreserveAuthoredHyperlinkStructure(t *testing.T) {
	known := map[string]string{
		"docs/a": "mem:repo/docs/a",
		"docs/b": "mem:repo/docs/b",
	}
	src := "# A\n\n" +
		"Inline [go to B](b.md#details).\n" +
		"Reference [the B page][bref].\n" +
		"Shortcut [bref].\n" +
		"Local [section](#local).\n" +
		"External [example](https://example.com/x?q=1#z).\n" +
		"Email [us](mailto:ops@example.com).\n" +
		"Image ![not an edge](b.md).\n" +
		"Code `[not a link](b.md)`.\n\n" +
		"```md\n[fenced](b.md)\n```\n\n" +
		"[bref]: b.md\n"
	refs, cites := references("docs/a.md", src, known, nil)
	if len(refs) != 1 || refs[0].TargetID != "mem:repo/docs/b" {
		t.Fatalf("unique graph refs = %#v, want exactly B", refs)
	}
	if len(cites) != 6 {
		for _, c := range cites {
			t.Logf("citation: %#v", c)
		}
		t.Fatalf("citation occurrences=%d, want 6", len(cites))
	}
	var inline, refUse, shortcut, local, external, mail *model.Citation
	for i := range cites {
		c := &cites[i]
		switch c.AnchorText {
		case "go to B":
			inline = c
		case "the B page":
			refUse = c
		case "bref":
			shortcut = c
		case "section":
			local = c
		case "example":
			external = c
		case "us":
			mail = c
		}
	}
	if inline == nil || inline.TargetID != "mem:repo/docs/b" || inline.Fragment != "#details" || inline.Syntax != "markdown-inline" || inline.Class != "internal-resolved" {
		t.Fatalf("bad inline citation: %#v", inline)
	}
	if refUse == nil || shortcut == nil || refUse.Syntax != "markdown-reference" || shortcut.Syntax != "markdown-reference" {
		t.Fatalf("reference uses not preserved: %#v %#v", refUse, shortcut)
	}
	if local == nil || local.Class != "local-fragment" || local.Fragment != "#local" {
		t.Fatalf("bad local fragment: %#v", local)
	}
	if external == nil || external.Class != "external" || external.ExternalHost != "example.com" || external.Fragment != "#z" {
		t.Fatalf("bad external citation: %#v", external)
	}
	if mail == nil || mail.Class != "external" {
		t.Fatalf("bad mail citation: %#v", mail)
	}
	for _, c := range cites {
		if c.AnchorText == "not an edge" || c.AnchorText == "not a link" || c.AnchorText == "fenced" {
			t.Fatalf("non-authored navigation edge leaked from image/code: %#v", c)
		}
	}
}

func TestReferenceDefinitionAloneIsNotCitation(t *testing.T) {
	known := map[string]string{"docs/a": "mem:repo/docs/a", "docs/b": "mem:repo/docs/b"}
	refs, cites := references("docs/a.md", "[b]: b.md\n", known, nil)
	if len(refs) != 0 || len(cites) != 0 {
		t.Fatalf("definition created citation: refs=%#v cites=%#v", refs, cites)
	}
}

func TestPinnedSourceRefInProvenance(t *testing.T) {
	d := t.TempDir()
	if err := os.MkdirAll(filepath.Join(d, "docs"), 0755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(d, "docs", "a.md"), []byte("# A\n"), 0644); err != nil {
		t.Fatal(err)
	}
	m, _, err := ingestPaths([]string{filepath.Join(d, "docs", "a.md")}, d, IngestOptions{ProjectID: "x", SourceRef: "deadbeef"})
	if err != nil {
		t.Fatal(err)
	}
	if got := m[0].Provenance.SourceRef; got != "deadbeef" {
		t.Fatalf("source ref=%q", got)
	}
	want := "https://github.com/gastownhall/beads/blob/deadbeef/docs/a.md"
	if got := m[0].Provenance.SourceURL; got != want {
		t.Fatalf("source URL=%q want %q", got, want)
	}
}
