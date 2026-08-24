package corpus

import (
	"testing"
	"verifiedskiplist/beads-usecase/model"
)

func TestManifestHashesIgnoreInputOrderButNotGraph(t *testing.T) {
	a := model.Memory{ID: "a", Title: "A", Body: "alpha", References: []model.Reference{{TargetID: "b", Kind: "imported-doc-link"}}}
	b := model.Memory{ID: "b", Title: "B", Body: "beta"}
	m1 := BuildManifest([]model.Memory{a, b}, nil, nil, "deadbeef", "test", false)
	m2 := BuildManifest([]model.Memory{b, a}, nil, nil, "deadbeef", "test", false)
	if m1.CorpusSHA256 != m2.CorpusSHA256 || m1.GraphSHA256 != m2.GraphSHA256 {
		t.Fatal("hashes depend on input order")
	}
	a.References = nil
	m3 := BuildManifest([]model.Memory{a, b}, nil, nil, "deadbeef", "test", false)
	if m1.GraphSHA256 == m3.GraphSHA256 {
		t.Fatal("graph hash ignored edge change")
	}
	if m1.CorpusSHA256 != m3.CorpusSHA256 {
		t.Fatal("corpus hash should hash bodies/identity separately from graph")
	}
}
