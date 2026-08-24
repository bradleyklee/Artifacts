package corpus

import (
	"os"
	"path/filepath"
	"testing"
)

func TestPublishedScopesAndNavigationSeparation(t *testing.T) {
	d := t.TempDir()
	mustMkdir := func(p string) {
		t.Helper()
		if err := os.MkdirAll(filepath.Join(d, p), 0755); err != nil {
			t.Fatal(err)
		}
	}
	mustWrite := func(p, s string) {
		t.Helper()
		full := filepath.Join(d, p)
		if err := os.MkdirAll(filepath.Dir(full), 0755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(full, []byte(s), 0644); err != nil {
			t.Fatal(err)
		}
	}
	mustMkdir("docs")
	mustWrite("docs/index.md", "# Home\n\n[Concept](concept.md)\n")
	mustWrite("docs/concept.md", "# Concept\n")
	mustWrite("docs/cli-reference/index.md", "# CLI\n")
	mustWrite("docs/docs.json", `{
  "redirects": [{"source":"/old","destination":"/concept"}],
  "navigation": {"groups":[
    {"group":"Main","pages":["index","concept",{"group":"CLI Reference","pages":["cli-reference/index"]}]}
  ]}
}`)

	all, citesAll, pub, err := IngestPublishedDocsAt(d, true, "abc123")
	if err != nil {
		t.Fatal(err)
	}
	if len(all) != 3 {
		t.Fatalf("all nodes=%d want 3", len(all))
	}
	if len(pub.Pages) != 3 || len(pub.Navigation) != 4 {
		t.Fatalf("published metadata=%#v", pub)
	}
	if len(citesAll) != 1 || len(all[0].References)+len(all[1].References)+len(all[2].References) != 1 {
		t.Fatalf("authored graph was contaminated by navigation: cites=%#v mem=%#v", citesAll, all)
	}
	human, _, _, err := IngestPublishedDocsAt(d, false, "abc123")
	if err != nil {
		t.Fatal(err)
	}
	if len(human) != 2 {
		t.Fatalf("human nodes=%d want 2", len(human))
	}
	for _, m := range human {
		if m.Provenance.SourceRef != "abc123" {
			t.Fatalf("unpinned provenance: %#v", m.Provenance)
		}
		if m.Provenance.SourceType == "generated-cli-doc" {
			t.Fatalf("CLI leaked into human scope: %#v", m)
		}
	}
}
